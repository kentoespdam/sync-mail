# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 26 files · ~23,918 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 157 nodes · 240 edges · 17 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 89 edges (avg confidence: 0.71)
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
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]

## God Nodes (most connected - your core abstractions)
1. `MappingConfigLoader` - 14 edges
2. `load_mapping()` - 14 edges
3. `MigrationError` - 11 edges
4. `Event` - 11 edges
5. `ETLPipeline` - 10 edges
6. `MappingError` - 10 edges
7. `ColumnMapping` - 10 edges
8. `MappingDocument` - 10 edges
9. `sync-mail` - 10 edges
10. `IntrospectionError` - 9 edges

## Surprising Connections (you probably didn't know these)
- `MappingConfigLoader` --uses--> `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Helper to find the primary key column name for a table from mapping.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Extracts data from the source table, using server-side cursors and yielding rows`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Transforms a single row based on the provided table mapping rules.`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py
- `MappingConfigLoader` --uses--> `Loads a batch of transformed rows into the target table using SQLAlchemy Core's`  [INFERRED]
  src/sync_mail/mapping.py → pipeline/etl_pipeline.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (21): Loads a YAML mapping file into a MappingDocument dataclass and validates it., ColumnMapping, MappingDocument, _fmt_line(), _has_action_required(), Helper to format line number prefix if available., Checks if any field contains 'ACTION_REQUIRED'., Validates a MappingDocument for semantic correctness.     Raises MappingError wi (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (10): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager to ensure database connection is closed properly., Context manager for atomic transactions on the database., transaction(), test_connect_failure_wraps_exception(), test_connect_success() (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (8): Exception, ETLPipeline, Extracts data from the source table, using server-side cursors and yielding rows, Transforms a single row based on the provided table mapping rules., Orchestrates the Extract, Transform, Load (ETL) process for data migration., Loads a batch of transformed rows into the target table using SQLAlchemy Core's, Executes the full migration process: Extract, Transform, Load for all tables., Helper to find the primary key column name for a table from mapping.

### Community 3 - "Community 3"
Cohesion: 0.21
Nodes (12): IntrospectionError, Raised when schema introspection fails., Event, Represents an event published by the migration engine., convert_schema_to_yaml(), get_all_table_schemas(), get_table_schema(), map_sqlalchemy_type_to_yaml() (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (8): Enum, EventBus, EventType, A minimal event bus for inter-module communication, especially between worker th, Subscribes a handler function to receive events.         The handler function mu, Internal method to process events from the queue and dispatch to subscribers., configure_logging(), Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.2
Nodes (7): App, main(), Main entry point for the sync-mail CLI application.     Launches the Textual TUI, Create child widgets for the app., An action to toggle dark mode., A Textual app to manage and monitor the sync-mail migration., SyncMailApp

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (8): BatchFailedError, ConnectionError, MigrationError, Raised when a database connection fails., Raised when a batch of data fails to commit., Raised when resuming a migration fails due to state issues., Base exception for all migration-related errors., ResumeError

### Community 8 - "Community 8"
Cohesion: 0.42
Nodes (9): load_mapping(), temp_yaml(), test_aggregate_errors(), test_error_line_numbers(), test_load_action_required_remaining(), test_load_duplicate_target(), test_load_invalid_batch_size(), test_load_missing_cast_target() (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (5): Initializes the ETL pipeline with configuration.          Args:             conf, Initializes the necessary components based on the pipeline configuration., MappingConfigLoader, Handles loading and validating YAML mapping configurations., Loads and validates the YAML mapping configuration from the specified path.

### Community 10 - "Community 10"
Cohesion: 0.5
Nodes (3): create_db_engine(), Creates a SQLAlchemy engine configured for MariaDB with server-side cursors., Publishes an event to the bus.         Events are added to an internal queue to

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **43 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Handles loading and validating YAML mapping configurations.` (+38 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_mapping()` connect `Community 8` to `Community 0`, `Community 9`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `Event` connect `Community 3` to `Community 9`, `Community 2`, `Community 10`, `Community 4`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `MappingError` connect `Community 0` to `Community 8`, `Community 9`, `Community 7`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MappingConfigLoader` (e.g. with `ETLPipeline` and `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`) actually correct?**
  _`MappingConfigLoader` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `load_mapping()` (e.g. with `._initialize_components()` and `MappingError`) actually correct?**
  _`load_mapping()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MigrationError` (e.g. with `._initialize_components()` and `.run_migration()`) actually correct?**
  _`MigrationError` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Event` (e.g. with `get_table_schema()` and `get_all_table_schemas()`) actually correct?**
  _`Event` has 8 INFERRED edges - model-reasoned connections that need verification._