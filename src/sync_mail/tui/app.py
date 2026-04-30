from textual.app import App
from sync_mail.tui.screens.menu import MenuScreen
from sync_mail.tui.screens.introspect import IntrospectScreen
from sync_mail.tui.screens.migrate import MigrateScreen
from sync_mail.tui.screens.inspect import InspectScreen
from sync_mail.tui.screens.connection import ConnectionScreen
from sync_mail.tui.screens.dry_run import DryRunScreen

class SyncMailApp(App):
    """A Textual app to manage and monitor the sync-mail migration."""

    CSS = """
    Screen {
        background: #1e1e1e;
    }

    .hidden {
        display: none;
    }

    #menu-container {
        width: 60;
        height: auto;
        border: thick $primary;
        padding: 1;
        margin: 2;
        background: #2d2d2d;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    #rec-title {
        background: $primary;
        color: white;
        text-align: center;
        text-style: bold;
        padding: 0 1;
    }

    .rec-item {
        padding: 0 1;
        border-bottom: solid $primary;
    }

    .rec-item.success {
        color: lightgreen;
    }

    #form-container {
        padding: 1 2;
    }

    Label {
        margin-top: 1;
        text-style: bold;
    }

    #metrics-grid {
        layout: grid;
        grid-size: 2 2;
        height: 6;
        border: solid $accent;
        margin: 1 0;
        padding: 0 1;
    }

    #metrics-grid Static {
        width: 1fr;
        content-align: center middle;
        border: solid $primary;
    }

    #log-panel {
        height: 1fr;
        border: panel $primary;
        margin-top: 1;
    }

    #details-panel {
        border: solid $accent;
        padding: 1;
        margin: 1;
        height: 1fr;
    }

    #details-content {
        height: 1fr;
        overflow-y: scroll;
        background: $boost;
        padding: 1;
    }

    /* Connection Screen Styles */
    ConnectionScreen {
        align: center middle;
    }

    #connection-form-container {
        width: 80;
        height: auto;
        border: thick $primary;
        padding: 1 2;
        margin: 1;
        background: #2d2d2d;
    }

    #form-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #status-banner {
        width: 100%;
        background: $error;
        color: white;
        padding: 0 1;
        margin-bottom: 1;
        text-align: center;
    }

    .db-config-block {
        width: 1fr;
        border: solid $primary;
        padding: 1;
        margin: 0 1;
    }

    .db-config-block Label {
        width: 100%;
        content-align: center middle;
        background: $primary;
        color: white;
        margin-bottom: 1;
    }

    #form-actions {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    #form-actions Button {
        width: 20;
        margin: 0 2;
    }

    .nav-hint {
        width: 100%;
        content-align: center middle;
        color: $accent;
        text-style: italic;
        margin: 1 0;
    }
    """

    SCREENS = {
        "menu": MenuScreen,
        "introspect": IntrospectScreen,
        "migrate": MigrateScreen,
        "inspect": InspectScreen,
        "connection": ConnectionScreen,
        "dry_run": DryRunScreen,
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nav_history: list[dict] = []  # Stack of (screen_name, snapshot_data)

    def on_mount(self) -> None:
        self.push_screen_with_snapshot("menu")
        # If connection config is not valid, push the connection screen on top of menu
        if getattr(self, "config_status", "UNKNOWN") != "VALID":
            self.push_screen_with_snapshot("connection")

    def push_screen_with_snapshot(self, screen_name: str) -> None:
        """Push a screen and record it in navigation history."""
        # Snapshot current screen if it exists
        if self.screen_stack:
            current_screen = self.screen
            if hasattr(current_screen, "get_snapshot"):
                snapshot = current_screen.get_snapshot()
                if self.nav_history:
                    self.nav_history[-1]["data"] = snapshot
        
        self.nav_history.append({"screen": screen_name, "data": {}})
        self.push_screen(screen_name)

    def pop_screen_with_snapshot(self) -> None:
        """Pop current screen and restore snapshot of the previous one."""
        if len(self.nav_history) <= 1:
            return  # Menu Utama cannot be popped

        # Pop current from history
        self.nav_history.pop()
        
        # Pop from textual screen stack
        self.pop_screen()
        
        # New top screen should load its snapshot
        if self.nav_history:
            snapshot = self.nav_history[-1]["data"]
            # We need to wait for the screen to be active to load snapshot
            # or use a call_after_refresh/call_later
            self.call_later(self._load_current_snapshot, snapshot)

    def _load_current_snapshot(self, snapshot: dict) -> None:
        if hasattr(self.screen, "load_snapshot") and snapshot:
            self.screen.load_snapshot(snapshot)

    def action_refresh(self) -> None:
        self.refresh()

def run_tui():
    app = SyncMailApp()
    app.run()

if __name__ == "__main__":
    run_tui()
