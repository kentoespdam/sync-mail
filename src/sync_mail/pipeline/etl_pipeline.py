# src/sync_mail/pipeline/etl_pipeline.py

import logging
from typing import Dict, Any, Generator, Optional, List
from sqlalchemy import text, inspect, insert, table, column
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError

from sync_mail.db.connection import create_db_engine
from sync_mail.errors import MigrationError, MappingError, ConnectionError, IntrospectionError, ResumeError, BatchFailedError
from sync_mail.mapping import MappingConfigLoader
from sync_mail.state import MigrationState
from sync_mail.observability import event_bus, Event, EventType

# Get a logger instance for this module
logger = logging.getLogger(__name__)

class ETLPipeline:
    """
    Orchestrates the Extract, Transform, Load (ETL) process for data migration.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the ETL pipeline with configuration.

        Args:
            config (Dict[str, Any]): A dictionary containing all necessary configuration,
                                     including 'db_source', 'db_target', 'mapping_path',
                                     'state_file', 'schema_name', etc.
        """
        self.config = config
        self.db_source_engine: Optional[Engine] = None
        self.db_target_engine: Optional[Engine] = None
        self.state_manager: Optional[MigrationState] = None
        self.mapping_config: Optional[Dict[str, Any]] = None
        self.schema_name: Optional[str] = config.get("schema_name") # Target schema for introspection/mapping

        # Initialize components lazily or based on config
        self._initialize_components()

    def _initialize_components(self):
        """
        Initializes the necessary components based on the pipeline configuration.
        This includes database engines, state manager, and mapping configuration.
        """
        try:
            # Initialize State Manager
            state_file = self.config.get("state_file", "state.json")
            self.state_manager = MigrationState(state_file_path=state_file)
            self.state_manager.load_state()

            # Initialize Database Engines
            source_db_config = self.config.get("db_source")
            if not source_db_config:
                raise MigrationError("Source database configuration ('db_source') is missing.")
            self.db_source_engine = create_db_engine(source_db_config)

            target_db_config = self.config.get("db_target")
            if not target_db_config:
                raise MigrationError("Target database configuration ('db_target') is missing.")
            self.db_target_engine = create_db_engine(target_db_config)

            # Initialize Mapping Configuration Loader
            mapping_path = self.config.get("mapping_path")
            if not mapping_path:
                raise MigrationError("Mapping configuration path ('mapping_path') is missing.")
            mapping_loader = MappingConfigLoader(mapping_path)
            self.mapping_config = mapping_loader.load_mapping()

            logger.info("ETL pipeline components initialized.")

        except (MigrationError, ConnectionError, MappingError, ResumeError) as e:
            logger.error(f"Failed to initialize ETL pipeline: {e}")
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": str(e), "component": "ETL Pipeline Initialization"}
                )
            )
            raise  # Re-raise the caught exception
        except Exception as e:
            error_message = f"An unexpected error occurred during pipeline initialization: {e}"
            logger.exception(error_message) # Log with traceback
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "component": "ETL Pipeline Initialization"}
                )
            )
            raise MigrationError(error_message, context={"exception": str(e)}) from e

    def _get_pk_column_name(self, table_name: str) -> Optional[str]:
        """Helper to find the primary key column name for a table from mapping."""
        if not self.mapping_config or not self.mapping_config.get("tables"):
            return None

        for table_map in self.mapping_config["tables"]:
            if table_map.get("name") == table_name:
                pk_columns = table_map.get("primary_key")
                if pk_columns and isinstance(pk_columns, list) and len(pk_columns) > 0:
                    return pk_columns[0] # Assume the first PK column is used for ordering/resuming
        logger.warning(f"Primary key column not found in mapping for table '{table_name}'. Resuming might be inaccurate.")
        return None

    def _extract_data(self, source_conn: Connection, table_name: str, table_map_def: Dict[str, Any], last_pk: Any = None) -> Generator[Dict[str, Any], None, None]:
        """
        Extracts data from the source table, using server-side cursors and yielding rows.
        Fetches data starting from the 'last_pk' if provided.
        """
        pk_column_name = self._get_pk_column_name(table_name)
        
        query_parts = [f"SELECT * FROM {table_name}"]
        query_params = {}

        if last_pk is not None and pk_column_name:
            query_parts.append(f"WHERE {pk_column_name} > :last_pk")
            query_params["last_pk"] = last_pk
        
        if pk_column_name:
            query_parts.append(f"ORDER BY {pk_column_name}")
        else:
            # If no PK, ordering is not guaranteed for resumption. Log a warning.
            logger.warning(f"No PK column defined for table '{table_name}'. Data extraction order may not be deterministic for resuming.")

        query = " ".join(query_parts)
        
        logger.info(f"Executing extraction query: '{query}' with params {query_params}" + (f" for table '{table_name}'" if table_name else ""))
        
        try:
            # Using server-side cursors via SSDictCursor is configured in create_db_engine.
            # SQLAlchemy's `stream_results=True` can also be used for explicit streaming,
            # but SSDictCursor typically implies server-side processing.
            # We pass execution options to ensure streaming behavior.
            result_proxy = source_conn.execution_options(stream_results=True).execute(text(query), query_params)
            
            row_count = 0
            # Fetch rows using mappings() which returns dict-like rows
            for row in result_proxy.mappings(): 
                yield row
                row_count += 1
                # Periodically update state while extracting if yielding a large number of rows
                # For simplicity, state is updated after batch loading, but could be done here too.

            logger.info(f"Finished data extraction for table '{table_name}'. Yielded {row_count} rows.")

        except SQLAlchemyError as e:
            error_message = f"Database error during data extraction for table '{table_name}': {e}"
            logger.error(error_message)
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "table_name": table_name, "last_pk": last_pk}
                )
            )
            raise IntrospectionError(error_message, context={"table_name": table_name, "last_pk": last_pk, "sqlalchemy_error": str(e)}) from e
        except Exception as e:
            error_message = f"An unexpected error occurred during data extraction for table '{table_name}': {e}"
            logger.exception(error_message) # Log with traceback
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "table_name": table_name, "last_pk": last_pk}
                )
            )
            raise IntrospectionError(error_message, context={"table_name": table_name, "last_pk": last_pk, "exception": str(e)}) from e


    def _transform_row(self, row: Dict[str, Any], table_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a single row based on the provided table mapping rules.
        """
        transformed_row = {}
        
        columns_in_mapping = table_mapping.get("columns", [])
        if not columns_in_mapping:
            logger.warning(f"No column definitions found in mapping for table '{table_mapping.get('name')}'. Returning original row data for columns present in mapping's table definition.")
            # Fallback: try to pass through columns that exist in the target table (handled in _load_data)
            return row # Return original row, relying on target schema/SQLAlchemy

        for col_definition in columns_in_mapping:
            col_name = col_definition.get("name")
            if not col_name:
                logger.warning(f"Skipping column definition without a name in mapping for table '{table_mapping.get('name')}'.")
                continue
            
            # Get value from source row if available
            if col_name in row:
                transformed_row[col_name] = row[col_name]
            
            # Use default value from mapping if column is not in source row and default is specified
            elif "default" in col_definition:
                transformed_row[col_name] = col_definition["default"]
                
            # If column is required by mapping but not in row and no default, it might be an issue.
            # This simple implementation relies on the _load_data filtering step.

        return transformed_row

    def _load_data(self, target_conn: Connection, table_name: str, transformed_rows: List[Dict[str, Any]], target_table_columns: List[Dict[str, Any]]):
        """
        Loads a batch of transformed rows into the target table using SQLAlchemy Core's insert construct.
        """
        if not transformed_rows:
            return 0 # No rows to load

        try:
            # Filter transformed_rows to only include columns that exist in the target table metadata.
            valid_columns_for_insert = {tc['name'] for tc in target_table_columns}
            
            final_rows_for_insert = []
            for row_data in transformed_rows:
                filtered_row = {k: v for k, v in row_data.items() if k in valid_columns_for_insert}
                if filtered_row: # Only add if there are valid columns after filtering
                    final_rows_for_insert.append(filtered_row)
            
            if not final_rows_for_insert:
                logger.warning(f"No valid columns found for insertion into table '{table_name}' after filtering. Batch skipped.")
                return 0

            # Dynamically create table object from metadata
            target_table = table(table_name, *(column(tc['name']) for tc in target_table_columns))
            
            # Execute bulk insert
            result = target_conn.execute(insert(target_table), final_rows_for_insert)
            
            num_rows_loaded = result.rowcount if result.rowcount != -1 else len(final_rows_for_insert)
            logger.info(f"Loaded {num_rows_loaded} rows into table '{table_name}'.")
            return num_rows_loaded
            
        except SQLAlchemyError as e:
            # Attempt to rollback the transaction for this batch if an error occurs
            try:
                target_conn.rollback()
            except Exception as rb_e:
                logger.error(f"Error during transaction rollback for '{table_name}': {rb_e}")
            
            raise BatchFailedError(f"Failed to load batch into table '{table_name}': {e}", context={"table_name": table_name, "rows_attempted": len(transformed_rows)}) from e
        except Exception as e:
            # Attempt to rollback on any other unexpected errors
            try:
                target_conn.rollback()
            except Exception as rb_e:
                logger.error(f"Error during transaction rollback for '{table_name}': {rb_e}")

            raise BatchFailedError(f"An unexpected error occurred during data loading into '{table_name}': {e}", context={"table_name": table_name, "rows_attempted": len(transformed_rows)}) from e

    def run_migration(self):
        """
        Executes the full migration process: Extract, Transform, Load for all tables.
        """
        if not self.db_source_engine or not self.db_target_engine or not self.state_manager or not self.mapping_config:
            raise MigrationError("Pipeline components not initialized properly.")

        logger.info("Starting data migration process.")
        event_bus.publish(
            Event(
                event_type=EventType.JOB_STARTED,
                payload={"message": "ETL pipeline initiated."}
            )
        )

        try:
            tables_to_migrate = [
                table_map.get("name") for table_map in self.mapping_config.get("tables", [])
                if table_map.get("name")
            ]
            
            if not tables_to_migrate:
                logger.warning("No tables found in mapping configuration. Nothing to migrate.")
                event_bus.publish(
                    Event(
                        event_type=EventType.JOB_COMPLETED,
                        payload={"message": "No tables to migrate as per mapping configuration."}
                    )
                )
                return

            # Fetch target table metadata once
            target_inspector = inspect(self.db_target_engine)
            target_tables_metadata: Dict[str, List[Dict[str, Any]]] = {}
            for table_name in tables_to_migrate:
                try:
                    table_cols = []
                    for col_info in target_inspector.get_columns(table_name):
                        table_cols.append({
                            "name": col_info["name"],
                            "type": str(col_info["type"])
                        })
                    target_tables_metadata[table_name] = table_cols
                except Exception as e:
                    raise IntrospectionError(f"Could not reflect columns for target table '{table_name}': {e}", context={"table_name": table_name}) from e

            table_mapping_definitions = {
                table_map.get("name"): table_map for table_map in self.mapping_config.get("tables", [])
                if table_map.get("name")
            }

            for table_name in tables_to_migrate:
                table_map_def = table_mapping_definitions.get(table_name)
                if not table_map_def:
                    logger.warning(f"Mapping definition not found for table '{table_name}'. Skipping.")
                    continue

                last_pk = self.state_manager.get_state_value(f"{table_name}_last_pk")
                pk_column_name = self._get_pk_column_name(table_name) # Get PK column name for state updates
                
                logger.info(f"Processing table: '{table_name}'" + (f" starting from PK: {last_pk}" if last_pk is not None else ""))
                event_bus.publish(
                    Event(
                        event_type=EventType.JOB_STARTED,
                        payload={"message": f"Processing table '{table_name}'", "table_name": table_name, "last_pk": last_pk}
                    )
                )

                batch_rows: List[Dict[str, Any]] = []
                batch_size = 1000 # Configurable batch size

                with self.db_source_engine.connect() as source_conn:
                    extraction_generator = self._extract_data(source_conn, table_name, table_map_def, last_pk)

                    for row in extraction_generator:
                        transformed_row = self._transform_row(row, table_map_def)
                        
                        target_cols_for_table = target_tables_metadata.get(table_name)
                        if not target_cols_for_table:
                            logger.error(f"Metadata for target table '{table_name}' not found. Cannot filter columns. Skipping row.")
                            continue

                        filtered_transformed_row = {}
                        for col_name, value in transformed_row.items():
                            if any(tc['name'] == col_name for tc in target_cols_for_table):
                                filtered_transformed_row[col_name] = value
                            else:
                                logger.warning(f"Column '{col_name}' from source/mapping not found in target table '{table_name}'. Skipping.")
                        
                        if not filtered_transformed_row:
                            logger.warning(f"No valid columns for insertion found in transformed row for table '{table_name}'. Row skipped.")
                            continue

                        batch_rows.append(filtered_transformed_row)

                        if len(batch_rows) >= batch_size:
                            with self.db_target_engine.connect() as target_conn:
                                try:
                                    with target_conn.begin() as transaction:
                                        loaded_count = self._load_data(target_conn, table_name, batch_rows, target_cols_for_table)
                                        
                                        current_row_pk = row.get(pk_column_name) if pk_column_name else None
                                        if current_row_pk is not None:
                                            self.state_manager.update_state(f"{table_name}_last_pk", current_row_pk)
                                        
                                        event_bus.publish(
                                            Event(
                                                event_type=EventType.BATCH_COMMITTED,
                                                payload={"table_name": table_name, "rows_loaded": loaded_count, "last_pk_processed": current_row_pk}
                                            )
                                        )
                                        
                                        self.state_manager.save_state()
                                        batch_rows = []
                                except BatchFailedError as bfe:
                                    logger.error(f"Batch failed for table {table_name}. Aborting migration for this table. Error: {bfe}")
                                    event_bus.publish(
                                        Event(
                                            event_type=EventType.BATCH_FAILED,
                                            payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(bfe)}
                                        )
                                    )
                                    transaction.rollback()
                                    break 
                                except SQLAlchemyError as sae:
                                    logger.error(f"Database error during batch load for table {table_name}: {sae}")
                                    event_bus.publish(
                                        Event(
                                            event_type=EventType.BATCH_FAILED,
                                            payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(sae)}
                                        )
                                    )
                                    transaction.rollback()
                                    break
                                except Exception as e: # Catch any other unexpected errors during batch load
                                    logger.exception(f"Unexpected error during batch load for table {table_name}: {e}")
                                    event_bus.publish(
                                        Event(
                                            event_type=EventType.BATCH_FAILED,
                                            payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(e)}
                                        )
                                    )
                                    transaction.rollback()
                                    break


                    if batch_rows: # Process any remaining rows in the last batch
                        with self.db_target_engine.connect() as target_conn:
                            try:
                                with target_conn.begin() as transaction:
                                    loaded_count = self._load_data(target_conn, table_name, batch_rows, target_cols_for_table)
                                    
                                    current_row_pk = row.get(pk_column_name) if pk_column_name else None
                                    if current_row_pk is not None:
                                        self.state_manager.update_state(f"{table_name}_last_pk", current_row_pk)
                                    
                                    event_bus.publish(
                                        Event(
                                            event_type=EventType.BATCH_COMMITTED,
                                            payload={"table_name": table_name, "rows_loaded": loaded_count, "last_pk_processed": current_row_pk}
                                        )
                                    )
                                    self.state_manager.save_state() # Save state after final batch
                                    batch_rows = []
                            except BatchFailedError as bfe:
                                logger.error(f"Final batch failed for table {table_name}. Error: {bfe}")
                                event_bus.publish(
                                    Event(
                                        event_type=EventType.BATCH_FAILED,
                                        payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(bfe)}
                                    )
                                )
                                transaction.rollback()
                            except SQLAlchemyError as sae:
                                logger.error(f"Database error during final batch load for table {table_name}: {sae}")
                                event_bus.publish(
                                    Event(
                                        event_type=EventType.BATCH_FAILED,
                                        payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(sae)}
                                    )
                                )
                                transaction.rollback()
                            except Exception as e: # Catch any other unexpected errors during final batch load
                                logger.exception(f"Unexpected error during final batch load for table {table_name}: {e}")
                                event_bus.publish(
                                    Event(
                                        event_type=EventType.BATCH_FAILED,
                                        payload={"table_name": table_name, "last_pk_processed": row.get(pk_column_name), "error": str(e)}
                                    )
                                )
                                transaction.rollback()


            logger.info("Data migration process completed.")
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_COMPLETED,
                    payload={"message": "ETL pipeline finished successfully."}
                )
            )

        except MigrationError as me:
            logger.error(f"Migration process aborted due to error: {me}")
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": str(me), "migration_error": True}
                )
            )
            raise
        except Exception as e:
            error_message = f"An unhandled error occurred during the migration process: {e}"
            logger.exception(error_message) # Log with traceback
            event_bus.publish(
                Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "unhandled_error": True}
                )
            )
            raise MigrationError(error_message, context={"exception": str(e)}) from e

