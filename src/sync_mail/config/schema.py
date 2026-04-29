from dataclasses import dataclass, field
from typing import List, Optional, Literal

TransformationType = Literal["NONE", "CAST", "INJECT_DEFAULT"]

@dataclass
class ColumnMapping:
    target_column: str
    source_column: Optional[str] = None
    transformation_type: TransformationType = "NONE"
    cast_target: Optional[str] = None
    default_value: Optional[str] = None
    # metadata for internal use (e.g., original type info for comments)
    _source_type: Optional[str] = None
    _target_type: Optional[str] = None

@dataclass
class MappingDocument:
    source_table: str
    target_table: str
    mappings: List[ColumnMapping]
    batch_size: int = 10000
    unmapped_source_columns: List[str] = field(default_factory=list)
