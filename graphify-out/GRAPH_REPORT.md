# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 26 files · ~23,675 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 183 nodes · 252 edges · 31 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.7)
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
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
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

## God Nodes (most connected - your core abstractions)
1. `MappingConfigLoader` - 14 edges
2. `load_mapping()` - 14 edges
3. `ColumnMapping` - 14 edges
4. `MappingDocument` - 14 edges
5. `Event` - 12 edges
6. `MigrationError` - 11 edges
7. `ETLPipeline` - 10 edges
8. `MappingError` - 10 edges
9. `sync-mail` - 10 edges
10. `IntrospectionError` - 9 edges

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
Cohesion: 0.09
Nodes (28): create_db_engine(), Creates a SQLAlchemy engine for introspection with low-memory settings., IntrospectionError, Raised when reading database schema from information_schema fails., Exception, Event, A migration event with a type and a structured payload., Publishes an event to the bus. (+20 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (20): Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, Root configuration for a migration job between two tables., Metadata for a single column mapping., Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'., Validates a MappingDocument for semantic correctness.     Raises MappingError wi (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (10): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager for database connection lifecycle., Context manager for atomic transactions.     Ensures BEGIN is sent at start, COM, transaction(), test_connect_failure_wraps_exception(), test_connect_success() (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (10): load_mapping(), Loads a YAML mapping file, parses it into a MappingDocument, and validates it., temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size() (+2 more)

### Community 5 - "Community 5"
Cohesion: 0.2
Nodes (7): App, main(), Main entry point for the sync-mail CLI application.     Launches the Textual TUI, Create child widgets for the app., An action to toggle dark mode., A Textual app to manage and monitor the sync-mail migration., SyncMailApp

### Community 6 - "Community 6"
Cohesion: 0.24
Nodes (8): BatchFailedError, ConnectionError, MigrationError, Raised when database connection fails (source or target)., Raised when a data batch transaction fails to commit., Raised when resuming from a checkpoint fails (e.g., corrupt state.json)., Base exception for all migration-related errors., ResumeError

### Community 7 - "Community 7"
Cohesion: 0.22
Nodes (7): Enum, EventType, Types of events that can be published to the EventBus., configure_logging(), ContextFormatter, Custom formatter that ensures 'batch_id' and 'primary_key' exist in the record, Configures the root logger with STDOUT (INFO) and RotatingFileHandler (ERROR).

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (6): EventBus, A thread-safe event bus for communication between worker threads and the UI., Internal loop to process and dispatch events from the queue., Starts the background dispatch thread., Stops the background dispatch thread., Subscribes a callback handler to receive events.

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (3): describe_table(), Introspects a table and returns its column metadata from information_schema., test_describe_table_success()

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Raised when there are issues with the YAML mapping configuration.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Raised when a database connection fails.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Raised when schema introspection fails.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Raised when a batch of data fails to commit.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Raised when resuming a migration fails due to state issues.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Represents an event published by the migration engine.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): A minimal event bus for inter-module communication, especially between worker th

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.         Events are added to an internal queue to

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Subscribes a handler function to receive events.         The handler function mu

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Internal method to process events from the queue and dispatch to subscribers.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Establishes a low-memory MariaDB connection using SSDictCursor.          Args:

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Context manager to ensure database connection is closed properly.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Context manager for atomic transactions on the database.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **64 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Handles loading and validating YAML mapping configurations.` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 17`** (1 nodes): `Raised when there are issues with the YAML mapping configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Raised when a database connection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Raised when schema introspection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Raised when a batch of data fails to commit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Raised when resuming a migration fails due to state issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Configures the root logger with StreamHandler and RotatingFileHandler.      Args`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Represents an event published by the migration engine.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `A minimal event bus for inter-module communication, especially between worker th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Publishes an event to the bus.         Events are added to an internal queue to`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Subscribes a handler function to receive events.         The handler function mu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Internal method to process events from the queue and dispatch to subscribers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Establishes a low-memory MariaDB connection using SSDictCursor.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Context manager to ensure database connection is closed properly.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Context manager for atomic transactions on the database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_mapping()` connect `Community 4` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `Event` connect `Community 0` to `Community 8`, `Community 7`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `EventBus` connect `Community 8` to `Community 0`, `Community 7`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MappingConfigLoader` (e.g. with `ETLPipeline` and `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`) actually correct?**
  _`MappingConfigLoader` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `load_mapping()` (e.g. with `._initialize_components()` and `MappingError`) actually correct?**
  _`load_mapping()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ColumnMapping` (e.g. with `Reconciles source and target metadata to generate a MappingDocument.` and `Writes a MappingDocument to a YAML file with comments using ruamel.yaml.`) actually correct?**
  _`ColumnMapping` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `MappingDocument` (e.g. with `Reconciles source and target metadata to generate a MappingDocument.` and `Writes a MappingDocument to a YAML file with comments using ruamel.yaml.`) actually correct?**
  _`MappingDocument` has 12 INFERRED edges - model-reasoned connections that need verification._