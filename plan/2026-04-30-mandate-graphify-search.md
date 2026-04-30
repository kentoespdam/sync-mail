# Design Document: Mandating Graphify for Source Code Navigation

## Goal
Explicitly mandate the use of `graphify` for searching function names, methods, and all source code-related entities within the project documentation and memory.

## Proposed Changes

### 1. `GEMINI.md`
Update the "Research" mandate and the "Graphify" section.

**Change in Core Mandates:**
- From: `- **Research:** ALWAYS use `graphify query` for local scanning. NEVER use recursive `ls` or `find`.`
- To: `- **Research:** ALWAYS use `graphify query` for local scanning and searching for source code entities (functions, methods, classes). NEVER use recursive `ls` or `find`.`

**Change in Graphify Section:**
- From:
  ```markdown
  ## Graphify (graphify-out/)
  - `graphify query "<q>"`: Architecture/Logic analysis.
  - `graphify path "<A>" "<B>"`: Module relations.
  ```
- To:
  ```markdown
  ## Graphify (graphify-out/)
  - `graphify query "<q>"`: Architecture/Logic analysis, function/method search, and code discovery.
  - `graphify path "<A>" "<B>"`: Module relations and dependency mapping.
  ```

### 2. `MEMORY.md`
Update the "Mandatory Directives" section.

**Change in Mandatory Directives:**
- From: `- **Research:** ALWAYS use `graphify query` or `graphify path` for scanning files.`
- To: `- **Research:** ALWAYS use `graphify query` or `graphify path` for scanning files and searching source code (functions, methods, classes).`

## Implementation Steps
1.  Modify `/mnt/DATA/python/sync-mail/GEMINI.md`.
2.  Modify `/home/dev/.gemini/tmp/sync-mail/memory/MEMORY.md`.
3.  Run `graphify update .` as required by hygiene rules.
