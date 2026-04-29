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
                    cast_target=t_meta["COLUMN_TYPE"],
                    comment=f"CAST: {s_meta['COLUMN_TYPE']} -> {t_meta['COLUMN_TYPE']} | ACTION_REQUIRED: Verify mapping"
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
    
    # Try to find PK (look for auto_increment in source)
    pk_column = "id" # default
    for s in source_meta:
        if "auto_increment" in s.get("EXTRA", "").lower():
            pk_column = s["COLUMN_NAME"]
            break
    else:
        if source_meta:
            pk_column = source_meta[0]["COLUMN_NAME"]

    return MappingDocument(
        source_table=source_table,
        target_table=target_table,
        pk_column=pk_column,
        batch_size=10000,
        mappings=mappings,
        unmapped_source_columns=unmapped_source
    )

def save_mapping_to_yaml(doc: MappingDocument, output_dir: str = "mappings") -> str:
    """
    Writes a MappingDocument to a YAML file with comments using ruamel.yaml.
    Returns the path to the generated file.
    """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    data = CommentedMap()
    data["migration_job"] = CommentedMap({
        "source_table": doc.source_table,
        "target_table": doc.target_table,
        "pk_column": doc.pk_column,
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
        
        # Add comment for CAST/INJECT or generic action required
        comment = m.comment
        if not comment:
            if m.transformation_type == "CAST":
                comment = f"CAST: {getattr(m, '_source_type', '?')} -> {getattr(m, '_target_type', '?')} | ACTION_REQUIRED: verify mapping"
            elif m.transformation_type == "INJECT_DEFAULT":
                comment = "ACTION_REQUIRED: verify default value"
        
        if comment:
            mappings_seq.yaml_add_eol_comment(comment, len(mappings_seq) - 1)
            
    data["migration_job"]["mappings"] = mappings_seq
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{doc.source_table}_to_{doc.target_table}.yaml")
    
    with open(output_path, "w") as f:
        # Add header comment
        f.write("# Auto-generated mapping template\n")
        if doc.unmapped_source_columns:
            f.write("# UNMAPPED SOURCE COLUMNS:\n")
            for col in doc.unmapped_source_columns:
                f.write(f"# - {col}\n")
            f.write("\n")
        yaml.dump(data, f)
        
    return output_path

def sort_tables_by_dependencies(tables: List[str], foreign_keys: List[Dict[str, str]]) -> List[str]:
    """
    Performs topological sort on tables based on foreign key relationships.
    """
    try:
        from graphlib import TopologicalSorter
    except ImportError:
        # Fallback for Python < 3.9 (though project says >= 3.14)
        return sorted(tables)

    ts = TopologicalSorter()
    table_set = set(tables)
    
    # Initialize all tables in the graph
    for t in tables:
        ts.add(t)
        
    # Add dependencies
    for fk in foreign_keys:
        child = fk["table"]
        parent = fk["parent_table"]
        if child in table_set and parent in table_set:
            ts.add(child, parent)
            
    try:
        return list(ts.static_order())
    except Exception:
        # Circular dependency fallback
        return sorted(tables)

def generate_mappings_for_schema(
    source_conn, 
    target_conn, 
    source_db: str, 
    target_db: str,
    output_dir: str = "mappings"
) -> List[str]:
    """
    Generates mapping files for all tables in the source schema.
    Returns list of generated file paths in topological order.
    """
    from sync_mail.db.introspect import list_tables, describe_table, get_foreign_keys
    
    s_tables = list_tables(source_conn, source_db)
    t_tables = list_tables(target_conn, target_db)
    t_set = set(t_tables)
    
    # Only process tables that exist in both
    common_tables = [t for t in s_tables if t in t_set]
    
    # Get FKs from target (where we enforce constraints)
    fks = get_foreign_keys(target_conn, target_db)
    
    sorted_tables = sort_tables_by_dependencies(common_tables, fks)
    
    generated_paths = []
    for table in sorted_tables:
        source_meta = describe_table(source_conn, source_db, table)
        target_meta = describe_table(target_conn, target_db, table)
        
        doc = generate_mapping(source_meta, target_meta, table, table)
        path = save_mapping_to_yaml(doc, output_dir=output_dir)
        generated_paths.append(path)
        
    return generated_paths
