from typing import List, Set
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.errors.exceptions import MappingError

def validate(mapping_doc: MappingDocument) -> None:
    """
    Validates a MappingDocument for semantic correctness.
    Raises MappingError with all violations if any are found.
    """
    errors = []
    
    # (g) source_table and target_table not empty
    if not mapping_doc.source_table:
        errors.append(f"{_fmt_line(mapping_doc)} 'source_table' tidak boleh kosong.")
    if not mapping_doc.target_table:
        errors.append(f"{_fmt_line(mapping_doc)} 'target_table' tidak boleh kosong.")
        
    # (d) batch_size in range 5,000 - 15,000
    if not (5000 <= mapping_doc.batch_size <= 15000):
        errors.append(f"{_fmt_line(mapping_doc)} 'batch_size' ({mapping_doc.batch_size}) di luar rentang valid 5.000 - 15.000.")
        
    # (e) Duplicate target_column
    seen_targets: Set[str] = set()
    
    for i, mapping in enumerate(mapping_doc.mappings):
        # (f) Check for ACTION_REQUIRED
        if _has_action_required(mapping):
            errors.append(f"{_fmt_line(mapping)} Kolom '{mapping.target_column}' masih mengandung 'ACTION_REQUIRED'.")
            
        # (e) Duplication check
        if mapping.target_column in seen_targets:
            errors.append(f"{_fmt_line(mapping)} Duplikasi target_column: '{mapping.target_column}'.")
        seen_targets.add(mapping.target_column)
        
        # (a) CAST must have cast_target
        if mapping.transformation_type == "CAST" and not mapping.cast_target:
            errors.append(f"{_fmt_line(mapping)} Kolom '{mapping.target_column}' (CAST) wajib punya 'cast_target'.")
            
        # (b) INJECT_DEFAULT must have default_value
        if mapping.transformation_type == "INJECT_DEFAULT" and mapping.default_value is None:
             errors.append(f"{_fmt_line(mapping)} Kolom '{mapping.target_column}' (INJECT_DEFAULT) wajib punya 'default_value'.")
             
        # (c) NONE must have source_column
        if mapping.transformation_type == "NONE" and not mapping.source_column:
             errors.append(f"{_fmt_line(mapping)} Kolom '{mapping.target_column}' (NONE) wajib punya 'source_column'.")

    if errors:
        msg = "Mapping document tidak valid:\n- " + "\n- ".join(errors)
        raise MappingError(msg)

def _fmt_line(obj: any) -> str:
    """Helper to format line number prefix if available."""
    line = getattr(obj, "_line_no", None)
    return f"Baris {line}:" if line is not None else ""

def _has_action_required(mapping: ColumnMapping) -> bool:
    """Checks if any field contains 'ACTION_REQUIRED'."""
    marker = "ACTION_REQUIRED"
    fields = [
        mapping.target_column,
        mapping.source_column,
        mapping.cast_target,
        mapping.default_value
    ]
    return any(marker in str(f) for f in fields if f is not None)
