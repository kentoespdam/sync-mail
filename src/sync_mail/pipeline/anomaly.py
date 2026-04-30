from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class AnomalySeverity(Enum):
    BLOCKER = auto()   # Will cause the actual migration to fail (e.g., NOT NULL violation, Type mismatch)
    ADVISORY = auto()  # Might cause data issues but might not fail the DB operation (e.g., Data truncation, ENUM mismatch)

class AnomalyCategory(Enum):
    TYPE_MISMATCH = "TYPE_MISMATCH"
    DATA_TRUNCATION = "DATA_TRUNCATION"
    NOT_NULL_VIOLATION = "NOT_NULL_VIOLATION"
    ENUM_MISMATCH = "ENUM_MISMATCH"
    DEFAULT_INVALID = "DEFAULT_INVALID"
    TRANSFORM_ERROR = "TRANSFORM_ERROR"
    MISSING_COLUMN = "MISSING_COLUMN"
    INVALID_SOURCE_COLUMN = "INVALID_SOURCE_COLUMN"

@dataclass
class Anomaly:
    category: AnomalyCategory
    severity: AnomalySeverity
    column: str
    row_pk: Any
    raw_value: Any
    message: str
    recommendation: str
    technical_detail: Optional[str] = None

    def __hash__(self):
        # Useful for deduplicating recommendations
        return hash((self.category, self.column, self.recommendation))

    def __eq__(self, other):
        if not isinstance(other, Anomaly):
            return False
        return (self.category == other.category and 
                self.column == other.column and 
                self.recommendation == other.recommendation)
