# Agent Instructions

Companion to `CLAUDE.md`. Read both. `plan/prd.md` is the authoritative spec (Indonesian).

## MANDATORY: graphify-first

Before reading raw files or grepping for logic:

- Read `graphify-out/GRAPH_REPORT.md` first; navigate `graphify-out/wiki/index.md` if present.
- Use `graphify query "<question>"`, `graphify path "<A>" "<B>"`, `graphify explain "<concept>"` for any conceptual / cross-module / "how does X work" question.
- **Symbol lookups go through graphify too** — finding a function, method, class, attribute, caller, or callee in this project starts with `graphify query "<name>"` / `graphify explain "<name>"` / `graphify path "<A>" "<B>"`, never Glob/Grep.
- After code changes: `graphify update .`
- **Do NOT** recursively scan folders or broad-Glob/Grep for application logic or symbol discovery. Grep is for exact-string textual lookups only (known error literal, log message, file-path string).

## MANDATORY: context7 for library docs

When writing code against any library/framework/SDK/API/CLI (PyMySQL, SQLAlchemy, Textual, pytest, etc.):

- Resolve + fetch via `context7` MCP (`resolve-library-id` → `query-docs`) or `ctx7` CLI (`npx ctx7@latest library <name> "<q>"` → `npx ctx7@latest docs <id> "<q>"`).
- **Prefer context7 over web search** for API syntax, setup, version migration, best practices, source examples.
- Skip for: refactoring, business-logic debugging, general programming concepts.

## Beads (`bd`) — sole task tracker

```bash
bd ready                  # available work
bd show <id>              # details
bd update <id> --claim    # claim atomically
bd close <id>             # complete
bd dolt push              # sync remote
bd remember "<insight>"   # persistent knowledge (not MEMORY.md)
```

Run `bd prime` for full reference. Never use TodoWrite/TaskCreate/markdown TODOs.

## Python / uv

Always use `uv`, never raw `python`/`pip`:

```bash
uv run <cmd>        # execute in project env
uv run pytest       # tests
uv add <pkg>        # add dep
uv sync             # sync env
```

## Architectural constraints (from PRD — non-negotiable)

Server-side cursors (`SSDictCursor`) · generator streaming · keyset pagination (no `OFFSET`) · `executemany()` batches 5k–15k · per-batch atomic txn · resume via persisted last PK · no ORM / no Pandas by default · query logging disabled.

YAML mapping: `migration_job { source_table, target_table, batch_size, mappings: [...] }` with `transformation_type` ∈ `NONE | CAST | INJECT_DEFAULT`.

## Shell hygiene (avoid hangs)

Always non-interactive:

```bash
cp -f / mv -f / rm -f / rm -rf
apt-get -y
ssh -o BatchMode=yes
scp -o BatchMode=yes
HOMEBREW_NO_AUTO_UPDATE=1 brew ...
```

## Session close — push or it didn't happen

1. File `bd` issues for follow-ups.
2. Quality gates if code changed (`uv run pytest`, linters).
3. Update/close `bd` issues.
4. **Push (mandatory)**:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status   # "up to date with origin"
   ```
5. Clean stashes, prune branches. Verify all pushed. Hand off.

Never stop before push. Never defer to the user — YOU push.
