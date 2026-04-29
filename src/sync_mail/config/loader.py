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

    yaml = YAML(typ="safe") # Use safe mode for loading unless round-trip is needed for editing
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.load(f)
    except Exception as e:
        raise MappingError(f"Failed to parse YAML file '{path}': {str(e)}") from e

    if not raw_data or "migration_job" not in raw_data:
        raise MappingError(f"Invalid mapping structure in '{path}': missing 'migration_job' key.")

    job_data = raw_data["migration_job"]
    
    try:
        mappings = []
        for m in job_data.get("mappings", []):
            mappings.append(ColumnMapping(
                target_column=m.get("target_column"),
                transformation_type=m.get("transformation_type", "NONE"),
                source_column=m.get("source_column"),
                cast_target=m.get("cast_target"),
                default_value=m.get("default_value")
            ))
            
        doc = MappingDocument(
            source_table=job_data.get("source_table"),
            target_table=job_data.get("target_table"),
            pk_column=job_data.get("pk_column"),
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
