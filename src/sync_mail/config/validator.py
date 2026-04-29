from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.errors import MappingError
from typing import List

def validate_mapping(doc: MappingDocument) -> None:
    """
    Validates a MappingDocument against business and structural rules.
    Collects all errors and raises a single MappingError if any violations are found.
    """
    errors = []

    # (g) Basic metadata
    if not doc.source_table:
        errors.append("Source table name cannot be empty.")
    if not doc.target_table:
        errors.append("Target table name cannot be empty.")

    # (d) batch_size check
    if not (5000 <= doc.batch_size <= 15000):
        errors.append(f"batch_size ({doc.batch_size}) must be between 5,000 and 15,000 as per performance requirements.")

    # (e) Duplicate target_column
    target_columns = [m.target_column for m in doc.mappings]
    duplicates = [c for c in set(target_columns) if target_columns.count(c) > 1]
    if duplicates:
        errors.append(f"Duplicate target columns found: {', '.join(duplicates)}")

    # (f) Check for ACTION_REQUIRED in any non-comment field
    def check_action_required(val, context_msg):
        if isinstance(val, str) and "ACTION_REQUIRED" in val:
            errors.append(f"Placeholder 'ACTION_REQUIRED' remains in {context_msg}.")

    for m in doc.mappings:
        col_ctx = f"column mapping for '{m.target_column}'"
        
        # Check specific fields for placeholders
        check_action_required(m.source_column, f"source_column of {col_ctx}")
        check_action_required(m.cast_target, f"cast_target of {col_ctx}")
        check_action_required(m.default_value, f"default_value of {col_ctx}")
        
        # (a) CAST must have cast_target
        if m.transformation_type == "CAST" and not m.cast_target:
            errors.append(f"Transformation CAST for '{m.target_column}' requires a 'cast_target'.")
            
        # (b) INJECT_DEFAULT must have default_value
        if m.transformation_type == "INJECT_DEFAULT" and m.default_value is None:
            errors.append(f"Transformation INJECT_DEFAULT for '{m.target_column}' requires a 'default_value'.")
            
        # (c) NONE must have source_column
        if m.transformation_type == "NONE" and not m.source_column:
            errors.append(f"Transformation NONE for '{m.target_column}' requires a 'source_column'.")

    if errors:
        error_msg = "Mapping document validation failed:\n" + "\n".join(f"- {e}" for e in errors)
        raise MappingError(error_msg, context={"errors": errors})
