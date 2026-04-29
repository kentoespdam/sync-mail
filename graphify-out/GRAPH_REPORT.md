# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 36 files · ~26,770 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 267 nodes · 446 edges · 33 communities detected
- Extraction: 54% EXTRACTED · 46% INFERRED · 0% AMBIGUOUS · INFERRED: 205 edges (avg confidence: 0.7)
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
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]

## God Nodes (most connected - your core abstractions)
1. `MappingDocument` - 28 edges
2. `Checkpoint` - 25 edges
3. `MappingConfigLoader` - 22 edges
4. `ColumnMapping` - 21 edges
5. `load_mapping()` - 17 edges
6. `load()` - 16 edges
7. `Event` - 13 edges
8. `MigrationJob` - 12 edges
9. `ThroughputCalculator` - 12 edges
10. `MigrationError` - 11 edges

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
Nodes (35): create_db_engine(), Creates a SQLAlchemy engine for introspection with low-memory settings., describe_table(), Introspects a table and returns its column metadata from information_schema., BatchFailedError, ConnectionError, IntrospectionError, MigrationError (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (22): Raised when resuming from a checkpoint fails (e.g., corrupt state.json)., ResumeError, load(), Functional wrapper for Loader.load for cases where a persistent Loader instance, Checkpoint, Saves the state atomically using a temporary file and os.replace()., Manages migration state persistence and process locking.     Uses an atomic writ, Marks the job as completed. (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (23): Loads a YAML mapping file, parses it into a MappingDocument, and validates it., Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, Root configuration for a migration job between two tables., Metadata for a single column mapping., Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'. (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (16): compute_eta(), Records a completed batch., Calculates rows per second based on the sliding window., Calculates rows per second since the start of the job., Computes Estimated Time of Arrival based on remaining rows and throughput., Calculates moving average throughput (rows/sec).     Uses a sliding window of re, ThroughputCalculator, MigrationJob (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (10): extract(), Extracts data from the source table using keyset pagination and streaming., Loader, Handles bulk loading of transformed data into the target table.     Caches the I, Builds the parameterized INSERT statement once., Loads a batch of transformed rows into the target database.                  Arg, Transforms a list of source rows into a list of tuples ready for target insertio, transform() (+2 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (13): Enum, EventBus, EventType, A thread-safe event bus for communication between worker threads and the UI., Internal loop to process and dispatch events from the queue., Starts the background dispatch thread., Stops the background dispatch thread., Types of events that can be published to the EventBus. (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (10): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager for database connection lifecycle., Context manager for atomic transactions.     Ensures BEGIN is sent at start, COM, transaction(), test_connect_failure_wraps_exception(), test_connect_success() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (7): App, main(), Main entry point for the sync-mail CLI application.     Launches the Textual TUI, Create child widgets for the app., An action to toggle dark mode., A Textual app to manage and monitor the sync-mail migration., SyncMailApp

### Community 9 - "Community 9"
Cohesion: 0.42
Nodes (9): load_mapping(), temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size(), test_load_missing_cast_target() (+1 more)

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Handles loading and validating YAML mapping configurations.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Loads and validates the YAML mapping configuration from the specified path.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Raised when there are issues with the YAML mapping configuration.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Raised when a database connection fails.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Raised when schema introspection fails.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Raised when a batch of data fails to commit.

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Raised when resuming a migration fails due to state issues.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Represents an event published by the migration engine.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): A minimal event bus for inter-module communication, especially between worker th

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Publishes an event to the bus.         Events are added to an internal queue to

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Subscribes a handler function to receive events.         The handler function mu

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Internal method to process events from the queue and dispatch to subscribers.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Establishes a low-memory MariaDB connection using SSDictCursor.          Args:

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Context manager to ensure database connection is closed properly.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Context manager for atomic transactions on the database.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **76 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Manages migration state persistence and process locking.     Uses an atomic writ` (+71 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 17`** (1 nodes): `Handles loading and validating YAML mapping configurations.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Loads and validates the YAML mapping configuration from the specified path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Raised when there are issues with the YAML mapping configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Raised when a database connection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Raised when schema introspection fails.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Raised when a batch of data fails to commit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Raised when resuming a migration fails due to state issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Configures the root logger with StreamHandler and RotatingFileHandler.      Args`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Represents an event published by the migration engine.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `A minimal event bus for inter-module communication, especially between worker th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Publishes an event to the bus.         Events are added to an internal queue to`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Subscribes a handler function to receive events.         The handler function mu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Internal method to process events from the queue and dispatch to subscribers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Establishes a low-memory MariaDB connection using SSDictCursor.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Context manager to ensure database connection is closed properly.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Context manager for atomic transactions on the database.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MappingConfigLoader` connect `Community 3` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `Event` connect `Community 0` to `Community 2`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `load_mapping()` connect `Community 9` to `Community 0`, `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `MappingDocument` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`MappingDocument` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Checkpoint` (e.g. with `MigrationJob` and `Orchestrates the end-to-end migration process.     Handles loading mapping, chec`) actually correct?**
  _`Checkpoint` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `MappingConfigLoader` (e.g. with `MappingDocument` and `ColumnMapping`) actually correct?**
  _`MappingConfigLoader` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ColumnMapping` (e.g. with `MappingConfigLoader` and `Handles loading and validating YAML mapping configurations.`) actually correct?**
  _`ColumnMapping` has 19 INFERRED edges - model-reasoned connections that need verification._