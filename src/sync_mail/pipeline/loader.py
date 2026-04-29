# src/sync_mail/pipeline/loader.py

import pymysql
from typing import List, Tuple
from sync_mail.config.schema import MappingDocument
from sync_mail.errors import BatchFailedError
from sync_mail.db.connection import transaction
from sync_mail.observability import logger

class Loader:
    """
    Handles bulk loading of transformed data into the target table.
    Caches the INSERT statement for performance.
    """
    def __init__(self, mapping: MappingDocument):
        self.mapping = mapping
        self.insert_sql = self._build_insert_sql()
        
    def _build_insert_sql(self) -> str:
        """
        Builds the parameterized INSERT statement once.
        """
        target_table = self.mapping.target_table
        columns = [m.target_column for m in self.mapping.mappings]
        
        cols_str = ", ".join(f"`{c}`" for c in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        sql = f"INSERT INTO `{target_table}` ({cols_str}) VALUES ({placeholders})"
        logger.debug(f"Generated Loader SQL: {sql}")
        return sql

    def load(self, conn_target: pymysql.connections.Connection, transformed_rows: List[Tuple]) -> int:
        """
        Loads a batch of transformed rows into the target database.
        
        Args:
            conn_target: PyMySQL connection to the target database.
            transformed_rows: List of tuples prepared by the transformer.
            
        Returns:
            The number of rows successfully inserted.
            
        Raises:
            BatchFailedError: If the transaction fails.
        """
        if not transformed_rows:
            return 0
            
        try:
            with transaction(conn_target):
                with conn_target.cursor() as cursor:
                    cursor.executemany(self.insert_sql, transformed_rows)
                    count = cursor.rowcount
                    return count
        except Exception as e:
            logger.error(f"Batch load failed: {str(e)}")
            # The transaction context manager handles rollback
            raise BatchFailedError(
                f"Failed to load batch into {self.mapping.target_table}: {str(e)}",
                context={
                    "target_table": self.mapping.target_table,
                    "batch_size": len(transformed_rows),
                    "error": str(e)
                }
            ) from e

def load(conn_target: pymysql.connections.Connection, mapping: MappingDocument, transformed_rows: List[Tuple]) -> int:
    """
    Functional wrapper for Loader.load for cases where a persistent Loader instance isn't used.
    Note: Re-building SQL every time might have slight overhead if called in a tight loop,
    but usually fine per batch.
    """
    loader = Loader(mapping)
    return loader.load(conn_target, transformed_rows)
