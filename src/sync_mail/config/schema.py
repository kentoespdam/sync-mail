from dataclasses import dataclass, field
from typing import List, Optional, Literal

TransformationType = Literal["NONE", "CAST", "INJECT_DEFAULT"]

@dataclass
class ColumnMapping:
    """
    Metadata for a single column mapping.
    """
    target_column: str
    transformation_type: TransformationType = "NONE"
    source_column: Optional[str] = None
    cast_target: Optional[str] = None
    default_value: Optional[str] = None
    # metadata/comments for the YAML output
    comment: Optional[str] = None
    _source_type: Optional[str] = None
    _target_type: Optional[str] = None
    _line_no: Optional[int] = None

@dataclass
class MappingDocument:
    """
    Root configuration for a migration job between two tables.
    """
    source_table: str
    target_table: str
    pk_column: str
    batch_size: int = 10000
    mappings: List[ColumnMapping] = field(default_factory=list)
    unmapped_source_columns: List[str] = field(default_factory=list)
