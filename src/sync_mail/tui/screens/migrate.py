from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input
from textual.containers import Vertical, Horizontal
from textual import work
from sqlalchemy.engine import make_url
import os

from sync_mail.pipeline.orchestrator import MigrationJob
from sync_mail.observability.events import event_bus, Event, EventType
from sync_mail.tui.widgets.progress import MigrationProgress
from sync_mail.tui.widgets.log_panel import LogPanel

class MigrateScreen(Screen):
    """Screen for monitoring migration job."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Vertical(id="config-panel"):
                yield Label("Job Configuration")
                yield Input(placeholder="Job Name", id="job-name", value="migration-01")
                yield Input(placeholder="Mapping YAML Path", id="mapping-path", value="mappings/test.yaml")
                yield Input(placeholder="Source DSN", id="source-dsn")
                yield Input(placeholder="Target DSN", id="target-dsn")
                yield Button("Start Migration", id="btn-start", variant="success")

            with Vertical(id="running-panel", classes="hidden"):
                yield Label("Migration Progress", id="progress-label")
                yield MigrationProgress(id="migration-metrics")
                
                yield LogPanel(id="log-panel")
                
                with Horizontal():
                    yield Button("Abort", id="btn-abort", variant="error")
                    yield Button("Finish", id="btn-finish", variant="primary", classes="hidden")
            
            yield Button("Back", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        event_bus.subscribe(self.on_event)

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
            log.write(f"Source: {event.payload['source_table']} -> Target: {event.payload['target_table']}")

        elif event.type == EventType.BATCH_COMMITTED:
            metrics = self.query_one("#migration-metrics", MigrationProgress)
            metrics.rows_done += event.payload['rows']
            metrics.throughput = event.payload['throughput']
            metrics.eta = event.payload['eta']
            
            self.query_one("#log-panel", LogPanel).write(
                f"Batch {event.payload['batch_id']} committed: {event.payload['rows']} rows. Last PK: {event.payload['last_pk']}"
            )

        elif event.type == EventType.JOB_COMPLETED:
            self.query_one("#log-panel", LogPanel).write_success(
                f"Job Completed! Total rows: {event.payload.get('total_rows')}"
            )
            self.query_one("#btn-abort").add_class("hidden")
            self.query_one("#btn-finish").remove_class("hidden")
            self.notify("Migration completed successfully!", severity="information")

        elif event.type == EventType.JOB_ABORTED:
            self.query_one("#log-panel", LogPanel).write_error(
                f"Job Aborted: {event.payload.get('reason')}"
            )
            self.query_one("#btn-abort").add_class("hidden")
            self.query_one("#btn-finish").remove_class("hidden")
            self.notify(f"Migration aborted: {event.payload.get('reason')}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-start":
            self.start_job()
        elif event.button.id == "btn-abort":
            if hasattr(self, "job"):
                self.job._should_abort = True
                self.notify("Aborting job...", severity="warning")
        elif event.button.id == "btn-finish":
            self.app.pop_screen()

    def start_job(self) -> None:
        job_name = self.query_one("#job-name", Input).value
        mapping_path = self.query_one("#mapping-path", Input).value
        source_dsn = self.query_one("#source-dsn", Input).value
        target_dsn = self.query_one("#target-dsn", Input).value

        if not all([job_name, mapping_path, source_dsn, target_dsn]):
            self.notify("All fields are required!", severity="error")
            return

        try:
            s_url = make_url(source_dsn)
            t_url = make_url(target_dsn)
            
            s_params = {
                "host": s_url.host,
                "port": s_url.port or 3306,
                "user": s_url.username,
                "password": s_url.password,
                "database": s_url.database
            }
            
            t_params = {
                "host": t_url.host,
                "port": t_url.port or 3306,
                "user": t_url.username,
                "password": t_url.password,
                "database": t_url.database
            }
            
            self.job = MigrationJob(job_name, mapping_path, s_params, t_params)
            self.run_migration()
        except Exception as e:
            self.notify(f"Configuration error: {e}", severity="error")

    @work(thread=True)
    def run_migration(self) -> None:
        try:
            self.job.run()
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Runtime error: {e}", severity="error")
