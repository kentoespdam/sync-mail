import os
from ruamel.yaml import YAML
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.config.validator import validate_mapping
from sync_mail.errors import MappingError

def load_mapping(path: str) -> MappingDocument:
    """
    Loads a YAML mapping file, parses it into a MappingDocument, and validates it.
    """
    if not os.path.exists(path):
        raise MappingError(f"Mapping file not found: {path}")

    yaml = YAML(typ="rt") # Use RoundTrip mode to get line numbers
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.load(f)
    except Exception as e:
        raise MappingError(f"Failed to parse YAML file '{path}': {str(e)}") from e

    if not raw_data:
        raise MappingError(f"Mapping file is empty: {path}")

    # Support both nested 'migration_job' and flat structure
    if "migration_job" in raw_data:
        job_data = raw_data["migration_job"]
    else:
        # Fallback to flat structure if source_table is present at root
        if "source_table" in raw_data:
            job_data = raw_data
        else:
            raise MappingError(f"Invalid mapping structure in '{path}': missing 'migration_job' key or 'source_table' at root.")
    
    try:
        mappings = []
        for i, m in enumerate(job_data.get("mappings", [])):
            # Try to get line number from ruamel.yaml metadata
            line_no = None
            if hasattr(job_data.get("mappings"), "lc"):
                line_no = job_data.get("mappings").lc.item(i)[0] + 1
            elif hasattr(m, "lc"):
                line_no = m.lc.line + 1
            
            mappings.append(ColumnMapping(
                target_column=m.get("target_column"),
                transformation_type=m.get("transformation_type", "NONE"),
                source_column=m.get("source_column"),
                cast_target=m.get("cast_target"),
                default_value=m.get("default_value"),
                _line_no=line_no
            ))
            
        doc = MappingDocument(
            source_table=job_data.get("source_table"),
            target_table=job_data.get("target_table"),
            pk_column=job_data.get("pk_column", "id"),
            batch_size=job_data.get("batch_size", 10000),
            mappings=mappings
        )
        
        # Immediate validation
        validate_mapping(doc)
        
        return doc
        
    except MappingError:
        # Re-raise MappingErrors from validator
        raise
    except Exception as e:
        raise MappingError(f"Error populating mapping structure from '{path}': {str(e)}") from e
