# CLAUDE.md

Guidance for Claude Code in this repo.

## Project

`sync-mail`: one-time batch **MariaDB → MariaDB** migration & schema transformation engine. Streams millions of rows with low memory, applies YAML-driven schema rules (CAST, INJECT_DEFAULT, missing-column handling), resumes from checkpoints. Authoritative spec: `plan/prd.md` (Indonesian).

## Architectural rules (non-negotiable, from PRD)

- **Server-side cursors only** (PyMySQL `SSDictCursor` or SQLAlchemy Core `yield_per()`). Never load full result sets.
- **Generator-based streaming** (`yield`) so chunk refs drop and GC releases RAM.
- **Keyset pagination only**: `WHERE pk > :last_id ORDER BY pk LIMIT :batch_size`. `OFFSET` is forbidden.
- **Bulk insert via `executemany()`**, batch 5,000–15,000 (tune to target `max_allowed_packet`).
- **No ORM, no Pandas by default.** SQLAlchemy Core only. Pandas only with strict `chunksize`.
- **Per-batch atomic txn**: `BEGIN` → `executemany` → `COMMIT`. On failure: `ROLLBACK`, optional row-by-row fallback.
- **Resume via state**: persist last evaluated PK to `state.json` or target state table after each commit.
- **Disable query/profiler logging** in driver and SQLAlchemy during runs.

## YAML mapping shape (see `plan/prd.md` §3)

```
migration_job:
  source_table, target_table, batch_size
  mappings: [ { source_column, target_column, transformation_type, ... } ]
```

`transformation_type`: `NONE` | `CAST` (with `cast_target`) | `INJECT_DEFAULT` (with `default_value`, e.g. `CURRENT_TIMESTAMP`). Introspection-generated templates flag review fields with `ACTION_REQUIRED`.

## Tooling

- **Python ≥ 3.14**. Use **`uv`** (`uv run`, `uv add`, `uv sync`) — never raw `python`/`pip`.
- Core deps: `PyMySQL`, `SQLAlchemy>=2.0`, YAML lib (`PyYAML` or `ruamel.yaml`).
- Tests: `pytest` via `uv run pytest`.
- `plan/` docs are Indonesian — preserve language unless asked otherwise.
- `GEMINI.md` may be stale; this file + `plan/prd.md` win.

## MANDATORY: graphify-first for code understanding

Before reading raw files, scanning, or grepping for application logic:

1. Read `graphify-out/GRAPH_REPORT.md` for god nodes and communities.
2. If `graphify-out/wiki/index.md` exists, navigate it instead of raw files.
3. For any "how does X work / relate to Y" question, use:
   - `graphify query "<question>"` — semantic traversal over EXTRACTED + INFERRED edges
   - `graphify path "<A>" "<B>"` — relationship between two concepts
   - `graphify explain "<concept>"` — concept summary
4. **Always use `graphify` to locate source-code symbols** — function names, method names, class names, attributes, callers/callees, or anything tied to project code. Start with `graphify query "<name>"` / `graphify explain "<name>"` / `graphify path "<A>" "<B>"` before reaching for Glob/Grep/Read.
5. After modifying code, run `graphify update .` to refresh the graph (AST-only, no API cost).

**Forbidden**: recursive folder scanning, broad Glob/Grep sweeps for conceptual/logic questions or symbol lookups. Use Grep only for exact-string textual lookups (a known error message, log literal, or file-path string).

## MANDATORY: context7 for library/framework docs

When coding against any library, framework, SDK, API, CLI, or cloud service — even well-known ones (React, SQLAlchemy, PyMySQL, Textual, pytest, etc.) — fetch current docs via **context7** before writing code. Training data may be stale.

- Use the `context7` MCP tools (`resolve-library-id` then `query-docs`) **or** the `ctx7` CLI (`npx ctx7@latest library <name> "<question>"` → `npx ctx7@latest docs <id> "<question>"`).
- **Prefer context7 over web search** for library docs, API syntax, version migration, setup, and CLI usage.
- Skip context7 for: refactoring, business logic debugging, code review, general programming concepts.

## Issue tracking: Beads (`bd`)

In-repo tracking lives in `.beads/` (Dolt-backed). Use `bd` for ALL task tracking — never TodoWrite/TaskCreate/markdown TODOs. Run `bd prime` for full command reference.

Quick: `bd ready` · `bd show <id>` · `bd update <id> --claim` · `bd close <id>` · `bd dolt push`

Persistent knowledge: `bd remember "<insight>"` (not MEMORY.md).

## Session close protocol — work is NOT done until `git push` succeeds

1. File `bd` issues for follow-ups.
2. Run quality gates if code changed (`uv run pytest`, linters).
3. Update issue status (`bd close`).
4. Push:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status   # must show "up to date with origin"
   ```
5. Clean stashes, prune branches.
6. Verify all committed AND pushed.
7. Hand off context for next session.

Never stop before pushing. Never say "ready to push when you are" — YOU push.

## Shell hygiene

Use non-interactive flags: `cp -f`, `mv -f`, `rm -f`, `rm -rf`, `apt-get -y`, `ssh -o BatchMode=yes`. Aliased `-i` mode will hang the agent.
