from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
from datetime import datetime
from sync_mail.pipeline.anomaly import Anomaly, AnomalySeverity, AnomalyCategory

@dataclass
class DryRunReport:
    job_name: str
    source_table: str
    target_table: str
    sample_limit: int
    source_host: str = ""
    source_db: str = ""
    target_host: str = ""
    target_db: str = ""
    mapping_path: str = ""
    rows_extracted: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    anomalies: List[Anomaly] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(a.severity == AnomalySeverity.BLOCKER for a in self.anomalies):
            return "FAIL"
        if self.anomalies:
            return "WARN"
        return "PASS"

    def get_summary(self) -> Dict[str, int]:
        summary = {}
        for cat in AnomalyCategory:
            count = sum(1 for a in self.anomalies if a.category == cat)
            if count > 0:
                summary[cat.value] = count
        return summary

    def get_unique_recommendations(self) -> List[str]:
        # Deduplicate recommendations while preserving order
        recs = []
        seen = set()
        
        # Prioritize blockers
        blockers = [a for a in self.anomalies if a.severity == AnomalySeverity.BLOCKER]
        advisories = [a for a in self.anomalies if a.severity == AnomalySeverity.ADVISORY]
        
        for a in blockers + advisories:
            if a.recommendation not in seen:
                recs.append(a.recommendation)
                seen.add(a.recommendation)
        return recs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_name": self.job_name,
            "source": self.source_table,
            "target": self.target_table,
            "sample_limit": self.sample_limit,
            "source_host": self.source_host,
            "source_db": self.source_db,
            "target_host": self.target_host,
            "target_db": self.target_db,
            "mapping_path": self.mapping_path,
            "rows_extracted": self.rows_extracted,
            "status": self.status,
            "summary": self.get_summary(),
            "recommendations": self.get_unique_recommendations(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "anomalies": [
                {
                    "category": a.category.value,
                    "severity": a.severity.name,
                    "column": a.column,
                    "row_pk": a.row_pk,
                    "raw_value": str(a.raw_value),
                    "message": a.message,
                    "recommendation": a.recommendation
                }
                for a in self.anomalies
            ]
        }

    def format_text(self) -> str:
        lines = []
        lines.append("┌─ DRY RUN REPORT " + "─" * (45 - 18) + "┐")
        lines.append(f"│ Job:        {self.job_name:<33} │")
        lines.append(f"│ Sample:     {self.rows_extracted:<3} rows extracted / {self.sample_limit:<3} limit    │")
        status_color = "✅" if self.status == "PASS" else "⚠️" if self.status == "WARN" else "❌"
        blocker_count = sum(1 for a in self.anomalies if a.severity == AnomalySeverity.BLOCKER)
        advisory_count = sum(1 for a in self.anomalies if a.severity == AnomalySeverity.ADVISORY)
        lines.append(f"│ Status:     {status_color} {self.status:<4} ({blocker_count} blocker, {advisory_count} advisory)   │")
        lines.append("└" + "─" * 45 + "┘")

        if self.anomalies:
            # Group by category
            by_cat = {}
            for a in self.anomalies:
                if a.category not in by_cat:
                    by_cat[a.category] = []
                by_cat[a.category].append(a)

            for sev in [AnomalySeverity.BLOCKER, AnomalySeverity.ADVISORY]:
                sev_label = "BLOCKER" if sev == AnomalySeverity.BLOCKER else "ADVISORY"
                sev_anomalies = [a for a in self.anomalies if a.severity == sev]
                if not sev_anomalies:
                    continue

                lines.append(f"\n▼ {sev_label}")
                
                # Group by category within severity
                cat_groups = {}
                for a in sev_anomalies:
                    if a.category not in cat_groups:
                        cat_groups[a.category] = {}
                    if a.column not in cat_groups[a.category]:
                        cat_groups[a.category][a.column] = []
                    cat_groups[a.category][a.column].append(a)

                for cat, col_groups in cat_groups.items():
                    for col, group in col_groups.items():
                        lines.append(f"  [{cat.value}] kolom target `{col}`")
                        pks = ", ".join(str(a.row_pk) for a in group[:3])
                        if len(group) > 3:
                            pks += f", ... (total {len(group)})"
                        lines.append(f"    PK: {pks}")
                        example_vals = ", ".join(repr(a.raw_value) for a in group[:3])
                        lines.append(f"    Contoh nilai: {example_vals}")
                        lines.append(f"    → Rekomendasi: {group[0].recommendation}")

            lines.append("\n▼ REKOMENDASI TINDAK LANJUT (deduplicated)")
            for i, rec in enumerate(self.get_unique_recommendations(), 1):
                lines.append(f"  {i}. {rec}")

        return "\n".join(lines)

from typing import Optional
