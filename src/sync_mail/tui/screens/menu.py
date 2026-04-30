from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Vertical, Center

class MenuScreen(Screen):
    """Main menu screen for sync-mail."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="menu-container"):
                yield Static("SYNC-MAIL CONTROL PANEL", id="title")
                yield Button("1. Introspect Schema → Generate YAML", id="btn-introspect", variant="primary")
                yield Button("2. Dry Run / Validate Mapping", id="btn-dry-run", variant="warning")
                yield Button("3. Run Migration Job", id="btn-migrate", variant="success")
                yield Button("4. Inspect Last State", id="btn-inspect", variant="default")
                yield Button("5. Quit", id="btn-quit", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-introspect":
            self.app.push_screen_with_snapshot("introspect")
        elif event.button.id == "btn-dry-run":
            self.app.push_screen_with_snapshot("dry_run")
        elif event.button.id == "btn-migrate":
            self.app.push_screen_with_snapshot("migrate")
        elif event.button.id == "btn-inspect":
            self.app.push_screen_with_snapshot("inspect")
        elif event.button.id == "btn-quit":
            self.app.exit()
