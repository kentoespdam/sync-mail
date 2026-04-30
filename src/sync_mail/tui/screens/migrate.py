from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Static, Label, Input, Checkbox
from textual.containers import Vertical, Horizontal
from textual import work
from sqlalchemy.engine import make_url
import os
from pathlib import Path

from sync_mail.pipeline.orchestrator import MigrationJob, JobBatch
from sync_mail.observability.events import event_bus, Event, EventType
from sync_mail.tui.widgets.progress import MigrationProgress, BatchProgress
from sync_mail.tui.widgets.log_panel import LogPanel

from sync_mail.tui.screens.base import BaseNavigationScreen

class MigrateScreen(BaseNavigationScreen):
    """Screen for monitoring migration job (Single or Batch)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Vertical(id="config-panel"):
                yield Label("Job Configuration")
                yield Input(placeholder="Job Name / Batch Name", id="job-name", value="migration-01")
                yield Input(placeholder="Mapping YAML Path OR Directory", id="mapping-path", value="mappings/")
                yield Input(placeholder="Source DSN", id="source-dsn")
                yield Input(placeholder="Target DSN", id="target-dsn")
                with Horizontal():
                    yield Checkbox("Batch Mode (Directory)", id="chk-batch")
                    yield Checkbox("Stop on Failure", id="chk-stop-on-failure")
                
                yield Static("Type 'B' and press Enter to go back to the previous step.", id="back-instruction", classes="nav-hint")
                yield Button("Start", id="btn-start", variant="success")

            with Vertical(id="running-panel", classes="hidden"):
                yield BatchProgress(id="batch-metrics", classes="hidden")
                yield Label("Current Job Progress", id="progress-label")
                yield MigrationProgress(id="migration-metrics")
                yield LogPanel(id="log-panel")
                
                with Horizontal():
                    yield Button("Abort", id="btn-abort", variant="error")
                    yield Button("Finish", id="btn-finish", variant="primary", classes="hidden")
            
            yield Button("Back", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        event_bus.subscribe(self.on_event)
        
        # Pre-fill connection details if available
        if hasattr(self.app, "connection_config"):
            config = self.app.connection_config
            s = config.get("source", {})
            t = config.get("target", {})
            
            if s:
                s_dsn = f"mysql+pymysql://{s.get('user')}:{s.get('password')}@{s.get('host')}:{s.get('port')}/{s.get('database')}"
                self.query_one("#source-dsn", Input).value = s_dsn
            
            if t:
                t_dsn = f"mysql+pymysql://{t.get('user')}:{t.get('password')}@{t.get('host')}:{t.get('port')}/{t.get('database')}"
                self.query_one("#target-dsn", Input).value = t_dsn

    def on_event(self, event: Event) -> None:
        self.app.call_from_thread(self.handle_event_ui, event)

    def handle_event_ui(self, event: Event) -> None:
        if event.type == EventType.JOB_STARTED:
            self.query_one("#config-panel").add_class("hidden")
            self.query_one("#running-panel").remove_class("hidden")
            metrics = self.query_one("#migration-metrics", MigrationProgress)
            metrics.total_rows = event.payload.get("total_rows_est", 100)
            metrics.rows_done = 0
            
            log = self.query_one("#log-panel", LogPanel)
            log.write_info(f"Job '{event.payload['job_name']}' started.")

        elif event.type == EventType.BATCH_COMMITTED:
            metrics = self.query_one("#migration-metrics", MigrationProgress)
            metrics.rows_done += event.payload['rows']
            metrics.throughput = event.payload['throughput']
            metrics.eta = event.payload['eta']

        elif event.type == EventType.MULTI_JOB_PROGRESS:
            batch_metrics = self.query_one("#batch-metrics", BatchProgress)
            batch_metrics.remove_class("hidden")
            batch_metrics.total_jobs = event.payload['total_jobs']
            batch_metrics.current_index = event.payload['current_job_index']
            batch_metrics.success_count = event.payload['success_count']
            batch_metrics.failure_count = event.payload['failure_count']
            batch_metrics.current_job_name = event.payload['current_job_name']
            
            if event.payload.get("is_done"):
                self.query_one("#log-panel", LogPanel).write_success("Batch Migration Completed.")

        elif event.type == EventType.REPORT_GENERATED:
            self.query_one("#log-panel", LogPanel).write_success(
                f"Laporan tersimpan di: {event.payload['filepath']}"
            )

        elif event.type == EventType.JOB_COMPLETED:
            self.query_one("#log-panel", LogPanel).write_success(
                f"Job '{event.payload.get('job_name', 'N/A')}' Completed."
            )
            # Only show finish button if not in batch or if it's the last job
            # Actually BatchProgress.is_done will handle the final message.
            if not self.query_one("#chk-batch", Checkbox).value:
                self.query_one("#btn-abort").add_class("hidden")
                self.query_one("#btn-finish").remove_class("hidden")

        elif event.type == EventType.JOB_ABORTED:
            self.query_one("#log-panel", LogPanel).write_error(
                f"Job Aborted: {event.payload.get('reason')}"
            )
            if not self.query_one("#chk-batch", Checkbox).value:
                self.query_one("#btn-abort").add_class("hidden")
                self.query_one("#btn-finish").remove_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen_with_snapshot()
        elif event.button.id == "btn-start":
            self.start_process()
        elif event.button.id == "btn-abort":
            if hasattr(self, "current_job"):
                self.current_job._should_abort = True
            if hasattr(self, "batch"):
                for job in self.batch.jobs:
                    job._should_abort = True
            self.notify("Aborting...", severity="warning")
        elif event.button.id == "btn-finish":
            self.app.pop_screen_with_snapshot()

    def start_process(self) -> None:
        job_name = self.query_one("#job-name", Input).value
        mapping_path = self.query_one("#mapping-path", Input).value
        source_dsn = self.query_one("#source-dsn", Input).value
        target_dsn = self.query_one("#target-dsn", Input).value
        is_batch = self.query_one("#chk-batch", Checkbox).value
        stop_on_failure = self.query_one("#chk-stop-on-failure", Checkbox).value

        if not all([job_name, mapping_path, source_dsn, target_dsn]):
            self.notify("All fields are required!", severity="error")
            return

        try:
            s_url = make_url(source_dsn)
            t_url = make_url(target_dsn)
            s_params = {"host": s_url.host, "port": s_url.port or 3306, "user": s_url.username, "password": s_url.password, "database": s_url.database}
            t_params = {"host": t_url.host, "port": t_url.port or 3306, "user": t_url.username, "password": t_url.password, "database": t_url.database}
            
            if is_batch:
                mapping_dir = Path(mapping_path)
                if not mapping_dir.is_dir():
                    self.notify("Mapping path must be a directory in Batch Mode", severity="error")
                    return
                
                jobs = []
                for yaml_file in sorted(mapping_dir.glob("*.yaml")):
                    # Job name per table
                    table_name = yaml_file.stem
                    jobs.append(MigrationJob(f"{job_name}-{table_name}", str(yaml_file), s_params, t_params))
                
                if not jobs:
                    self.notify("No YAML files found in directory", severity="error")
                    return
                
                self.batch = JobBatch(jobs, stop_on_failure=stop_on_failure)
                self.run_batch_worker()
            else:
                self.current_job = MigrationJob(job_name, mapping_path, s_params, t_params)
                self.run_single_worker()
                
        except Exception as e:
            self.notify(f"Configuration error: {e}", severity="error")

    @work(thread=True)
    def run_single_worker(self) -> None:
        try:
            self.current_job.run()
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Runtime error: {e}", severity="error")
        finally:
            self.app.call_from_thread(self._show_finish)

    @work(thread=True)
    def run_batch_worker(self) -> None:
        try:
            self.batch.run()
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Batch error: {e}", severity="error")
        finally:
            self.app.call_from_thread(self._show_finish)

    def _show_finish(self) -> None:
        self.query_one("#btn-abort").add_class("hidden")
        self.query_one("#btn-finish").remove_class("hidden")
