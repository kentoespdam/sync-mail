from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Static, Label, Input
from textual.containers import Vertical, Horizontal, Grid
from textual.message import Message
from sync_mail.tui.screens.base import BaseNavigationScreen

class ConnectionScreen(BaseNavigationScreen):
    """Screen for database connection configuration."""

    class Connected(Message):
        """Message sent when connection details are submitted."""
        def __init__(self, config: dict) -> None:
            self.config = config
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="connection-form-container"):
            yield Static("DATABASE CONNECTION SETUP", id="form-title")
            
            status_msg = self._get_status_message()
            if status_msg:
                yield Static(status_msg, id="status-banner")

            with Horizontal():
                with Vertical(classes="db-config-block"):
                    yield Label("SOURCE DATABASE")
                    yield Input(placeholder="Host (localhost)", id="src-host", value="localhost")
                    yield Input(placeholder="Port (3306)", id="src-port", value="3306")
                    yield Input(placeholder="User", id="src-user")
                    yield Input(placeholder="Password", id="src-pass", password=True)
                    yield Input(placeholder="Database Name", id="src-db")

                with Vertical(classes="db-config-block"):
                    yield Label("TARGET DATABASE")
                    yield Input(placeholder="Host (localhost)", id="tgt-host", value="localhost")
                    yield Input(placeholder="Port (3306)", id="tgt-port", value="3306")
                    yield Input(placeholder="User", id="tgt-user")
                    yield Input(placeholder="Password", id="tgt-pass", password=True)
                    yield Input(placeholder="Database Name", id="tgt-db")

            yield Static("Type 'B' and press Enter to go back to the previous step.", id="back-instruction", classes="nav-hint")

            with Horizontal(id="form-actions"):
                yield Button("Connect", id="btn-connect", variant="success")
                yield Button("Quit", id="btn-quit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        # Pre-fill from existing config if available
        if hasattr(self.app, "connection_config"):
            config = self.app.connection_config
            s = config.get("source", {})
            t = config.get("target", {})
            
            if s:
                if s.get("host"): self.query_one("#src-host", Input).value = str(s.get("host"))
                if s.get("port"): self.query_one("#src-port", Input).value = str(s.get("port"))
                if s.get("user"): self.query_one("#src-user", Input).value = str(s.get("user"))
                if s.get("password"): self.query_one("#src-pass", Input).value = str(s.get("password"))
                if s.get("database"): self.query_one("#src-db", Input).value = str(s.get("database"))

            if t:
                if t.get("host"): self.query_one("#tgt-host", Input).value = str(t.get("host"))
                if t.get("port"): self.query_one("#tgt-port", Input).value = str(t.get("port"))
                if t.get("user"): self.query_one("#tgt-user", Input).value = str(t.get("user"))
                if t.get("password"): self.query_one("#tgt-pass", Input).value = str(t.get("password"))
                if t.get("database"): self.query_one("#tgt-db", Input).value = str(t.get("database"))

    def _get_status_message(self) -> str:
        status = getattr(self.app, "config_status", "UNKNOWN")
        if status == "MISSING_FILE":
            return "File 'connection.yaml' not found. Please enter connection details below."
        elif status == "EMPTY_FILE":
            return "File 'connection.yaml' is empty. Please enter connection details below."
        elif status == "INVALID_FORMAT":
            return "File 'connection.yaml' has an invalid format. Please enter connection details below."
        elif status in ["SOURCE_INCOMPLETE", "TARGET_INCOMPLETE", "BOTH_INCOMPLETE"]:
            return f"Connection configuration is incomplete ({status}). Please fill missing fields."
        elif "PARSE_ERROR" in status:
            return f"Error parsing 'connection.yaml': {status.split(':', 1)[1]}"
        return ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-quit":
            self.app.exit()
        elif event.button.id == "btn-connect":
            self.submit_form()

    def submit_form(self) -> None:
        # Collect data
        try:
            config = {
                "source": {
                    "host": self.query_one("#src-host", Input).value,
                    "port": int(self.query_one("#src-port", Input).value or 3306),
                    "user": self.query_one("#src-user", Input).value,
                    "password": self.query_one("#src-pass", Input).value,
                    "database": self.query_one("#src-db", Input).value,
                },
                "target": {
                    "host": self.query_one("#tgt-host", Input).value,
                    "port": int(self.query_one("#tgt-port", Input).value or 3306),
                    "user": self.query_one("#tgt-user", Input).value,
                    "password": self.query_one("#tgt-pass", Input).value,
                    "database": self.query_one("#tgt-db", Input).value,
                }
            }
            
            # Basic validation
            if not all([config["source"]["user"], config["source"]["database"], 
                        config["target"]["user"], config["target"]["database"]]):
                self.notify("User and Database are required for both source and target!", severity="error")
                return

            # Update app config and status
            self.app.connection_config = config
            self.app.config_status = "VALID"
            
            self.notify("Connection details updated.", severity="information")
            self.app.pop_screen_with_snapshot()
            
        except ValueError:
            self.notify("Port must be a number!", severity="error")
