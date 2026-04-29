from typing import List, Dict, Any
from sync_mail.config.schema import MappingDocument, ColumnMapping
import os
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

def generate_mapping(source_meta: List[Dict[str, Any]], 
                     target_meta: List[Dict[str, Any]], 
                     source_table: str, 
                     target_table: str) -> MappingDocument:
    """
    Generates a MappingDocument based on source and target metadata.
    
    Logic:
    - Identical name & full type -> NONE
    - Identical name & different type -> CAST (with ACTION_REQUIRED)
    - Target only -> INJECT_DEFAULT (with ACTION_REQUIRED)
    - Source only -> Recorded in unmapped_source_columns
    """
    source_cols = {col['COLUMN_NAME']: col for col in source_meta}
    target_cols = target_meta # ORDINAL_POSITION order is preserved
    
    mappings = []
    mapped_source_cols = set()
    
    for t_col in target_cols:
        name = t_col['COLUMN_NAME']
        t_full_type = t_col['COLUMN_TYPE']
        
        if name in source_cols:
            s_col = source_cols[name]
            s_full_type = s_col['COLUMN_TYPE']
            mapped_source_cols.add(name)
            
            if s_full_type == t_full_type:
                mappings.append(ColumnMapping(
                    target_column=name,
                    source_column=name,
                    transformation_type="NONE",
                    _source_type=s_full_type,
                    _target_type=t_full_type
                ))
            else:
                # Type mismatch, e.g. ENUM to VARCHAR
                mappings.append(ColumnMapping(
                    target_column=name,
                    source_column=name,
                    transformation_type="CAST",
                    cast_target=t_full_type,
                    _source_type=s_full_type,
                    _target_type=t_full_type
                ))
        else:
            # Column only in target
            mappings.append(ColumnMapping(
                target_column=name,
                source_column=None,
                transformation_type="INJECT_DEFAULT",
                default_value="ACTION_REQUIRED",
                _target_type=t_full_type
            ))
            
    unmapped_source = [col for col in source_cols if col not in mapped_source_cols]
    
    return MappingDocument(
        source_table=source_table,
        target_table=target_table,
        mappings=mappings,
        unmapped_source_columns=unmapped_source
    )

def save_mapping_to_yaml(doc: MappingDocument, output_dir: str = "mappings") -> str:
    """
    Saves MappingDocument to a YAML file using ruamel.yaml to preserve comments and order.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    filename = f"{doc.source_table}_to_{doc.target_table}.yaml"
    filepath = os.path.join(output_dir, filename)
    
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    
    data = CommentedMap()
    data['source_table'] = doc.source_table
    data['target_table'] = doc.target_table
    data['batch_size'] = doc.batch_size
    
    mappings_list = CommentedSeq()
    for m in doc.mappings:
        m_map = CommentedMap()
        m_map['target_column'] = m.target_column
        m_map['source_column'] = m.source_column
        m_map['transformation_type'] = m.transformation_type
        
        # Add context comment before each mapping
        if m.transformation_type == "NONE":
            m_map.yaml_set_start_comment(f"NONE: {m._source_type}")
        elif m.transformation_type == "CAST":
            m_map['cast_target'] = m.cast_target
            m_map.yaml_set_start_comment(f"CAST: {m._source_type} -> {m._target_type}")
            m_map.yaml_add_eol_comment("ACTION_REQUIRED: verify mapping", key='transformation_type')
        elif m.transformation_type == "INJECT_DEFAULT":
            m_map['default_value'] = m.default_value
            m_map.yaml_set_start_comment(f"INJECT_DEFAULT: target is {m._target_type}")
            m_map.yaml_add_eol_comment("ACTION_REQUIRED: provide value", key='default_value')
            
        mappings_list.append(m_map)
        
    data['mappings'] = mappings_list
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f)
        if doc.unmapped_source_columns:
            f.write("\n# UNMAPPED SOURCE COLUMNS:\n")
            for col in sorted(doc.unmapped_source_columns):
                f.write(f"# - {col}\n")
                
    return filepath
