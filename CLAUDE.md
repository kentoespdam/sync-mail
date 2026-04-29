# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

`sync-mail` is a one-time batch **MariaDB → MariaDB** data migration & schema transformation engine. Goals: stream millions of rows with a low memory footprint, apply YAML-driven schema rules (type casts, default injection, missing-column handling), and resume from checkpoints after interruption.

The implementation is **greenfield**: `main.py` is still a PyCharm placeholder, `pyproject.toml` has no dependencies declared, and there is no CLI yet. Treat `plan/prd.md` as the authoritative spec — it describes architecture and rules in detail (mostly in Indonesian). `plan/extract-prd.md` is the prompt template the user uses to elaborate the PRD into phased tasks.

## Architectural rules (non-negotiable, from the PRD)

These constraints must hold for any new code; they are the reason the project exists:

- **Server-side cursors only.** Use PyMySQL's `SSDictCursor` (or SQLAlchemy Core with `yield_per()`). Never load a full result set into client memory.
- **Generator-based streaming.** Wrap cursor reads in generators (`yield`) so each chunk's references drop and Python's GC can release RAM.
- **Keyset pagination, never `OFFSET`.** Extract uses `WHERE pk > :last_id ORDER BY pk LIMIT :batch_size`. `OFFSET` is forbidden — it forces MariaDB to rescan prior rows.
- **Bulk insert via `executemany()`** with batch size 5,000–15,000, tuned against target's `max_allowed_packet`.
- **No ORM, no Pandas by default.** SQLAlchemy is allowed only at Core level. Pandas only with strict `chunksize` if matrix transforms are unavoidable.
- **Per-batch atomic transactions.** `BEGIN` → `executemany` → `COMMIT`. On batch failure, `ROLLBACK`, then optionally fall back to row-by-row insert to isolate the bad row.
- **Resume via state.** After each successful batch commit, persist the last evaluated primary key (to `state.json` or a state table on the target) so a restart continues exactly where it stopped.
- **Disable query/profiler logging** in driver and SQLAlchemy during runs — no SQL text retention in memory.

## YAML mapping shape

The mapping file is the single source of truth for schema resolution. Top-level shape (see `plan/prd.md` §3):

```
migration_job:
  source_table, target_table, batch_size
  mappings: list of { source_column, target_column, transformation_type, ... }
```

Supported `transformation_type` values: `NONE` (direct), `CAST` (with `cast_target`, e.g. ENUM→VARCHAR), `INJECT_DEFAULT` (with `default_value`, including `CURRENT_TIMESTAMP`). Auto-generated templates from introspection should mark fields needing human review with an `ACTION_REQUIRED` flag.

## Tooling

- **Python ≥ 3.14** (declared in `pyproject.toml`). Install in a venv with `pip install -e .`.
- **Dependencies are not yet pinned.** When adding the first real code, add `PyMySQL`, `SQLAlchemy>=2.0`, and a YAML lib (`PyYAML` or `ruamel.yaml`) to `pyproject.toml`.
- **No tests yet.** When adding tests, use `pytest`.

## Issue tracking: Beads (`bd`)

This repo uses [Beads](https://github.com/steveyegge/beads) for in-repo issue tracking (data lives in `.beads/`, Dolt-backed). Use it for tasks/bugs instead of TODO comments:

- `bd list` — view issues
- `bd create "..."` — new issue
- `bd show <id>` / `bd update <id> --claim` / `bd update <id> --status done`
- `bd dolt push` — sync Dolt remote

## Notes for future work

- A `GEMINI.md` exists with overlapping but partially out-of-date guidance; prefer this file and `plan/prd.md` when they disagree.
- The PRD is written in Indonesian — preserve that when editing `plan/` docs unless asked otherwise.


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
