from textual.app import ComposeResult
from textual.widgets import Header, Footer, Label, Button, Input, Static, Checkbox
from textual.containers import Vertical, Horizontal
from textual import work
from sqlalchemy.engine import make_url
import os

from sync_mail.db.connection import connection_scope
from sync_mail.db.introspect import describe_table, list_tables
from sync_mail.reconciliation.auto_yaml import generate_mapping, save_mapping_to_yaml, generate_mappings_for_schema

from sync_mail.tui.screens.base import BaseNavigationScreen

class IntrospectScreen(BaseNavigationScreen):
    """Screen for database introspection and mapping generation."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-container"):
            yield Label("Source DSN (mariadb+pymysql://user:pass@host:port/db)")
            yield Input(placeholder="mariadb+pymysql://user:pass@host:port/db", id="source-dsn")
            yield Label("Target DSN (mariadb+pymysql://user:pass@host:port/db)")
            yield Input(placeholder="mariadb+pymysql://user:pass@host:port/db", id="target-dsn")
            
            with Horizontal():
                yield Checkbox("Schema Mode (All Tables)", id="chk-schema")
            
            with Vertical(id="table-inputs"):
                yield Label("Source Table")
                yield Input(placeholder="source_table_name", id="source-table")
                yield Label("Target Table")
                yield Input(placeholder="target_table_name", id="target-table")
            
            yield Label("Output Path/Directory")
            yield Input(value="mappings/", id="output-path")
            
            yield Static("Type 'B' and press Enter to go back to the previous step.", id="back-instruction", classes="nav-hint")

            with Horizontal():
                yield Button("Generate Mapping(s)", id="btn-generate", variant="primary")
                yield Button("Back", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
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

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "chk-schema":
            if event.value:
                self.query_one("#table-inputs").add_class("hidden")
            else:
                self.query_one("#table-inputs").remove_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen_with_snapshot()
        elif event.button.id == "btn-generate":
            self.start_introspection()

    def start_introspection(self) -> None:
        source_dsn = self.query_one("#source-dsn", Input).value
        target_dsn = self.query_one("#target-dsn", Input).value
        is_schema = self.query_one("#chk-schema", Checkbox).value
        output_path = self.query_one("#output-path", Input).value

        if not all([source_dsn, target_dsn, output_path]):
            self.notify("DSNs and Output Path are required!", severity="error")
            return

        self.query_one("#btn-generate").disabled = True
        self.notify("Starting introspection...", severity="information")
        
        if is_schema:
            self.run_schema_introspection(source_dsn, target_dsn, output_path)
        else:
            source_table = self.query_one("#source-table", Input).value
            target_table = self.query_one("#target-table", Input).value
            if not all([source_table, target_table]):
                self.notify("Table names are required in Single-Table mode", severity="error")
                self.query_one("#btn-generate").disabled = False
                return
            self.run_single_introspection(source_dsn, target_dsn, source_table, target_table, output_path)

    @work(thread=True)
    def run_single_introspection(self, source_dsn, target_dsn, source_table, target_table, output_path):
        try:
            s_url = make_url(source_dsn)
            t_url = make_url(target_dsn)
            s_params = {"host": s_url.host, "port": s_url.port or 3306, "user": s_url.username, "password": s_url.password, "database": s_url.database}
            t_params = {"host": t_url.host, "port": t_url.port or 3306, "user": t_url.username, "password": t_url.password, "database": t_url.database}
            
            with connection_scope("source", s_params) as s_conn:
                s_meta = describe_table(s_conn, s_params["database"], source_table)
            with connection_scope("target", t_params) as t_conn:
                t_meta = describe_table(t_conn, t_params["database"], target_table)
                
            from sync_mail.reconciliation.auto_yaml import generate_mapping, save_mapping_to_yaml
            doc = generate_mapping(s_meta, t_meta, source_table, target_table)
            
            # If output_path is a directory, append default filename
            if output_path.endswith("/") or os.path.isdir(output_path):
                os.makedirs(output_path, exist_ok=True)
                final_path = save_mapping_to_yaml(doc, output_dir=output_path)
            else:
                final_path = save_mapping_to_yaml(doc, output_dir=os.path.dirname(output_path))
                
            self.app.call_from_thread(self.on_success, f"Mapping generated: {final_path}")
        except Exception as e:
            self.app.call_from_thread(self.on_error, str(e))

    @work(thread=True)
    def run_schema_introspection(self, source_dsn, target_dsn, output_dir):
        try:
            s_url = make_url(source_dsn)
            t_url = make_url(target_dsn)
            s_params = {"host": s_url.host, "port": s_url.port or 3306, "user": s_url.username, "password": s_url.password, "database": s_url.database}
            t_params = {"host": t_url.host, "port": t_url.port or 3306, "user": t_url.username, "password": t_url.password, "database": t_url.database}
            
            with connection_scope("source", s_params) as s_conn:
                with connection_scope("target", t_params) as t_conn:
                    paths = generate_mappings_for_schema(s_conn, t_conn, s_params["database"], t_params["database"], output_dir=output_dir)
            
            self.app.call_from_thread(self.on_success, f"Generated {len(paths)} mapping files in {output_dir}")
        except Exception as e:
            self.app.call_from_thread(self.on_error, str(e))

    def on_success(self, message: str):
        self.notify(message, severity="information", timeout=5)
        self.query_one("#btn-generate").disabled = False

    def on_error(self, error: str):
        self.notify(f"Error: {error}", severity="error", timeout=10)
        self.query_one("#btn-generate").disabled = False
