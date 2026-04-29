from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Button, Input, Static
from textual.containers import Vertical, Horizontal
from textual import work
from sqlalchemy.engine import make_url
import os

from sync_mail.db.connection import connection_scope
from sync_mail.db.introspect import describe_table
from sync_mail.reconciliation.auto_yaml import generate_mapping, save_mapping_to_yaml

class IntrospectScreen(Screen):
    """Screen for database introspection and mapping generation."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-container"):
            yield Label("Source DSN (mariadb+pymysql://user:pass@host:port/db)")
            yield Input(placeholder="mariadb+pymysql://user:pass@host:port/db", id="source-dsn")
            yield Label("Target DSN (mariadb+pymysql://user:pass@host:port/db)")
            yield Input(placeholder="mariadb+pymysql://user:pass@host:port/db", id="target-dsn")
            yield Label("Source Table")
            yield Input(placeholder="source_table_name", id="source-table")
            yield Label("Target Table")
            yield Input(placeholder="target_table_name", id="target-table")
            yield Label("Output Path (relative to current dir)")
            yield Input(value="mappings/new_mapping.yaml", id="output-path")
            
            with Horizontal():
                yield Button("Generate Mapping", id="btn-generate", variant="primary")
                yield Button("Back", id="btn-back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-generate":
            self.start_introspection()

    def start_introspection(self) -> None:
        source_dsn = self.query_one("#source-dsn", Input).value
        target_dsn = self.query_one("#target-dsn", Input).value
        source_table = self.query_one("#source-table", Input).value
        target_table = self.query_one("#target-table", Input).value
        output_path = self.query_one("#output-path", Input).value

        if not all([source_dsn, target_dsn, source_table, target_table]):
            self.notify("All fields are required!", severity="error")
            return

        self.query_one("#btn-generate").disabled = True
        self.notify("Starting introspection...", severity="information")
        self.run_introspection(source_dsn, target_dsn, source_table, target_table, output_path)

    @work(thread=True)
    def run_introspection(self, source_dsn: str, target_dsn: str, source_table: str, target_table: str, output_path: str):
        try:
            # Parse DSNs
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
            
            # Connect and introspect
            with connection_scope("source", s_params) as s_conn:
                s_meta = describe_table(s_conn, s_params["database"], source_table)
                
            with connection_scope("target", t_params) as t_conn:
                t_meta = describe_table(t_conn, t_params["database"], target_table)
                
            # Generate mapping
            doc = generate_mapping(s_meta, t_meta, source_table, target_table)
            
            # Save mapping
            output_dir = os.path.dirname(output_path) or "mappings"
            # Ensure filename ends with .yaml
            if not output_path.endswith(".yaml"):
                output_path += ".yaml"
            
            saved_path = save_mapping_to_yaml(doc, output_dir=output_dir)
            
            self.app.call_from_thread(self.on_success, saved_path)
            
        except Exception as e:
            self.app.call_from_thread(self.on_error, str(e))

    def on_success(self, path: str):
        self.notify(f"Mapping generated: {path}", severity="information", timeout=5)
        self.query_one("#btn-generate").disabled = False

    def on_error(self, error: str):
        self.notify(f"Error: {error}", severity="error", timeout=10)
        self.query_one("#btn-generate").disabled = False
