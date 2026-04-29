# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 33 files · ~25,881 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 237 nodes · 362 edges · 31 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 152 edges (avg confidence: 0.72)
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
- [[_COMMUNITY_Community 38|Community 38]]

## God Nodes (most connected - your core abstractions)
1. `MappingDocument` - 23 edges
2. `Checkpoint` - 19 edges
3. `load_mapping()` - 16 edges
4. `ColumnMapping` - 16 edges
5. `MappingConfigLoader` - 14 edges
6. `load()` - 14 edges
7. `Event` - 12 edges
8. `MigrationError` - 11 edges
9. `ETLPipeline` - 10 edges
10. `MappingError` - 10 edges

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
Cohesion: 0.08
Nodes (29): Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, Root configuration for a migration job between two tables., Metadata for a single column mapping., Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'., Validates a MappingDocument for semantic correctness.     Raises MappingError wi (+21 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (22): Raised when resuming from a checkpoint fails (e.g., corrupt state.json)., ResumeError, load(), Functional wrapper for Loader.load for cases where a persistent Loader instance, Checkpoint, Saves the state atomically using a temporary file and os.replace()., Manages migration state persistence and process locking.     Uses an atomic writ, Marks the job as completed. (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (19): create_db_engine(), Creates a SQLAlchemy engine for introspection with low-memory settings., describe_table(), Introspects a table and returns its column metadata from information_schema., IntrospectionError, Raised when reading database schema from information_schema fails., Event, A migration event with a type and a structured payload. (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (13): Exception, ETLPipeline, Extracts data from the source table, using server-side cursors and yielding rows, Transforms a single row based on the provided table mapping rules., Orchestrates the Extract, Transform, Load (ETL) process for data migration., Loads a batch of transformed rows into the target table using SQLAlchemy Core's, Initializes the ETL pipeline with configuration.          Args:             conf, Executes the full migration process: Extract, Transform, Load for all tables. (+5 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (13): Enum, EventBus, EventType, A thread-safe event bus for communication between worker threads and the UI., Internal loop to process and dispatch events from the queue., Starts the background dispatch thread., Stops the background dispatch thread., Types of events that can be published to the EventBus. (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (11): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager for database connection lifecycle., Context manager for atomic transactions.     Ensures BEGIN is sent at start, COM, transaction(), Loads a batch of transformed rows into the target database.                  Arg, test_connect_failure_wraps_exception() (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (10): load_mapping(), Loads a YAML mapping file, parses it into a MappingDocument, and validates it., temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size() (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (7): App, main(), Main entry point for the sync-mail CLI application.     Launches the Textual TUI, Create child widgets for the app., An action to toggle dark mode., A Textual app to manage and monitor the sync-mail migration., SyncMailApp

### Community 9 - "Community 9"
Cohesion: 0.28
Nodes (6): BatchFailedError, ConnectionError, MigrationError, Raised when database connection fails (source or target)., Raised when a data batch transaction fails to commit., Base exception for all migration-related errors.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Raised when there are issues with the YAML mapping configuration.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Raised when a database connection fails.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Raised when schema introspection fails.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Raised when a batch of data fails to commit.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Raised when resuming a migration fails due to state issues.

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Represents an event published by the migration engine.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): A minimal event bus for inter-module communication, especially between worker th

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.         Events are added to an internal queue to

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Subscribes a handler function to receive events.         The handler function mu

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Internal method to process events from the queue and dispatch to subscribers.

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Establishes a low-memory MariaDB connection using SSDictCursor.          Args:

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Context manager to ensure database connection is closed properly.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Context manager for atomic transactions on the database.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **71 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Handles loading and validating YAML mapping configurations.` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (1 nodes): `Raised when there are issues with the YAML mapping configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Raised when a database connection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Raised when schema introspection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Raised when a batch of data fails to commit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Raised when resuming a migration fails due to state issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Configures the root logger with StreamHandler and RotatingFileHandler.      Args`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Represents an event published by the migration engine.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `A minimal event bus for inter-module communication, especially between worker th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Publishes an event to the bus.         Events are added to an internal queue to`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Subscribes a handler function to receive events.         The handler function mu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Internal method to process events from the queue and dispatch to subscribers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Establishes a low-memory MariaDB connection using SSDictCursor.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Context manager to ensure database connection is closed properly.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Context manager for atomic transactions on the database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_mapping()` connect `Community 7` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `Event` connect `Community 2` to `Community 3`, `Community 4`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `MappingDocument` connect `Community 0` to `Community 1`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `MappingDocument` (e.g. with `Reconciles source and target metadata to generate a MappingDocument.` and `Writes a MappingDocument to a YAML file with comments using ruamel.yaml.`) actually correct?**
  _`MappingDocument` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Checkpoint` (e.g. with `Fixture to provide a clean temporary state directory.` and `test_load_non_existent()`) actually correct?**
  _`Checkpoint` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `load_mapping()` (e.g. with `._initialize_components()` and `MappingError`) actually correct?**
  _`load_mapping()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ColumnMapping` (e.g. with `Reconciles source and target metadata to generate a MappingDocument.` and `Writes a MappingDocument to a YAML file with comments using ruamel.yaml.`) actually correct?**
  _`ColumnMapping` has 14 INFERRED edges - model-reasoned connections that need verification._