from typing import List, Dict, Any
import pymysql
from sync_mail.errors import IntrospectionError

def describe_table(conn: pymysql.connections.Connection, schema: str, table: str) -> List[Dict[str, Any]]:
    """
    Introspects a table and returns its column metadata from information_schema.
    
    Args:
        conn: A PyMySQL connection (should be using SSDictCursor for consistency).
        schema: The database name/schema.
        table: The table name.
        
    Returns:
        List[Dict[str, Any]]: List of column metadata dictionaries.
        
    Raises:
        IntrospectionError: If table not found or query fails.
    """
    query = """
    SELECT 
        COLUMN_NAME, 
        DATA_TYPE, 
        COLUMN_TYPE,
        IS_NULLABLE, 
        COLUMN_DEFAULT, 
        EXTRA,
        ORDINAL_POSITION
    FROM information_schema.columns
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ORDINAL_POSITION
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (schema, table))
            # SSDictCursor returns a generator-like object, but fetchall() works.
            # However, for large results fetchall() on SSDictCursor might be memory intensive 
            # if we don't need it. But here we expect a small number of columns.
            columns = list(cursor.fetchall())
            
            if not columns:
                raise IntrospectionError(
                    f"Table '{table}' not found in schema '{schema}'.",
                    context={"schema": schema, "table": table}
                )
            
            return columns
    except pymysql.MySQLError as e:
        raise IntrospectionError(
            f"Failed to introspect table '{table}': {str(e)}",
            context={"schema": schema, "table": table, "error": str(e)}
        ) from e
