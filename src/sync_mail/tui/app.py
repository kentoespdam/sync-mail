from textual.app import App
from sync_mail.tui.screens.menu import MenuScreen
from sync_mail.tui.screens.introspect import IntrospectScreen
from sync_mail.tui.screens.migrate import MigrateScreen
from sync_mail.tui.screens.inspect import InspectScreen

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
        border: thin $primary;
    }

    #log-panel {
        height: 1fr;
        border: sunken $primary;
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
    """

    SCREENS = {
        "menu": MenuScreen,
        "introspect": IntrospectScreen,
        "migrate": MigrateScreen,
        "inspect": InspectScreen,
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def on_mount(self) -> None:
        self.push_screen("menu")

    def action_refresh(self) -> None:
        self.refresh()

def run_tui():
    app = SyncMailApp()
    app.run()

if __name__ == "__main__":
    run_tui()
