# Graph Report - sync-mail  (2026-04-30)

## Corpus Check
- 60 files · ~54,321 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 541 nodes · 999 edges · 65 communities detected
- Extraction: 51% EXTRACTED · 49% INFERRED · 0% AMBIGUOUS · INFERRED: 492 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]

## God Nodes (most connected - your core abstractions)
1. `MappingDocument` - 45 edges
2. `ColumnMapping` - 34 edges
3. `SyncMailApp` - 33 edges
4. `Event` - 27 edges
5. `DryRunScreen` - 26 edges
6. `Checkpoint` - 24 edges
7. `MigrateScreen` - 24 edges
8. `DryRunEngine` - 23 edges
9. `MappingConfigLoader` - 22 edges
10. `ConnectionScreen` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Main entry point for the sync-mail CLI application.     Launches the Textual TUI` --uses--> `SyncMailApp`  [INFERRED]
  main.py → src/sync_mail/tui/app.py
- `MappingConfigLoader` --uses--> `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Initializes the ETL pipeline with configuration.          Args:             conf`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Initializes the necessary components based on the pipeline configuration.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Helper to find the primary key column name for a table from mapping.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (42): EventType, Types of events that can be published to the EventBus., compute_eta(), Records a completed batch., Calculates rows per second based on the sliding window., Calculates rows per second since the start of the job., Computes Estimated Time of Arrival based on remaining rows and throughput., Calculates moving average throughput (rows/sec).     Uses a sliding window of re (+34 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (43): App, BaseNavigationScreen, Message, Screen, BaseNavigationScreen, Return a snapshot of current input values., Load input values from snapshot., Base class for screens with back navigation and state retention. (+35 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (32): DataTable, ColumnMetadata, describe_target_columns(), Retrieves detailed metadata for target columns., Enum, Anomaly, AnomalyCategory, AnomalySeverity (+24 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (44): create_db_engine(), Creates a SQLAlchemy engine for introspection with low-memory settings., get_foreign_keys(), Retrieves all foreign key relationships in a schema.     Returns list of {'table, BatchFailedError, ConfigError, ConnectionError, IntrospectionError (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (38): Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, Root configuration for a migration job between two tables., Metadata for a single column mapping., Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'., Validates a MappingDocument for semantic correctness.     Raises MappingError wi (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (18): describe_table(), list_tables(), Retrieves all table names in a schema., Introspects a table and returns its column metadata from information_schema., generate_mapping(), generate_mappings_for_schema(), Reconciles source and target metadata to generate a MappingDocument., Performs topological sort on tables based on foreign key relationships. (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (11): _check_gitignore(), _load_from_yaml(), Checks if the connection file is in .gitignore and warns if not., Resolves database connection configuration from YAML or interactive input.     F, Loads YAML and returns (data, status_string), Temporarily disables stdout logging handler., resolve_connection_config(), silence_stdout() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (3): HTMLReportGenerator, JobReportData, reporter()

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (10): EventBus, A thread-safe event bus for communication between worker threads and the UI., Internal loop to process and dispatch events from the queue., Starts the background dispatch thread., Stops the background dispatch thread., Subscribes a callback handler to receive events., configure_logging(), ContextFormatter (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (11): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager for database connection lifecycle., Context manager for atomic transactions.     Ensures BEGIN is sent at start, COM, transaction(), Loads a batch of transformed rows into the target database.                  Arg, test_connect_failure_wraps_exception() (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.42
Nodes (10): load_mapping(), Loads a YAML mapping file, parses it into a MappingDocument, and validates it., temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size() (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.28
Nodes (2): BatchProgress, Overall progress for a batch of jobs.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Screen for inspecting state files.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Screen for database introspection and mapping generation.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): A minimal event bus for inter-module communication, especially between worker th

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.         Events are added to an internal queue to

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Internal loop to process and dispatch events from the queue.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Starts the background dispatch thread.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Stops the background dispatch thread.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Subscribes a callback handler to receive events.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): A migration event with a type and a structured payload.

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): A thread-safe event bus for communication between worker threads and the UI.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Internal loop to process and dispatch events from the queue.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Starts the background dispatch thread.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Stops the background dispatch thread.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Subscribes a callback handler to receive events.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Loads YAML and returns (data, status_string)

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Prompts for missing fields in source and/or target blocks.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Prompts for host, port, user, password, database.

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Temporarily disables stdout logging handler.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Checks if the connection file is in .gitignore and warns if not.

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): A migration event with a type and a structured payload.

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): A thread-safe event bus for communication between worker threads and the UI.

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Internal loop to process and dispatch events from the queue.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Starts the background dispatch thread.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Stops the background dispatch thread.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Subscribes a callback handler to receive events.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): A Textual app to manage and monitor the sync-mail migration.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): An action to toggle dark mode.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Root configuration for a migration job between two tables.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Handles loading and validating YAML mapping configurations.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Loads and validates the YAML mapping configuration from the specified path.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Raised when there are issues with the YAML mapping configuration.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Raised when a database connection fails.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Raised when schema introspection fails.

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Raised when a batch of data fails to commit.

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Raised when resuming a migration fails due to state issues.

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Represents an event published by the migration engine.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Subscribes a handler function to receive events.         The handler function mu

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Internal method to process events from the queue and dispatch to subscribers.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Establishes a low-memory MariaDB connection using SSDictCursor.          Args:

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Context manager to ensure database connection is closed properly.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Context manager for atomic transactions on the database.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **121 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Manages migration state persistence and process locking.     Uses an atomic writ` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 12`** (9 nodes): `BatchProgress`, `.compose()`, `._update_label()`, `.watch_current_index()`, `.watch_current_job_name()`, `.watch_failure_count()`, `.watch_success_count()`, `.watch_total_jobs()`, `Overall progress for a batch of jobs.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Screen for inspecting state files.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Screen for database introspection and mapping generation.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `A minimal event bus for inter-module communication, especially between worker th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Publishes an event to the bus.         Events are added to an internal queue to`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Internal loop to process and dispatch events from the queue.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Starts the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Stops the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Publishes an event to the bus.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Subscribes a callback handler to receive events.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `A migration event with a type and a structured payload.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `A thread-safe event bus for communication between worker threads and the UI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Internal loop to process and dispatch events from the queue.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Starts the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Stops the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Publishes an event to the bus.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Subscribes a callback handler to receive events.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Loads YAML and returns (data, status_string)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Prompts for missing fields in source and/or target blocks.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Prompts for host, port, user, password, database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Temporarily disables stdout logging handler.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Checks if the connection file is in .gitignore and warns if not.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `A migration event with a type and a structured payload.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `A thread-safe event bus for communication between worker threads and the UI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Internal loop to process and dispatch events from the queue.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Starts the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Stops the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Publishes an event to the bus.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Subscribes a callback handler to receive events.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `A Textual app to manage and monitor the sync-mail migration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `An action to toggle dark mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Root configuration for a migration job between two tables.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Handles loading and validating YAML mapping configurations.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Loads and validates the YAML mapping configuration from the specified path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Raised when there are issues with the YAML mapping configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Raised when a database connection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Raised when schema introspection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Raised when a batch of data fails to commit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Raised when resuming a migration fails due to state issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Configures the root logger with StreamHandler and RotatingFileHandler.      Args`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Represents an event published by the migration engine.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Subscribes a handler function to receive events.         The handler function mu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Internal method to process events from the queue and dispatch to subscribers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Establishes a low-memory MariaDB connection using SSDictCursor.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Context manager to ensure database connection is closed properly.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Context manager for atomic transactions on the database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Event` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `DryRunScreen` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `SyncMailApp` connect `Community 1` to `Community 0`, `Community 6`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `MappingDocument` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`MappingDocument` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `ColumnMapping` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`ColumnMapping` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SyncMailApp` (e.g. with `Main entry point for the sync-mail CLI application.     Launches the Textual TUI` and `MenuScreen`) actually correct?**
  _`SyncMailApp` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Event` (e.g. with `MigrateScreen` and `Screen for monitoring migration job (Single or Batch).`) actually correct?**
  _`Event` has 23 INFERRED edges - model-reasoned connections that need verification._