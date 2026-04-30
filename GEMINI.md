# sync-mail | High-Performance Migration Engine

## Core Mandates
- **Research:** ALWAYS use `graphify query` for local scanning and searching for source code entities (functions, methods, classes). NEVER use recursive `ls` or `find`.
- **Docs:** PRIORITIZE `context7` for libraries and best practices over general web search.
- **Memory:** Generators + `SSDictCursor` for all streaming.
- **TUI:** Long tasks in `App.run_worker(thread=True)`, UI via `app.call_from_thread()`.
- **Hygiene:** Run `graphify update .` after ANY code change.

## Beads (`bd`) - Task Management
Sole task tracker. NEVER use markdown TODOs.
- `bd ready` / `bd show <id>`: Find/Read work.
- `bd update <id> --claim`: Claim atomically.
- `bd close <id>`: Mark complete.
- `bd dolt push`: Sync state (Mandatory).
- `bd remember "<insight>"`: Persistent knowledge.

## Session Close (MANDATORY)
1. Run quality gates (`uv run pytest`, linters).
2. Close `bd` issues.
3. **Push or it didn't happen:**
   ```bash
   git pull --rebase && bd dolt push && git push
   ```

## Stack & Commands
- **Tech:** Python 3.14+, `uv`, MariaDB (SQLAlchemy Core), Textual (TUI).
- **Setup:** `uv sync`
- **Run:** `uv run python src/sync_mail/tui/app.py`
- **Test:** `uv run pytest`

## Graphify (graphify-out/)
- `graphify query "<q>"`: Architecture/Logic analysis, function/method search, and code discovery.
- `graphify path "<A>" "<B>"`: Module relations and dependency mapping.
