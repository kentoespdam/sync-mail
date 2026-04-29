# Graph Report - sync-mail  (2026-04-29)

## Corpus Check
- 23 files · ~22,885 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 138 nodes · 190 edges · 14 communities detected
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 64 edges (avg confidence: 0.73)
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
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]

## God Nodes (most connected - your core abstractions)
1. `MappingConfigLoader` - 14 edges
2. `MigrationError` - 11 edges
3. `Event` - 11 edges
4. `ETLPipeline` - 10 edges
5. `sync-mail` - 10 edges
6. `IntrospectionError` - 9 edges
7. `connect()` - 8 edges
8. `get_table_schema()` - 7 edges
9. `SyncMailApp` - 7 edges
10. `get_all_table_schemas()` - 6 edges

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
Cohesion: 0.15
Nodes (17): create_db_engine(), Creates a SQLAlchemy engine configured for MariaDB with server-side cursors., IntrospectionError, Raised when schema introspection fails., Exception, Event, Represents an event published by the migration engine., Publishes an event to the bus.         Events are added to an internal queue to (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (11): ETLPipeline, Extracts data from the source table, using server-side cursors and yielding rows, Transforms a single row based on the provided table mapping rules., Orchestrates the Extract, Transform, Load (ETL) process for data migration., Loads a batch of transformed rows into the target table using SQLAlchemy Core's, Initializes the ETL pipeline with configuration.          Args:             conf, Executes the full migration process: Extract, Transform, Load for all tables., Initializes the necessary components based on the pipeline configuration. (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (12): ColumnMapping, MappingDocument, describe_table(), Introspects a table and returns its column metadata from information_schema., generate_mapping(), Generates a MappingDocument based on source and target metadata.          Logic:, Saves MappingDocument to a YAML file using ruamel.yaml to preserve comments and, save_mapping_to_yaml() (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (10): connect(), connection_scope(), Establishes a low-memory MariaDB connection using SSDictCursor.          Args:, Context manager to ensure database connection is closed properly., Context manager for atomic transactions on the database., transaction(), test_connect_failure_wraps_exception(), test_connect_success() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (8): Enum, EventBus, EventType, A minimal event bus for inter-module communication, especially between worker th, Subscribes a handler function to receive events.         The handler function mu, Internal method to process events from the queue and dispatch to subscribers., configure_logging(), Configures the root logger with StreamHandler and RotatingFileHandler.      Args

### Community 5 - "Community 5"
Cohesion: 0.21
Nodes (10): BatchFailedError, ConnectionError, MappingError, MigrationError, Raised when there are issues with the YAML mapping configuration., Raised when a database connection fails., Raised when a batch of data fails to commit., Raised when resuming a migration fails due to state issues. (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (13): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, MariaDB, plan/prd.md (+5 more)

### Community 7 - "Community 7"
Cohesion: 0.2
Nodes (7): App, main(), Main entry point for the sync-mail CLI application.     Launches the Textual TUI, Create child widgets for the app., An action to toggle dark mode., A Textual app to manage and monitor the sync-mail migration., SyncMailApp

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Retrieves schema information for a specific table.      Args:         engine (En

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Retrieves schema information for all tables in a given schema.      Args:

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Maps SQLAlchemy type string representations to a simplified YAML type string.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Converts introspected schema information into a YAML string format using ruamel.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **43 isolated node(s):** `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.`, `Converts introspected schema information into a YAML string format using ruamel.`, `Handles loading and validating YAML mapping configurations.` (+38 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (1 nodes): `Retrieves schema information for a specific table.      Args:         engine (En`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Retrieves schema information for all tables in a given schema.      Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Maps SQLAlchemy type string representations to a simplified YAML type string.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Converts introspected schema information into a YAML string format using ruamel.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IntrospectionError` connect `Community 0` to `Community 2`, `Community 5`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `describe_table()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `MappingConfigLoader` (e.g. with `ETLPipeline` and `Orchestrates the Extract, Transform, Load (ETL) process for data migration.`) actually correct?**
  _`MappingConfigLoader` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MigrationError` (e.g. with `._initialize_components()` and `.run_migration()`) actually correct?**
  _`MigrationError` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Event` (e.g. with `get_table_schema()` and `get_all_table_schemas()`) actually correct?**
  _`Event` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Retrieves schema information for a specific table.      Args:         engine (En`, `Retrieves schema information for all tables in a given schema.      Args:`, `Maps SQLAlchemy type string representations to a simplified YAML type string.` to the rest of the system?**
  _43 weakly-connected nodes found - possible documentation gaps or missing edges._