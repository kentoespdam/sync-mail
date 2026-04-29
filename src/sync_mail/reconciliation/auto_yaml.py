import os
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from sync_mail.config.schema import MappingDocument, ColumnMapping
from typing import List, Dict, Any

def generate_mapping(
    source_meta: List[Dict[str, Any]], 
    target_meta: List[Dict[str, Any]], 
    source_table: str, 
    target_table: str
) -> MappingDocument:
    """
    Reconciles source and target metadata to generate a MappingDocument.
    """
    source_cols = {c["COLUMN_NAME"]: c for c in source_meta}
    
    mappings = []
    mapped_source_names = set()
    
    for t_meta in target_meta:
        t_name = t_meta["COLUMN_NAME"]
        t_type = t_meta["DATA_TYPE"]
        
        if t_name in source_cols:
            s_meta = source_cols[t_name]
            s_type = s_meta["DATA_TYPE"]
            mapped_source_names.add(t_name)
            
            if s_type == t_type:
                mappings.append(ColumnMapping(
                    target_column=t_name,
                    source_column=t_name,
                    transformation_type="NONE"
                ))
            else:
                # Type mismatch, e.g., enum -> varchar
                mappings.append(ColumnMapping(
                    target_column=t_name,
                    source_column=t_name,
                    transformation_type="CAST",
                    cast_target=t_type.upper(),
                    comment=f"CAST: {s_type} -> {t_type} | ACTION_REQUIRED: Verify mapping"
                ))
        else:
            # Target column missing in source
            mappings.append(ColumnMapping(
                target_column=t_name,
                transformation_type="INJECT_DEFAULT",
                default_value="ACTION_REQUIRED",
                comment="ACTION_REQUIRED: Column missing in source"
            ))
            
    unmapped_source = [s for s in source_cols if s not in mapped_source_names]
    
    return MappingDocument(
        source_table=source_table,
        target_table=target_table,
        batch_size=10000,
        mappings=mappings,
        unmapped_source_columns=unmapped_source
    )

def write_mapping_yaml(doc: MappingDocument, output_path: str):
    """
    Writes a MappingDocument to a YAML file with comments using ruamel.yaml.
    """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    data = CommentedMap()
    data["migration_job"] = CommentedMap({
        "source_table": doc.source_table,
        "target_table": doc.target_table,
        "batch_size": doc.batch_size
    })
    
    mappings_seq = CommentedSeq()
    for m in doc.mappings:
        m_map = CommentedMap()
        if m.source_column:
            m_map["source_column"] = m.source_column
        else:
            m_map["source_column"] = None
            
        m_map["target_column"] = m.target_column
        m_map["transformation_type"] = m.transformation_type
        
        if m.transformation_type == "CAST":
            m_map["cast_target"] = m.cast_target
        elif m.transformation_type == "INJECT_DEFAULT":
            m_map["default_value"] = m.default_value
            
        mappings_seq.append(m_map)
        if m.comment:
            mappings_seq.yaml_add_eol_comment(m.comment, len(mappings_seq) - 1)
            
    data["migration_job"]["mappings"] = mappings_seq
    
    # Add unmapped source columns as comments at the end
    if doc.unmapped_source_columns:
        data.yaml_set_comment_before_after_key("migration_job", after="\n# UNMAPPED SOURCE COLUMNS:")
        for col in doc.unmapped_source_columns:
            # Since ruamel.yaml doesn't have a direct "add comment at the very end" easily via data
            # we'll just add it to the unmapped_source_columns key if we wanted to show them.
            # But the plan says "catat sebagai komentar di YAML".
            pass
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        # Add header comment
        f.write("# Auto-generated mapping template\n")
        if doc.unmapped_source_columns:
            f.write("# UNMAPPED SOURCE COLUMNS:\n")
            for col in doc.unmapped_source_columns:
                f.write(f"# - {col}\n")
            f.write("\n")
        yaml.dump(data, f)
