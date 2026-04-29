# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 45 files · ~35,146 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 375 nodes · 634 edges · 47 communities detected
- Extraction: 56% EXTRACTED · 44% INFERRED · 0% AMBIGUOUS · INFERRED: 281 edges (avg confidence: 0.69)
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

## God Nodes (most connected - your core abstractions)
1. `MappingDocument` - 36 edges
2. `ColumnMapping` - 29 edges
3. `Checkpoint` - 23 edges
4. `MappingConfigLoader` - 22 edges
5. `MigrateScreen` - 19 edges
6. `load_mapping()` - 17 edges
7. `Event` - 17 edges
8. `MigrationJob` - 16 edges
9. `SyncMailApp` - 14 edges
10. `ThroughputCalculator` - 14 edges

## Surprising Connections (you probably didn't know these)
- `MappingConfigLoader` --uses--> `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Initializes the ETL pipeline with configuration.          Args:             conf`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Initializes the necessary components based on the pipeline configuration.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Helper to find the primary key column name for a table from mapping.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Extracts data from the source table, using server-side cursors and yielding rows`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (30): compute_eta(), Records a completed batch., Calculates rows per second based on the sliding window., Calculates rows per second since the start of the job., Computes Estimated Time of Arrival based on remaining rows and throughput., Calculates moving average throughput (rows/sec).     Uses a sliding window of re, ThroughputCalculator, load() (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (36): Loads a YAML mapping file, parses it into a MappingDocument, and validates it., Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, Root configuration for a migration job between two tables., Metadata for a single column mapping., Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'. (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (21): Enum, Event, EventBus, EventType, A migration event with a type and a structured payload., A thread-safe event bus for communication between worker threads and the UI., Internal loop to process and dispatch events from the queue., Starts the background dispatch thread. (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (17): App, Screen, InspectScreen, Screen for inspecting state files., IntrospectScreen, Screen for database introspection and mapping generation., run_schema_introspection(), run_single_introspection() (+9 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (21): BatchFailedError, ConfigError, MigrationError, Raised when a data batch transaction fails to commit., Raised when resuming from a checkpoint fails (e.g., corrupt state.json)., Raised when there are issues with general configuration files (e.g., connection., Base exception for all migration-related errors., ResumeError (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (5): Vertical, BatchProgress, MigrationProgress, Overall progress for a batch of jobs., Combined progress bar and metrics widget.

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (15): connect(), connection_scope(), create_db_engine(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager for database connection lifecycle., Context manager for atomic transactions.     Ensures BEGIN is sent at start, COM, Creates a SQLAlchemy engine for introspection with low-memory settings., transaction() (+7 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (18): describe_table(), get_foreign_keys(), list_tables(), Retrieves all table names in a schema., Retrieves all foreign key relationships in a schema.     Returns list of {'table, Introspects a table and returns its column metadata from information_schema., IntrospectionError, Raised when reading database schema from information_schema fails. (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (13): _ask(), _check_gitignore(), _load_from_yaml(), _prompt_block(), _prompt_for_config(), Prompts for missing fields in source and/or target blocks., Prompts for host, port, user, password, database., Resolves database connection configuration from YAML or interactive input.     F (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (5): extract(), Extracts data from the source table using keyset pagination and streaming., Loader, Handles bulk loading of transformed data into the target table.     Caches the I, Builds the parameterized INSERT statement once.

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.49
Nodes (9): load_mapping(), temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size(), test_load_missing_cast_target() (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (4): configure_logging(), ContextFormatter, Custom formatter that ensures 'batch_id' and 'primary_key' exist in the record, Configures the root logger with STDOUT (INFO) and RotatingFileHandler (ERROR).

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): A migration event with a type and a structured payload.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): A thread-safe event bus for communication between worker threads and the UI.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Internal loop to process and dispatch events from the queue.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Starts the background dispatch thread.

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Stops the background dispatch thread.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Subscribes a callback handler to receive events.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): A Textual app to manage and monitor the sync-mail migration.

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Create child widgets for the app.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): An action to toggle dark mode.

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Root configuration for a migration job between two tables.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Handles loading and validating YAML mapping configurations.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Loads and validates the YAML mapping configuration from the specified path.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Raised when there are issues with the YAML mapping configuration.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Raised when a database connection fails.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Raised when schema introspection fails.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Raised when a batch of data fails to commit.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Raised when resuming a migration fails due to state issues.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Represents an event published by the migration engine.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): A minimal event bus for inter-module communication, especially between worker th

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.         Events are added to an internal queue to

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Subscribes a handler function to receive events.         The handler function mu

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Internal method to process events from the queue and dispatch to subscribers.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Establishes a low-memory MariaDB connection using SSDictCursor.          Args:

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Context manager to ensure database connection is closed properly.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Context manager for atomic transactions on the database.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **100 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Manages migration state persistence and process locking.     Uses an atomic writ` (+95 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 19`** (1 nodes): `A migration event with a type and a structured payload.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `A thread-safe event bus for communication between worker threads and the UI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Internal loop to process and dispatch events from the queue.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Starts the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Stops the background dispatch thread.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Publishes an event to the bus.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Subscribes a callback handler to receive events.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `A Textual app to manage and monitor the sync-mail migration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Create child widgets for the app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `An action to toggle dark mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Root configuration for a migration job between two tables.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Handles loading and validating YAML mapping configurations.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Loads and validates the YAML mapping configuration from the specified path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Raised when there are issues with the YAML mapping configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Raised when a database connection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Raised when schema introspection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Raised when a batch of data fails to commit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Raised when resuming a migration fails due to state issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Configures the root logger with StreamHandler and RotatingFileHandler.      Args`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Represents an event published by the migration engine.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `A minimal event bus for inter-module communication, especially between worker th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Publishes an event to the bus.         Events are added to an internal queue to`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Subscribes a handler function to receive events.         The handler function mu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Internal method to process events from the queue and dispatch to subscribers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Establishes a low-memory MariaDB connection using SSDictCursor.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Context manager to ensure database connection is closed properly.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Context manager for atomic transactions on the database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MigrateScreen` connect `Community 2` to `Community 0`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `Event` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `MappingDocument` connect `Community 1` to `Community 0`, `Community 9`, `Community 11`, `Community 6`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `MappingDocument` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`MappingDocument` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `ColumnMapping` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`ColumnMapping` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Checkpoint` (e.g. with `MigrationJob` and `JobBatch`) actually correct?**
  _`Checkpoint` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `MappingConfigLoader` (e.g. with `MappingDocument` and `ColumnMapping`) actually correct?**
  _`MappingConfigLoader` has 18 INFERRED edges - model-reasoned connections that need verification._