from textual.widgets import DataTable
from typing import List, Dict, Any
from sync_mail.pipeline.anomaly import Anomaly

class AnomalyTable(DataTable):
    """Widget for displaying grouped anomalies from Dry Run."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Kategori", "Target Column", "PK", "Nilai", "Pesan")

    def update_anomalies(self, anomalies: List[Anomaly], filter_severity: Any = None) -> None:
        self.clear()
        
        # Group by (category, column, message)
        groups: Dict[tuple, List[Anomaly]] = {}
        for a in anomalies:
            if filter_severity and a.severity != filter_severity:
                continue
            
            key = (a.category.value, a.column, a.message)
            if key not in groups:
                groups[key] = []
            groups[key].append(a)

        for key, group in groups.items():
            cat, col, msg = key
            
            # PK grouping logic: 1, 2, 3, ... (+n)
            pks = [str(a.row_pk) for a in group]
            if len(pks) > 5:
                pk_str = f"{', '.join(pks[:5])} ... (+{len(pks) - 5})"
            else:
                pk_str = ", ".join(pks)
            
            # Raw values: show first 3
            vals = [repr(a.raw_value) for a in group]
            if len(vals) > 3:
                val_str = f"{', '.join(vals[:3])} ..."
            else:
                val_str = ", ".join(vals)

            self.add_row(cat, col, pk_str, val_str, msg)
