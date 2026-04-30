# src/sync_mail/pipeline/transformer.py

import decimal
from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from sync_mail.config.schema import MappingDocument
from sync_mail.errors import BatchFailedError

def transform_row(
    row: Dict[str, Any], 
    mapping: MappingDocument, 
    current_time: Optional[datetime] = None
) -> Tuple[Any, ...]:
    """
    Transforms a single source row into a tuple ready for target insertion.
    """
    transformed_row = []
    pk_val = row.get(mapping.pk_column, "UNKNOWN")
    
    for m in mapping.mappings:
        val = None
        
        if m.transformation_type == "NONE":
            val = row.get(m.source_column)
            
        elif m.transformation_type == "CAST":
            source_val = row.get(m.source_column)
            if source_val is None:
                val = None
            else:
                try:
                    if m.cast_target == "VARCHAR" or m.cast_target == "TEXT":
                        val = str(source_val)
                    elif m.cast_target == "INTEGER":
                        val = int(source_val)
                    elif m.cast_target == "DECIMAL":
                        val = Decimal(str(source_val))
                    elif m.cast_target == "FLOAT":
                        val = float(source_val)
                    else:
                        val = str(source_val)
                except (ValueError, TypeError, decimal.InvalidOperation) as e:
                    raise BatchFailedError(
                        f"Transformation CAST failed for column '{m.target_column}' at PK {pk_val}",
                        context={
                            "pk": pk_val,
                            "column": m.target_column,
                            "source_value": source_val,
                            "cast_target": m.cast_target,
                            "error": str(e)
                        }
                    ) from e
                    
        elif m.transformation_type == "INJECT_DEFAULT":
            if m.default_value == "CURRENT_TIMESTAMP":
                val = current_time
            else:
                val = m.default_value
        
        transformed_row.append(val)
        
    return tuple(transformed_row)

def transform(rows: List[Dict[str, Any]], mapping: MappingDocument) -> List[Tuple[Any, ...]]:
    """
    Transforms a list of source rows into a list of tuples ready for target insertion.
    """
    transformed_rows = []
    
    # Cache current timestamp if needed (once per batch)
    current_time = None
    for m in mapping.mappings:
        if m.transformation_type == "INJECT_DEFAULT" and m.default_value == "CURRENT_TIMESTAMP":
            current_time = datetime.now(UTC).replace(tzinfo=None)
            break

    for row in rows:
        transformed_rows.append(transform_row(row, mapping, current_time))
        
    return transformed_rows

from typing import Optional
