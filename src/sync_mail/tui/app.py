from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class SyncMailApp(App):
    """A Textual app to manage and monitor the sync-mail migration."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("Welcome to Sync-Mail!", id="body")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = SyncMailApp()
    app.run()
