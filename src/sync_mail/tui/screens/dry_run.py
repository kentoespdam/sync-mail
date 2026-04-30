from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Static, Label, Input, Select, ProgressBar
from textual.containers import Vertical, Horizontal, Container
from textual import work, on
from textual.reactive import reactive
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sync_mail.pipeline.dry_run import DryRunEngine
from sync_mail.pipeline.dry_run_report import DryRunReport
from sync_mail.config.loader import load_mapping
from sync_mail.db.connection import connect
from sync_mail.observability.events import event_bus, Event, EventType
from sync_mail.tui.widgets.anomaly_table import AnomalyTable
from sync_mail.tui.widgets.recommendation_panel import RecommendationPanel

from sync_mail.tui.screens.base import BaseNavigationScreen

class DryRunScreen(BaseNavigationScreen):
    """Screen for running and viewing Dry Run results."""

    BINDINGS = [
        ("b", "back_key", "Kembali"),
        ("s", "start", "Jalankan Dry Run"),
    ]

    CSS = """
    #dry-run-container {
        padding: 1;
    }

    #input-section {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #status-section {
        height: auto;
        margin-bottom: 1;
        align: center middle;
    }

    #progress-bar {
        width: 100%;
    }

    #result-header {
        height: 3;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    .pass { background: green; color: white; }
    .warn { background: orange; color: black; }
    .fail { background: red; color: white; }

    #report-section {
        layout: horizontal;
        height: 1fr;
    }

    #anomaly-section {
        width: 60%;
        border: solid $primary;
        margin-right: 1;
    }

    #recommendation-section {
        width: 40%;
        border: solid $primary;
    }

    #action-section {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    #action-section Button {
        margin: 0 1;
    }

    .hidden {
        display: none;
    }

    #status-label {
        text-style: bold italic;
        margin-bottom: 1;
    }
    """

    status_text = reactive("Idle")
    current_report: Optional[DryRunReport] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dry-run-container"):
            with Vertical(id="input-section"):
                yield Label("Konfigurasi Dry Run")
                yield Select([], id="select-mapping", prompt="Pilih Mapping YAML...")
                yield Label("Sample Limit (10-1000):")
                yield Input(value="100", id="input-sample-limit", type="integer")
                
                yield Static("Type 'B' and press Enter to go back to the previous step.", id="back-instruction", classes="nav-hint")

                with Horizontal(id="form-buttons"):
                    yield Button("Jalankan Dry Run", id="btn-start", variant="success")
                    yield Button("Kembali ke Menu", id="btn-back")

            with Vertical(id="status-section", classes="hidden"):
                yield Label(self.status_text, id="status-label")
                yield ProgressBar(id="progress-bar", total=100, show_percentage=True)
                yield Button("Batal", id="btn-cancel", variant="error")

            yield Static("", id="result-header", classes="hidden")

            with Horizontal(id="report-section", classes="hidden"):
                yield AnomalyTable(id="anomaly-table")
                yield RecommendationPanel(id="recommendation-panel")

            with Horizontal(id="action-section", classes="hidden"):
                yield Button("Simpan Laporan", id="btn-save", variant="primary")
                yield Button("Edit Mapping", id="btn-edit")
                yield Button("Lanjut ke Migrasi", id="btn-continue", variant="success")

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_mappings()
        event_bus.subscribe(self.on_event)

    def refresh_mappings(self) -> None:
        mapping_dir = Path("mappings")
        options = []
        if mapping_dir.exists():
            for f in sorted(mapping_dir.glob("*.yaml")):
                options.append((f.name, str(f)))
        
        select = self.query_one("#select-mapping", Select)
        select.set_options(options)

    def on_bus_event(self, event: Event) -> None:
        self.app.call_from_thread(self.handle_event_ui, event)

    def handle_event_ui(self, event: Event) -> None:
        if event.type == EventType.DRY_RUN_STARTED:
            self.status_text = "Menjalankan Dry Run..."
            self.query_one("#progress-bar", ProgressBar).total = event.payload.get("sample_limit", 100)
            self.query_one("#progress-bar", ProgressBar).progress = 0
            
        elif event.type == EventType.DRY_RUN_ROW_EVALUATED:
            self.query_one("#progress-bar", ProgressBar).progress = event.payload.get("rows_processed", 0)
            self.status_text = f"Memproses: {event.payload.get('rows_processed')} / {event.payload.get('total_sample')}"

        elif event.type == EventType.REPORT_GENERATED:
            self.notify(f"Laporan tersimpan di: {event.payload['filename']}", severity="information")

        elif event.type == EventType.DRY_RUN_COMPLETED:
            self.status_text = "Selesai."
            # payload['report'] is a dict from DryRunReport.to_dict()
            # We need the actual object for better handling, but we can reconstruct or pass it.
            # In engine.py, we publish report.to_dict().
            # Let's handle it.
            pass

    def watch_status_text(self, new_val: str) -> None:
        try:
            self.query_one("#status-label", Label).update(new_val)
        except Exception:
            pass

    @on(Button.Pressed, "#btn-start")
    def action_start(self) -> None:
        mapping_path = self.query_one("#select-mapping", Select).value
        if mapping_path is Select.BLANK:
            self.notify("Pilih file mapping terlebih dahulu!", severity="error")
            return
        
        try:
            sample_limit = int(self.query_one("#input-sample-limit", Input).value)
            if not (10 <= sample_limit <= 1000):
                raise ValueError()
        except ValueError:
            self.notify("Sample limit harus antara 10 dan 1000!", severity="error")
            return

        self.query_one("#input-section").add_class("hidden")
        self.query_one("#status-section").remove_class("hidden")
        self.query_one("#report-section").add_class("hidden")
        self.query_one("#action-section").add_class("hidden")
        self.query_one("#result-header").add_class("hidden")
        
        self.run_worker_dry_run(mapping_path, sample_limit)

    @work(thread=True)
    def run_worker_dry_run(self, mapping_path: str, sample_limit: int) -> None:
        self._should_cancel = False
        try:
            # 1. Load Mapping
            mapping = load_mapping(mapping_path)
            
            # 2. Get connections
            if not hasattr(self.app, "connection_config"):
                raise Exception("Konfigurasi koneksi tidak ditemukan. Harap atur di Connection Screen.")
            
            config = self.app.connection_config
            s_params = config.get("source")
            t_params = config.get("target")
            
            conn_s = connect("source", s_params)
            conn_t = connect("target", t_params)
            
            try:
                engine = DryRunEngine(
                    conn_s, 
                    conn_t, 
                    t_params.get("database"), 
                    mapping, 
                    sample_limit,
                    source_host=s_params.get("host"),
                    source_db=s_params.get("database"),
                    target_host=t_params.get("host"),
                    target_db=t_params.get("database"),
                    mapping_path=mapping_path
                )
                # Monkey patch execute to support cancellation if needed, 
                # but for now we just run it. 
                # The execute loop in DryRunEngine doesn't check for cancel yet.
                # Let's assume it's fast enough for sample_limit=1000.
                
                report = engine.execute()
                self.app.call_from_thread(self.show_results, report)
            finally:
                conn_s.close()
                conn_t.close()
                
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {str(e)}", severity="error")
            self.app.call_from_thread(self.reset_ui)

    def show_results(self, report: DryRunReport) -> None:
        self.current_report = report
        self.query_one("#status-section").add_class("hidden")
        
        # Header Badge
        header = self.query_one("#result-header", Static)
        header.remove_class("pass", "warn", "fail")
        header.remove_class("hidden")
        
        status = report.status
        if status == "PASS":
            header.add_class("pass")
            header.update(f"✅ PASS: {report.job_name} ({report.rows_extracted} rows)")
        elif status == "WARN":
            header.add_class("warn")
            header.update(f"⚠️ WARN: {report.job_name} ({len(report.anomalies)} anomalies)")
        else:
            header.add_class("fail")
            header.update(f"❌ FAIL: {report.job_name} ({len(report.anomalies)} anomalies)")
        
        # Tables
        self.query_one("#anomaly-table", AnomalyTable).update_anomalies(report.anomalies)
        self.query_one("#recommendation-panel", RecommendationPanel).update_recommendations(report.anomalies)
        
        self.query_one("#report-section").remove_class("hidden")
        self.query_one("#action-section").remove_class("hidden")
        
        # Disable continue if fail
        btn_continue = self.query_one("#btn-continue", Button)
        if status == "FAIL":
            btn_continue.disabled = True
            btn_continue.tooltip = "Selesaikan blocker terlebih dahulu sebelum migrasi nyata."
        else:
            btn_continue.disabled = False
            btn_continue.tooltip = "Mapping aman untuk dijalankan."

    def reset_ui(self) -> None:
        self.query_one("#input-section").remove_class("hidden")
        self.query_one("#status-section").add_class("hidden")

    @on(Button.Pressed, "#btn-back")
    def action_back(self) -> None:
        self.app.pop_screen_with_snapshot()

    def action_back_key(self) -> None:
        self.app.pop_screen_with_snapshot()

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        if hasattr(self, "current_engine") and self.current_engine:
            self.current_engine._should_stop = True
            self.notify("Membatalkan...", severity="warning")
        else:
            self.reset_ui()

    @on(Button.Pressed, "#btn-save")
    def action_save(self) -> None:
        if not self.current_report:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        txt_path = log_dir / f"dry-run-{timestamp}.txt"
        json_path = log_dir / f"dry-run-{timestamp}.json"
        
        with open(txt_path, "w") as f:
            f.write(self.current_report.format_text())
            
        with open(json_path, "w") as f:
            json.dump(self.current_report.to_dict(), f, indent=2)
            
        self.notify(f"Laporan disimpan ke {txt_path}", severity="info")

    @on(Button.Pressed, "#btn-edit")
    def action_edit(self) -> None:
        mapping_path = self.query_one("#select-mapping", Select).value
        self.notify(f"Buka file ini di editor Anda: {mapping_path}", severity="info")

    @on(Button.Pressed, "#btn-continue")
    def action_continue(self) -> None:
        self.app.push_screen_with_snapshot("migrate")
