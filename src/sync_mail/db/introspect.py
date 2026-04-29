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
