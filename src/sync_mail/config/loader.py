import os
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.config.validator import validate
from sync_mail.errors.exceptions import MappingError

def load_mapping(path: str) -> MappingDocument:
    """
    Loads a YAML mapping file into a MappingDocument dataclass and validates it.
    
    Args:
        path: Path to the YAML file.
        
    Returns:
        A validated MappingDocument.
        
    Raises:
        MappingError: If the file is missing, corrupted, or fails validation.
    """
    if not os.path.exists(path):
        raise MappingError(f"Mapping file tidak ditemukan: {path}")
        
    yaml = YAML(typ='rt')
    try:
        with open(path, 'r') as f:
            data = yaml.load(f)
    except YAMLError as e:
        raise MappingError(f"Gagal memparsing file YAML {path}: {str(e)}")
    except Exception as e:
        raise MappingError(f"Terjadi kesalahan saat membaca {path}: {str(e)}")
        
    if not data:
        raise MappingError(f"Mapping file {path} kosong.")

    try:
        doc_line = data.lc.line + 1 if hasattr(data, 'lc') else None
        
        mappings = []
        raw_mappings = data.get('mappings', [])
        
        for i, m_data in enumerate(raw_mappings):
            # Get line number for this mapping element
            # In CommentedSeq, we can check lc for the index
            m_line = None
            if hasattr(raw_mappings, 'lc'):
                m_line = raw_mappings.lc.item(i)[0] + 1
            
            mappings.append(ColumnMapping(
                target_column=m_data.get('target_column'),
                source_column=m_data.get('source_column'),
                transformation_type=m_data.get('transformation_type', 'NONE'),
                cast_target=m_data.get('cast_target'),
                default_value=m_data.get('default_value'),
                _line_no=m_line
            ))
            
        doc = MappingDocument(
            source_table=data.get('source_table'),
            target_table=data.get('target_table'),
            mappings=mappings,
            batch_size=data.get('batch_size', 10000),
            unmapped_source_columns=[], # Optional, usually not in YAML for loading
            _line_no=doc_line
        )
        
        # Validate before returning
        validate(doc)
        
        return doc
        
    except Exception as e:
        if isinstance(e, MappingError):
            raise e
        raise MappingError(f"Gagal memproses struktur mapping di {path}: {str(e)}")
