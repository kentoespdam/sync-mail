# GEMINI.md - sync-mail

## Project Overview
`sync-mail` is a high-performance Data Migration & Schema Transformation engine built in Python. Its primary purpose is to facilitate large-scale (millions of rows) one-time batch migrations between MariaDB hosts, specifically from a legacy source to an optimized target schema.

### Key Features
- **Low-Memory Footprint:** Uses server-side cursors and generator-based streaming to process data in chunks, preventing RAM exhaustion.
- **Schema Transformation:** Handles complex type conversions (e.g., `ENUM` to `VARCHAR`), missing column injections, and structural normalization via YAML-based mapping rules.
- **Bulk Loading:** Optimizes insertion speed using bulk insert operations.
- **Resiliency:** Features state management (via `state.json` or database tables) to allow resuming migrations from the last successful checkpoint.
- **Auto-Generation:** Supports schema introspection to automatically generate initial YAML mapping templates.

## Main Technologies
- **Language:** Python (>= 3.14)
- **Database:** MariaDB/MySQL
- **Libraries:**
  - `PyMySQL` (specifically `SSDictCursor` for server-side processing)
  - `SQLAlchemy 2.0` (Core layer only, avoiding ORM for performance)
  - `PyYAML` / `ruamel.yaml` (for configuration management)
  - `Beads` (for AI-native issue tracking and project management)

## Project Structure
- `main.py`: Entry point for the application.
- `plan/`: Contains project requirements and planning documentation.
  - `prd.md`: Comprehensive Product Requirements Document.
  - `extract-prd.md`: Specialized extraction requirements.
- `.beads/`: Configuration and data for the Beads issue tracking system.
- `pyproject.toml`: Project metadata and dependencies.

## Building and Running
### Installation
Ensure Python 3.14+ is installed. Use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Migrations
*Note: Specific CLI commands are TBD as implementation progresses.*
- **Generate Mapping:** `python main.py --introspect` (Planned)
- **Start Migration:** `python main.py --config mapping.yaml` (Planned)

### Testing
- **TODO:** Implement unit and integration tests using `pytest`.

## Development Conventions
- **Memory Efficiency:** Always use generators and server-side cursors for database operations. Avoid loading large datasets into memory at once.
- **Explicit Transformations:** All schema changes must be documented in the YAML mapping file.
- **Issue Tracking:** Use `bd` (Beads) for managing tasks and bugs.
  - `bd list`: View current issues.
  - `bd create "task description"`: Create a new task.
- **Coding Style:** Adhere to PEP 8. Use type hints for all function signatures.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
