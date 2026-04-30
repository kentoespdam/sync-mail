from textual.screen import Screen
from textual.widgets import Input, Select, Checkbox

class BaseNavigationScreen(Screen):
    """Base class for screens with back navigation and state retention."""

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Intercept 'B' to go back."""
        value = event.value.strip().upper()
        if value == "B":
            # Clear the input so it doesn't look like we're submitting 'B'
            event.input.value = ""
            self.app.pop_screen_with_snapshot()
            event.stop()

    def get_snapshot(self) -> dict:
        """Return a snapshot of current input values."""
        snapshot = {}
        # Snapshot Inputs
        for widget in self.query(Input):
            if widget.id:
                snapshot[widget.id] = widget.value
        # Snapshot Selects
        for widget in self.query(Select):
            if widget.id:
                snapshot[widget.id] = widget.value
        # Snapshot Checkboxes
        for widget in self.query(Checkbox):
            if widget.id:
                snapshot[widget.id] = widget.value
        return snapshot

    def load_snapshot(self, data: dict) -> None:
        """Load input values from snapshot."""
        for widget_id, value in data.items():
            try:
                # Try to find widget by ID across supported types
                widget = self.query_one(f"#{widget_id}")
                if isinstance(widget, Input):
                    widget.value = value
                elif isinstance(widget, Select):
                    widget.value = value
                elif isinstance(widget, Checkbox):
                    widget.value = value
            except:
                pass
