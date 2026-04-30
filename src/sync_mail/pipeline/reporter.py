# src/sync_mail/pipeline/reporter.py

import os
import socket
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from sync_mail.observability import event_bus, Event, EventType, logger

@dataclass
class JobReportData:
    job_name: str
    mode: str  # "DRY_RUN" or "REAL_SYNC"
    status: str = "UNKNOWN"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source_host: str = ""
    source_db: str = ""
    target_host: str = ""
    target_db: str = ""
    source_table: str = ""
    target_table: str = ""
    mapping_path: str = ""
    total_rows_est: int = 0
    rows_processed: int = 0
    rows_committed: int = 0
    batches_committed: int = 0
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    version: str = "0.1.0"
    hostname: str = field(default_factory=socket.gethostname)

    @property
    def duration_str(self) -> str:
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            seconds = int(diff.total_seconds())
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return "Unknown"

    @property
    def success_rate(self) -> float:
        if self.mode == "DRY_RUN":
            return 100.0 if not any(a["severity"] == "BLOCKER" for a in self.anomalies) else 0.0
        if self.rows_processed > 0:
            return (self.rows_committed / self.rows_processed) * 100
        return 0.0

class HTMLReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.active_jobs: Dict[str, JobReportData] = {}
        self.completed_jobs: List[JobReportData] = []
        self.batch_context: Optional[Dict[str, Any]] = None
        self._ensure_output_dir()
        self._subscribe()

    def _ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create reports directory: {e}")

    def _subscribe(self):
        event_bus.subscribe(self.handle_event)

    def handle_event(self, event: Event):
        try:
            if event.type == EventType.MULTI_JOB_PROGRESS:
                self.batch_context = event.payload
                if event.payload.get("is_done"):
                    if self.completed_jobs:
                        self._save_batch_report(self.completed_jobs)
                        self.completed_jobs = []
                    self.batch_context = None
            
            elif event.type == EventType.JOB_STARTED:
                payload = event.payload
                job_name = payload["job_name"]
                self.active_jobs[job_name] = JobReportData(
                    job_name=job_name,
                    mode="REAL_SYNC",
                    start_time=datetime.now(),
                    source_host=payload.get("source_host", ""),
                    source_db=payload.get("source_db", ""),
                    target_host=payload.get("target_host", ""),
                    target_db=payload.get("target_db", ""),
                    source_table=payload.get("source_table", ""),
                    target_table=payload.get("target_table", ""),
                    mapping_path=payload.get("mapping_path", ""),
                    total_rows_est=payload.get("total_rows_est", 0)
                )

            elif event.type == EventType.BATCH_COMMITTED:
                job_name = event.payload["job_name"]
                if job_name in self.active_jobs:
                    self.active_jobs[job_name].rows_committed += event.payload.get("rows", 0)
                    self.active_jobs[job_name].rows_processed += event.payload.get("rows", 0)
                    self.active_jobs[job_name].batches_committed += 1

            elif event.type == EventType.JOB_COMPLETED:
                job_name = event.payload["job_name"]
                if job_name in self.active_jobs:
                    data = self.active_jobs.pop(job_name)
                    data.status = "SUCCESS"
                    data.end_time = datetime.now()
                    if self.batch_context:
                        self.completed_jobs.append(data)
                    else:
                        self._save_report(data)

            elif event.type == EventType.JOB_ABORTED:
                job_name = event.payload["job_name"]
                if job_name in self.active_jobs:
                    data = self.active_jobs.pop(job_name)
                    data.status = "ABORTED"
                    data.error_message = event.payload.get("reason")
                    data.end_time = datetime.now()
                    if self.batch_context:
                        self.completed_jobs.append(data)
                        # If batch aborted, we might want to trigger report immediately if it's the last job
                        # But MultiJobProgress might not send is_done. 
                        # For now, let's trigger single report if batch context is not 'completed'
                    else:
                        self._save_report(data)

            elif event.type == EventType.DRY_RUN_COMPLETED:
                report_dict = event.payload["report"]
                data = JobReportData(
                    job_name=report_dict["job_name"],
                    mode="DRY_RUN",
                    status=report_dict["status"],
                    start_time=datetime.fromisoformat(report_dict["start_time"]) if report_dict.get("start_time") else datetime.now(),
                    end_time=datetime.fromisoformat(report_dict["end_time"]) if report_dict.get("end_time") else datetime.now(),
                    source_host=report_dict.get("source_host", ""),
                    source_db=report_dict.get("source_db", ""),
                    target_host=report_dict.get("target_host", ""),
                    target_db=report_dict.get("target_db", ""),
                    source_table=report_dict.get("source", ""),
                    target_table=report_dict.get("target", ""),
                    mapping_path=report_dict.get("mapping_path", ""),
                    rows_processed=report_dict.get("rows_extracted", 0),
                    anomalies=report_dict.get("anomalies", []),
                    recommendations=report_dict.get("recommendations", [])
                )
                self._save_report(data)

        except Exception as e:
            logger.error(f"Error in HTMLReportGenerator.handle_event: {e}")

    def _save_report(self, data: JobReportData):
        self._generate_html([data], is_batch=False)

    def _save_batch_report(self, jobs: List[JobReportData]):
        self._generate_html(jobs, is_batch=True)

    def _generate_html(self, jobs: List[JobReportData], is_batch: bool):
        if not jobs:
            return

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        mode_str = "batch" if is_batch else jobs[0].mode.lower().replace("_", "-")
        table_name = "multi" if is_batch else jobs[0].source_table
        filename = f"{mode_str}_{table_name}_{timestamp}.html"
        filepath = os.path.abspath(os.path.join(self.output_dir, filename))

        try:
            html_content = self._render_template(jobs, is_batch)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"Report generated: {filepath}")
            event_bus.publish(Event(EventType.REPORT_GENERATED, {
                "filepath": filepath,
                "filename": filename,
                "is_batch": is_batch
            }))
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")

    def _render_template(self, jobs: List[JobReportData], is_batch: bool) -> str:
        # Theme setup
        is_dry_run = any(j.mode == "DRY_RUN" for j in jobs)
        primary_color = "#3498db" if is_dry_run else "#2ecc71"
        if not is_dry_run and any(j.status in ("ABORTED", "FAIL") for j in jobs):
            primary_color = "#e74c3c"
        elif not is_dry_run and any(j.status == "WARN" for j in jobs):
            primary_color = "#f1c40f"

        title = "Sync-Mail Migration Report"
        if is_batch:
            title = "Sync-Mail Batch Migration Summary"
        elif is_dry_run:
            title = "Sync-Mail Dry Run Report"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: {primary_color};
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #2c3e50;
            --text-muted: #7f8c8d;
            --border: #dee2e6;
            --success: #2ecc71;
            --warning: #f1c40f;
            --danger: #e74c3c;
            --info: #3498db;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border);
        }}
        
        h1 {{ margin: 0; font-size: 24px; }}
        
        .badge {{
            padding: 8px 16px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 14px;
        }}
        
        .badge-success {{ background-color: var(--success); }}
        .badge-warning {{ background-color: var(--warning); }}
        .badge-danger {{ background-color: var(--danger); }}
        .badge-info {{ background-color: var(--info); }}
        
        .dry-run-banner {{
            background-color: var(--info);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }}
        
        .card-title {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        
        .card-value {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        h2 {{
            font-size: 18px;
            border-left: 4px solid var(--primary);
            padding-left: 10px;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background-color: #f1f3f5;
            font-weight: bold;
            color: var(--text-muted);
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        .recommendation-box {{
            background-color: #fff9db;
            border-left: 5px solid var(--warning);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        
        .recommendation-box h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #856404;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            font-size: 12px;
            color: var(--text-muted);
            text-align: center;
        }}
        
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 150px;
            color: rgba(0,0,0,0.03);
            pointer-events: none;
            z-index: -1;
            white-space: nowrap;
        }}

        .job-detail-card {{
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }}

        .error-message {{
            background-color: #fff5f5;
            color: var(--danger);
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #feb2b2;
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {f'<div class="watermark">DRY RUN</div>' if is_dry_run else ''}
        
        {f'<div class="dry-run-banner">MODE SIMULASI — TIDAK ADA DATA YANG DITULIS KE TARGET</div>' if is_dry_run else ''}
        
        <header>
            <div>
                <h1>{title}</h1>
                <p style="color: var(--text-muted); margin: 5px 0 0 0;">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div>
                <span class="badge {self._get_status_class(jobs)}">{self._get_overall_status(jobs)}</span>
            </div>
        </header>

        <section>
            <h2>Ringkasan Eksekutif</h2>
            <div class="grid">
                <div class="card">
                    <div class="card-title">Durasi Total</div>
                    <div class="card-value">{self._get_total_duration(jobs)}</div>
                </div>
                <div class="card">
                    <div class="card-title">Mode</div>
                    <div class="card-value">{"DRY RUN" if is_dry_run else "REAL SYNC"}</div>
                </div>
                <div class="card">
                    <div class="card-title">Total Baris</div>
                    <div class="card-value">{sum(j.rows_processed for j in jobs):,}</div>
                </div>
                <div class="card">
                    <div class="card-title">Success Rate</div>
                    <div class="card-value">{self._get_overall_success_rate(jobs):.1f}%</div>
                </div>
                <div class="card">
                    <div class="card-title">Total Anomali</div>
                    <div class="card-value">{sum(len(j.anomalies) for j in jobs)}</div>
                </div>
            </div>
        </section>

        <section>
            <h2>Detail Koneksi</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sisi</th>
                        <th>Host</th>
                        <th>Database</th>
                        <th>Tabel</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Source</td>
                        <td>{jobs[0].source_host}</td>
                        <td>{jobs[0].source_db}</td>
                        <td>{", ".join(set(j.source_table for j in jobs))}</td>
                    </tr>
                    <tr>
                        <td>Target</td>
                        <td>{jobs[0].target_host}</td>
                        <td>{jobs[0].target_db}</td>
                        <td>{", ".join(set(j.target_table for j in jobs))}</td>
                    </tr>
                </tbody>
            </table>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 5px;">
                Mapping File: {jobs[0].mapping_path or "N/A"}
            </p>
        </section>

        <section>
            <h2>Detail Per Tabel</h2>
            {self._render_jobs_detail(jobs)}
        </section>

        {self._render_recommendations(jobs)}

        <div class="footer">
            sync-mail v{jobs[0].version} | Host: {jobs[0].hostname} | &copy; {datetime.now().year}
        </div>
    </div>
</body>
</html>"""
        return html

    def _get_status_class(self, jobs: List[JobReportData]) -> str:
        if any(j.mode == "DRY_RUN" for j in jobs): return "badge-info"
        if all(j.status == "SUCCESS" for j in jobs): return "badge-success"
        if any(j.status == "ABORTED" for j in jobs): return "badge-danger"
        return "badge-warning"

    def _get_overall_status(self, jobs: List[JobReportData]) -> str:
        if any(j.mode == "DRY_RUN" for j in jobs):
            blockers = sum(1 for j in jobs for a in j.anomalies if a["severity"] == "BLOCKER")
            if blockers > 0: return "DRY RUN - FAIL"
            if any(len(j.anomalies) > 0 for j in jobs): return "DRY RUN - WARN"
            return "DRY RUN - PASS"
        
        if all(j.status == "SUCCESS" for j in jobs): return "SYNC COMPLETED"
        if all(j.status == "ABORTED" for j in jobs): return "SYNC FAILED"
        return "SYNC PARTIAL"

    def _get_total_duration(self, jobs: List[JobReportData]) -> str:
        if not jobs: return "0s"
        start = min((j.start_time for j in jobs if j.start_time), default=None)
        end = max((j.end_time for j in jobs if j.end_time), default=None)
        if start and end:
            diff = end - start
            seconds = int(diff.total_seconds())
            if seconds < 60: return f"{seconds}s"
            return f"{seconds // 60}m {seconds % 60}s"
        return "N/A"

    def _get_overall_success_rate(self, jobs: List[JobReportData]) -> float:
        total = sum(j.rows_processed for j in jobs)
        if total == 0: return 0.0
        committed = sum(j.rows_committed for j in jobs)
        return (committed / total) * 100

    def _render_jobs_detail(self, jobs: List[JobReportData]) -> str:
        rows = []
        for j in jobs:
            status_badge = f'<span class="badge {self._get_job_status_class(j)}">{j.status}</span>'
            rows.append(f"""
            <div class="card job-detail-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0;">{j.job_name}</h3>
                    {status_badge}
                </div>
                <div class="grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 15px;">
                    <div>
                        <div class="card-title">Rows Processed</div>
                        <div class="card-value">{j.rows_processed:,}</div>
                    </div>
                    <div>
                        <div class="card-title">Rows Committed</div>
                        <div class="card-value">{j.rows_committed:,}</div>
                    </div>
                    <div>
                        <div class="card-title">Duration</div>
                        <div class="card-value">{j.duration_str}</div>
                    </div>
                    <div>
                        <div class="card-title">Anomalies</div>
                        <div class="card-value">{len(j.anomalies)}</div>
                    </div>
                </div>
                {f'<div class="error-message"><strong>Error:</strong> {j.error_message}</div>' if j.error_message else ''}
                {self._render_anomalies_table(j.anomalies)}
            </div>
            """)
        return "\n".join(rows)

    def _get_job_status_class(self, job: JobReportData) -> str:
        if job.status in ("SUCCESS", "PASS"): return "badge-success"
        if job.status in ("ABORTED", "FAIL"): return "badge-danger"
        return "badge-warning"

    def _render_anomalies_table(self, anomalies: List[Dict[str, Any]]) -> str:
        if not anomalies:
            return '<p style="color: var(--success); font-size: 14px;">&check; Tidak ada anomali terdeteksi.</p>'
        
        rows = []
        for a in anomalies[:50]: # Limit to first 50
            sev_class = "badge-danger" if a["severity"] == "BLOCKER" else "badge-warning"
            rows.append(f"""
            <tr>
                <td><span class="badge {sev_class}" style="padding: 2px 6px; font-size: 10px;">{a["severity"]}</span></td>
                <td>{a["category"]}</td>
                <td><code>{a["column"]}</code></td>
                <td>{a["row_pk"]}</td>
                <td><code title="{a["raw_value"]}">{str(a["raw_value"])[:20]}{"..." if len(str(a["raw_value"])) > 20 else ""}</code></td>
                <td>{a["message"]}</td>
            </tr>
            """)
        
        table = f"""
        <div style="overflow-x: auto;">
            <table style="font-size: 13px; margin-top: 10px;">
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Category</th>
                        <th>Column</th>
                        <th>PK</th>
                        <th>Raw Value</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        """
        if len(anomalies) > 50:
            table += f'<p style="font-size: 12px; color: var(--text-muted); text-align: center;">... and {len(anomalies)-50} more anomalies hidden.</p>'
        return table

    def _render_recommendations(self, jobs: List[JobReportData]) -> str:
        all_recs = []
        seen = set()
        for j in jobs:
            for r in j.recommendations:
                if r not in seen:
                    all_recs.append(r)
                    seen.add(r)
        
        if not all_recs:
            return ""
            
        items = "".join([f"<li>{r}</li>" for r in all_recs])
        return f"""
        <section>
            <h2>Rekomendasi Tindak Lanjut</h2>
            <div class="recommendation-box">
                <h3>Tindakan yang Disarankan:</h3>
                <ul>
                    {items}
                </ul>
            </div>
        </section>
        """

# Initialize global reporter
reporter = HTMLReportGenerator()
