# src/sync_mail/introspection.py

# from sqlalchemy import inspect, text # removed text as it's not used in this snippet but might be needed elsewhere. Keep it for now if used below.
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from typing import Dict, Any, List, Tuple
from ruamel.yaml import YAML

from sync_mail.db.connection import create_db_engine
from sync_mail.errors import IntrospectionError
from sync_mail.observability import event_bus, EventType

def get_table_schema(engine: Engine, table_name: str) -> Dict[str, Any]:
    """
    Retrieves schema information for a specific table.

    Args:
        engine (Engine): The SQLAlchemy engine connected to the database.
        table_name (str): The name of the table to inspect.

    Returns:
        Dict[str, Any]: A dictionary representing the table's schema,
                        including columns, types, and constraints.
    
    Raises:
        IntrospectionError: If introspection fails for the given table.
    """
    try:
        with engine.connect() as connection:
            inspector = inspect(engine)
            
            # Get column information
            columns = []
            for col_info in inspector.get_columns(table_name):
                column_data = {
                    "name": col_info["name"],
                    "type": str(col_info["type"]), # Convert SQLAlchemy type to string representation
                    "nullable": col_info["nullable"],
                    "default": col_info["default"],
                    "primary_key": col_info.get("primary_key", False),
                    "autoincrement": col_info.get("autoincrement", False)
                }
                # Add unique constraint info if available
                if col_info.get("unique"):
                    column_data["unique"] = col_info["unique"]
                columns.append(column_data)

            # Get primary key constraint details
            pk_constraint = inspector.get_pk_constraint(table_name)
            primary_key_columns = pk_constraint.get("constrained_columns", [])

            # Get unique constraints
            unique_constraints = []
            for uc in inspector.get_unique_constraints(table_name):
                unique_constraints.append({
                    "name": uc.get("name"),
                    "columns": uc.get("column_names", [])
                })

            # Get foreign key constraints
            foreign_keys = []
            for fk in inspector.get_foreign_keys(table_name):
                foreign_keys.append({
                    "name": fk.get("name"),
                    "local_columns": fk.get("local_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", [])
                })
                
            schema_info = {
                "columns": columns,
                "primary_key": primary_key_columns,
                "unique_constraints": unique_constraints,
                "foreign_keys": foreign_keys
            }
            
            event_bus.publish(
                event_bus.Event(
                    event_type=EventType.JOB_STARTED, # Using a generic event for now
                    payload={"message": f"Schema introspection for table '{table_name}' completed."}
                )
            )
            return schema_info

    except Exception as e:
        error_message = f"Failed to introspect schema for table '{table_name}': {e}"
        event_bus.publish(
            event_bus.Event(
                event_type=EventType.JOB_ABORTED, # Indicate failure
                payload={"error": error_message, "table_name": table_name}
            )
        )
        raise IntrospectionError(error_message, context={"table_name": table_name, "exception": str(e)}) from e

