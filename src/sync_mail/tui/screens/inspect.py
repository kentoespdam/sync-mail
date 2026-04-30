from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, DataTable, Static, Label
from textual.containers import Vertical, Horizontal
import os
import json
from pathlib import Path

from sync_mail.tui.screens.base import BaseNavigationScreen

class InspectScreen(BaseNavigationScreen):
    """Screen for inspecting state files."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label("Migration States (from ./state/*.state.json)", id="title")
            yield DataTable(id="state-table")
            
            with Vertical(id="details-panel", classes="hidden"):
                yield Label("State Details", id="details-title")
                yield Static("", id="details-content")
                yield Button("Close Details", id="btn-close-details")
            
            yield Static("Type 'B' and press Enter to go back to the previous step.", id="back-instruction", classes="nav-hint")

            with Horizontal():
                yield Button("Refresh", id="btn-refresh")
                yield Button("Back", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#state-table", DataTable)
        table.add_columns("Job Name", "Source", "Target", "Status", "Last PK", "Rows")
        table.cursor_type = "row"
        self.refresh_states()

    def refresh_states(self) -> None:
        table = self.query_one("#state-table", DataTable)
        table.clear()
        
        state_dir = Path("state")
        if not state_dir.exists():
            return
            
        for file in state_dir.glob("*.state.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    table.add_row(
                        data.get("job_name", "N/A"),
                        data.get("source_table", "N/A"),
                        data.get("target_table", "N/A"),
                        data.get("status", "unknown"),
                        str(data.get("last_pk", "N/A")),
                        str(data.get("rows_committed", 0))
                    )
            except Exception:
                continue

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Show full JSON details
        row_data = event.data_table.get_row(event.row_key)
        job_name = row_data[0]
        
        state_file = Path("state") / f"{job_name}.state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                content = f.read()
                self.query_one("#details-content", Static).update(content)
                self.query_one("#details-panel").remove_class("hidden")
                self.query_one("#state-table").add_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen_with_snapshot()
        elif event.button.id == "btn-refresh":
            self.refresh_states()
        elif event.button.id == "btn-close-details":
            self.query_one("#details-panel").add_class("hidden")
            self.query_one("#state-table").remove_class("hidden")
