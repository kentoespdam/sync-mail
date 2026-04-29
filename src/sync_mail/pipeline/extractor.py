# src/sync_mail/pipeline/extractor.py

import pymysql
from typing import Dict, Any, List, Generator
from sync_mail.config.schema import MappingDocument
from sync_mail.observability import logger

def extract(
    conn_source: pymysql.connections.Connection,
    mapping: MappingDocument,
    last_pk: Any
) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Extracts data from the source table using keyset pagination and streaming.
    
    Args:
        conn_source: PyMySQL connection to the source database.
        mapping: The mapping configuration.
        last_pk: The last processed primary key value (for resumption).
        
    Yields:
        A list of dictionaries representing a chunk of rows.
    """
    source_table = mapping.source_table
    pk_col = mapping.pk_column
    batch_size = mapping.batch_size
    
    # Get all source columns needed for mapping
    source_columns = []
    for m in mapping.mappings:
        if m.source_column and m.source_column not in source_columns:
            source_columns.append(m.source_column)
    
    # Ensure PK is included in the select if it's not already there
    if pk_col not in source_columns:
        source_columns.append(pk_col)
    
    cols_str = ", ".join(f"`{c}`" for c in source_columns)
    
    current_last_pk = last_pk
    
    while True:
        # Build query for keyset pagination
        # Note: We use string formatting for table and column names (safe if from validated config)
        # and parameters for the variable last_pk value.
        query = f"""
            SELECT {cols_str}
            FROM `{source_table}`
            WHERE `{pk_col}` > %s
            ORDER BY `{pk_col}` ASC
            LIMIT %s
        """
        
        with conn_source.cursor() as cursor:
            logger.debug(f"Extracting batch starting from {pk_col} > {current_last_pk}")
            cursor.execute(query, (current_last_pk, batch_size))
            rows = cursor.fetchall()
            
            if not rows:
                logger.info("Extraction complete: no more rows found.")
                break
            
            yield rows
            
            # Update current_last_pk for next iteration
            current_last_pk = rows[-1][pk_col]
            
            if len(rows) < batch_size:
                logger.info("Extraction complete: reached end of stream.")
                break
