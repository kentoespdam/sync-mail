from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Vertical, ScrollableContainer
from typing import List, Set
from sync_mail.pipeline.anomaly import Anomaly, AnomalySeverity

class RecommendationPanel(Vertical):
    """Panel for showing deduplicated recommendations with priority icons."""

    def compose(self) -> ComposeResult:
        yield Label("REKOMENDASI TINDAK LANJUT", id="rec-title")
        yield ScrollableContainer(id="rec-list")

    def update_recommendations(self, anomalies: List[Anomaly]) -> None:
        rec_list = self.query_one("#rec-list", ScrollableContainer)
        # Clear existing
        for child in rec_list.children:
            child.remove()
        
        if not anomalies:
            rec_list.mount(Static("Tidak ada anomali. Mapping siap dipakai.", classes="rec-item success"))
            return

        # Deduplicate
        seen: Set[str] = set()
        
        # Sort by severity (Blockers first)
        sorted_anomalies = sorted(anomalies, key=lambda x: x.severity.value)
        
        for a in sorted_anomalies:
            if a.recommendation not in seen:
                icon = "🔴 Blocker" if a.severity == AnomalySeverity.BLOCKER else "🟡 Advisory"
                rec_list.mount(Static(f"{icon}: {a.recommendation}", classes="rec-item"))
                seen.add(a.recommendation)
