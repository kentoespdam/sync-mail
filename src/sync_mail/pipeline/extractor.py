# src/sync_mail/pipeline/extractor.py

import pymysql
from typing import Dict, Any, List, Generator
from sync_mail.config.schema import MappingDocument
from sync_mail.observability import logger

def extract(
    conn_source: pymysql.connections.Connection,
    mapping: MappingDocument,
    last_pk: Any,
    limit_override: Optional[int] = None
) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Extracts data from the source table using keyset pagination and streaming.
    
    Args:
        conn_source: PyMySQL connection to the source database.
        mapping: The mapping configuration.
        last_pk: The last processed primary key value (for resumption).
        limit_override: If provided, total rows extracted will not exceed this limit.
        
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
    total_yielded = 0
    
    while True:
        # Determine current batch size
        current_batch_size = batch_size
        if limit_override is not None:
            remaining = limit_override - total_yielded
            if remaining <= 0:
                break
            current_batch_size = min(batch_size, remaining)

        # Build query for keyset pagination
        query = f"""
            SELECT {cols_str}
            FROM `{source_table}`
            WHERE `{pk_col}` > %s
            ORDER BY `{pk_col}` ASC
            LIMIT %s
        """
        
        with conn_source.cursor() as cursor:
            logger.debug(f"Extracting batch starting from {pk_col} > {current_last_pk}")
            cursor.execute(query, (current_last_pk, current_batch_size))
            rows = cursor.fetchall()
            
            if not rows:
                logger.info("Extraction complete: no more rows found.")
                break
            
            yield rows
            total_yielded += len(rows)
            
            # Update current_last_pk for next iteration
            current_last_pk = rows[-1][pk_col]
            
            if len(rows) < current_batch_size or (limit_override and total_yielded >= limit_override):
                logger.info(f"Extraction complete: yielded {total_yielded} rows.")
                break

from typing import Optional
