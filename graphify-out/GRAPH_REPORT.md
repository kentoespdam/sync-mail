# Graph Report - .  (2026-04-29)

## Corpus Check
- Corpus is ~2,158 words - fits in a single context window. You may not need a graph.

## Summary
- 43 nodes · 33 edges · 10 communities detected
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Claude Project Overview|Claude Project Overview]]
- [[_COMMUNITY_Gemini Project Infrastructure|Gemini Project Infrastructure]]
- [[_COMMUNITY_ETL Pipeline & Data Flow|ETL Pipeline & Data Flow]]
- [[_COMMUNITY_Schema & YAML Management|Schema & YAML Management]]
- [[_COMMUNITY_DB Connectors & Cursors|DB Connectors & Cursors]]
- [[_COMMUNITY_State Management & Resiliency|State Management & Resiliency]]
- [[_COMMUNITY_Organizational Delegation SOP|Organizational Delegation SOP]]
- [[_COMMUNITY_Data Reconciliation Logic|Data Reconciliation Logic]]
- [[_COMMUNITY_Atomic Batch Transactions|Atomic Batch Transactions]]
- [[_COMMUNITY_Extraction PRD References|Extraction PRD References]]

## God Nodes (most connected - your core abstractions)
1. `sync-mail` - 12 edges
2. `sync-mail Project` - 7 edges
3. `ETL Data Flow` - 4 edges
4. `Extract phase` - 3 edges
5. `Server-side cursors` - 3 edges
6. `Data Migration & Schema Transformation engine` - 2 edges
7. `Load phase` - 2 edges
8. `YAML Generation` - 2 edges
9. `MariaDB/MySQL` - 1 edges
10. `PyMySQL` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Data Migration & Schema Transformation engine` --rationale_for--> `Generator-Based Processing`  [INFERRED]
  GEMINI.md → plan/prd.md
- `Phased Work Plan` --conceptually_related_to--> `ETL Data Flow`  [INFERRED]
  plan/extract-prd.md → plan/prd.md

## Communities

### Community 0 - "Claude Project Overview"
Cohesion: 0.17
Nodes (12): Per-batch atomic transactions, Beads, Bulk insert, Resume via state, Generator-based streaming, Keyset pagination, main.py, MariaDB (+4 more)

### Community 1 - "Gemini Project Infrastructure"
Cohesion: 0.22
Nodes (9): Beads, Data Migration & Schema Transformation engine, main.py, MariaDB/MySQL, PyMySQL, PyYAML / ruamel.yaml, SQLAlchemy 2.0, sync-mail Project (+1 more)

### Community 2 - "ETL Pipeline & Data Flow"
Cohesion: 0.25
Nodes (8): Phased Work Plan, Bulk Insert, ETL Data Flow, Extract phase, Keyset Pagination (Watermarking), Load phase, Server-Side Cursors, Transform phase

### Community 3 - "Schema & YAML Management"
Cohesion: 0.67
Nodes (3): mapping_template.yaml, Schema Introspection, YAML Generation

### Community 4 - "DB Connectors & Cursors"
Cohesion: 0.67
Nodes (3): PyMySQL, Server-side cursors, SQLAlchemy

### Community 6 - "State Management & Resiliency"
Cohesion: 1.0
Nodes (2): state.json, State Management & Resume Capability

### Community 7 - "Organizational Delegation SOP"
Cohesion: 1.0
Nodes (1): SOP Delegasi

### Community 8 - "Data Reconciliation Logic"
Cohesion: 1.0
Nodes (1): Reconciliation Logic

### Community 9 - "Atomic Batch Transactions"
Cohesion: 1.0
Nodes (1): Atomic Transactions

### Community 10 - "Extraction PRD References"
Cohesion: 1.0
Nodes (1): plan/extract-prd.md

## Knowledge Gaps
- **33 isolated node(s):** `MariaDB/MySQL`, `PyMySQL`, `SQLAlchemy 2.0`, `PyYAML / ruamel.yaml`, `Beads` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `State Management & Resiliency`** (2 nodes): `state.json`, `State Management & Resume Capability`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Organizational Delegation SOP`** (1 nodes): `SOP Delegasi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Reconciliation Logic`** (1 nodes): `Reconciliation Logic`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Atomic Batch Transactions`** (1 nodes): `Atomic Transactions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Extraction PRD References`** (1 nodes): `plan/extract-prd.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `sync-mail` connect `Claude Project Overview` to `DB Connectors & Cursors`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `Server-side cursors` connect `DB Connectors & Cursors` to `Claude Project Overview`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **What connects `MariaDB/MySQL`, `PyMySQL`, `SQLAlchemy 2.0` to the rest of the system?**
  _33 weakly-connected nodes found - possible documentation gaps or missing edges._