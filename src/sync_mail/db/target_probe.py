import pymysql
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

@dataclass
class ColumnMetadata:
    name: str
    data_type: str
    is_nullable: bool
    default: Any
    max_length: Optional[int]
    enum_values: Optional[Set[str]]
    column_type: str # Raw COLUMN_TYPE for more detail if needed

def describe_target_columns(conn: pymysql.connections.Connection, schema: str, table: str) -> Dict[str, ColumnMetadata]:
    """
    Retrieves detailed metadata for target columns.
    """
    query = """
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            IS_NULLABLE, 
            COLUMN_DEFAULT, 
            CHARACTER_MAXIMUM_LENGTH,
            COLUMN_TYPE
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query, (schema, table))
        rows = cursor.fetchall()
        
    metadata = {}
    for row in rows:
        name = row["COLUMN_NAME"]
        data_type = row["DATA_TYPE"].upper()
        is_nullable = row["IS_NULLABLE"].upper() == "YES"
        default = row["COLUMN_DEFAULT"]
        max_length = row["CHARACTER_MAXIMUM_LENGTH"]
        column_type = row["COLUMN_TYPE"]
        
        enum_values = None
        if data_type == "ENUM":
            # Extract enum values: enum('a','b','c') -> {'a', 'b', 'c'}
            matches = re.findall(r"'(.*?)'", column_type)
            if matches:
                enum_values = set(matches)
        
        metadata[name] = ColumnMetadata(
            name=name,
            data_type=data_type,
            is_nullable=is_nullable,
            default=default,
            max_length=max_length,
            enum_values=enum_values,
            column_type=column_type
        )
        
    return metadata
