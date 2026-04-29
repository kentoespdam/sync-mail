import pymysql
from typing import List, Dict, Any
from sync_mail.errors import IntrospectionError

def describe_table(conn: pymysql.connections.Connection, schema: str, table: str) -> List[Dict[str, Any]]:
    """
    Retrieves column metadata from information_schema.columns.
    
    Args:
        conn: PyMySQL connection object.
        schema: Database name.
        table: Table name.
        
    Returns:
        List of dictionaries containing column metadata, ordered by ORDINAL_POSITION.
    """
    query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_TYPE
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (schema, table))
            columns = cursor.fetchall()
            
            if not columns:
                raise IntrospectionError(
                    f"Table '{schema}.{table}' not found in information_schema.",
                    context={"schema": schema, "table": table}
                )
            
            return columns
    except pymysql.MySQLError as e:
        raise IntrospectionError(
            f"Failed to introspect table '{schema}.{table}': {str(e)}",
            context={"schema": schema, "table": table, "error": str(e)}
        ) from e

def list_tables(conn: pymysql.connections.Connection, schema: str) -> List[str]:
    """
    Retrieves all table names in a schema.
    """
    query = "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'"
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (schema,))
            return [row["TABLE_NAME"] for row in cursor.fetchall()]
    except pymysql.MySQLError as e:
        raise IntrospectionError(
            f"Failed to list tables in schema '{schema}': {str(e)}",
            context={"schema": schema, "error": str(e)}
        ) from e

def get_foreign_keys(conn: pymysql.connections.Connection, schema: str) -> List[Dict[str, str]]:
    """
    Retrieves all foreign key relationships in a schema.
    Returns list of {'table': ..., 'parent_table': ...}
    """
    query = """
        SELECT TABLE_NAME as `table`, REFERENCED_TABLE_NAME as `parent_table`
        FROM information_schema.key_column_usage
        WHERE TABLE_SCHEMA = %s 
          AND REFERENCED_TABLE_NAME IS NOT NULL
          AND TABLE_NAME != REFERENCED_TABLE_NAME
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (schema,))
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise IntrospectionError(
            f"Failed to fetch foreign keys in schema '{schema}': {str(e)}",
            context={"schema": schema, "error": str(e)}
        ) from e
