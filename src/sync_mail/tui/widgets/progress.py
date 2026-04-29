from textual.widgets import ProgressBar, Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.app import ComposeResult

class MigrationProgress(Vertical):
    """Combined progress bar and metrics widget."""
    
    total_rows = reactive(100)
    rows_done = reactive(0)
    throughput = reactive(0.0)
    eta = reactive("--:--:--")

    def compose(self) -> ComposeResult:
        yield ProgressBar(total=self.total_rows, show_eta=True, id="pb")
        with Horizontal(id="metrics"):
            yield Static("Throughput: 0 rows/s", id="throughput")
            yield Static("ETA: --:--:--", id="eta")

    def watch_total_rows(self, value: int) -> None:
        self.query_one("#pb", ProgressBar).total = value

    def watch_rows_done(self, value: int) -> None:
        self.query_one("#pb", ProgressBar).progress = value

    def watch_throughput(self, value: float) -> None:
        self.query_one("#throughput", Static).update(f"Throughput: {value:.2f} rows/s")

    def watch_eta(self, value: str) -> None:
        self.query_one("#eta", Static).update(f"ETA: {value}")
