from textual.widgets import ProgressBar, Static, Label
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

class BatchProgress(Vertical):
    """Overall progress for a batch of jobs."""
    total_jobs = reactive(0)
    current_index = reactive(0)
    success_count = reactive(0)
    failure_count = reactive(0)
    current_job_name = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("Batch Progress: 0/0", id="batch-status")
        yield ProgressBar(total=100, id="batch-pb")
        with Horizontal():
            yield Static("Success: 0", id="success-count")
            yield Static("Failure: 0", id="failure-count")
            yield Static("Current: None", id="current-job")

    def watch_total_jobs(self, value: int) -> None:
        self.query_one("#batch-pb", ProgressBar).total = value
        self._update_label()

    def watch_current_index(self, value: int) -> None:
        self.query_one("#batch-pb", ProgressBar).progress = value
        self._update_label()

    def watch_success_count(self, value: int) -> None:
        self.query_one("#success-count", Static).update(f"Success: {value}")

    def watch_failure_count(self, value: int) -> None:
        self.query_one("#failure-count", Static).update(f"Failure: {value}")

    def watch_current_job_name(self, value: str) -> None:
        self.query_one("#current-job", Static).update(f"Current: {value}")

    def _update_label(self) -> None:
        self.query_one("#batch-status", Label).update(f"Batch Progress: {self.current_index}/{self.total_jobs}")
