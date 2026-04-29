from textual.widgets import RichLog
from textual.binding import Binding

class LogPanel(RichLog):
    """Custom RichLog with bindings and auto-scroll."""
    
    BINDINGS = [
        Binding("c", "clear", "Clear Logs"),
    ]

    def action_clear(self) -> None:
        self.clear()

    def write_info(self, message: str) -> None:
        self.write(f"[blue]INFO:[/blue] {message}")

    def write_error(self, message: str) -> None:
        self.write(f"[bold red]ERROR:[/bold red] {message}")

    def write_success(self, message: str) -> None:
        self.write(f"[bold green]SUCCESS:[/bold green] {message}")