def get_all_table_schemas(engine: Engine, schema_name: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves schema information for all tables in a given schema.

    Args:
        engine (Engine): The SQLAlchemy engine connected to the database.
        schema_name (str, optional): The name of the schema to inspect. If None,
                                     the default schema associated with the connection is used.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where keys are table names and values
                                   are their schema information dictionaries.

    Raises:
        IntrospectionError: If introspection fails for any table or the schema.
    """
    all_schemas = {}
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names(schema=schema_name)
        
        for table_name in table_names:
            all_schemas[table_name] = get_table_schema(engine, table_name)
        
        event_bus.publish(
            event_bus.Event(
                event_type=EventType.JOB_STARTED, # Generic event type for now
                payload={"message": f"Successfully introspected schemas for {len(table_names)} tables."}
            )
        )
        return all_schemas

    except Exception as e:
        error_message = f"Failed to introspect all table schemas for schema '{schema_name or 'default'}': {e}"
        event_bus.publish(
            event_bus.Event(
                event_type=EventType.JOB_ABORTED, # Indicate failure
                payload={"error": error_message, "schema_name": schema_name}
            )
        )
        raise IntrospectionError(error_message, context={"schema_name": schema_name, "exception": str(e)}) from e

def map_sqlalchemy_type_to_yaml(sqlalchemy_type: str) -> str:
    """
    Maps SQLAlchemy type string representations to a simplified YAML type string.
    This is a simplified mapping and might need expansion based on project needs.
    """
    # Convert to lowercase for easier matching
    type_str = str(sqlalchemy_type).lower()

    if "varchar" in type_str or "text" in type_str:
        return "string"
    elif "int" in type_str:
        return "integer"
    elif "float" in type_str or "double" in type_str or "real" in type_str:
        return "float"
    elif "decimal" in type_str or "numeric" in type_str:
        return "decimal"
    elif "date" in type_str or "time" in type_str or "timestamp" in type_str:
        return "datetime"
    elif "bool" in type_str:
        return "boolean"
    elif "binary" in type_str or "blob" in type_str:
        return "binary"
    else:
        return "unknown" # Default for unhandled types

def convert_schema_to_yaml(all_schemas: Dict[str, Dict[str, Any]], schema_name: str = None) -> str:
    """
    Converts introspected schema information into a YAML string format using ruamel.yaml.

    Args:
        all_schemas (Dict[str, Dict[str, Any]]): The dictionary of schema information
                                                 obtained from get_all_table_schemas.
        schema_name (str, optional): The name of the schema for context in the YAML output.

    Returns:
        str: A YAML formatted string representing the schemas.
    
    Raises:
        IntrospectionError: If there's an issue during YAML conversion.
    """
    yaml_data = {
        "schema": schema_name if schema_name else "default",
        "tables": []
    }

    try:
        for table_name, schema_info in all_schemas.items():
            table_yaml_entry = {
                "name": table_name,
                "columns": [],
                "primary_key": schema_info.get("primary_key", []),
                "unique_constraints": schema_info.get("unique_constraints", []),
                "foreign_keys": schema_info.get("foreign_keys", [])
            }

            for col in schema_info.get("columns", []):
                mapped_type = map_sqlalchemy_type_to_yaml(col.get("type", "unknown"))
                column_entry = {
                    "name": col.get("name", "unnamed_column"),
                    "type": mapped_type,
                    "nullable": col.get("nullable", True),
                    "default": col.get("default"),
                    "primary_key": col.get("primary_key", False),
                    "autoincrement": col.get("autoincrement", False),
                }
                # Only include 'unique' if it's True, to keep YAML clean
                if col.get("unique") is True:
                    column_entry["unique"] = True
                
                table_yaml_entry["columns"].append(column_entry)
            
            yaml_data["tables"].append(table_yaml_entry)

        # Use ruamel.yaml for generation, ensuring it's installed and imported.
        yaml_handler = YAML()
        yaml_handler.indent(mapping=2, sequence=4, offset=2) # Configure indentation for readability
        yaml_handler.width = 4096 # Prevent line wrapping for YAML output

        # Use a string stream to capture the YAML output
        from io import StringIO
        string_stream = StringIO()
        yaml_handler.dump(yaml_data, string_stream)
        yaml_output = string_stream.getvalue()

        event_bus.publish(
            event_bus.Event(
                event_type=EventType.JOB_STARTED, # Generic event
                payload={"message": "Schema data successfully converted to YAML format."}
            )
        )
        return yaml_output

    except Exception as e:
        error_message = f"Failed to convert schema information to YAML: {e}"
        event_bus.publish(
            event_bus.Event(
                event_type=EventType.JOB_ABORTED,
                payload={"error": error_message, "context": "YAML Conversion"}
            )
        )
        raise IntrospectionError(error_message, context={"exception": str(e)}) from e
