---
marp: true
theme: default
paginate: true
---

# Walloon PEB — technical write-up

*Framing — star schema, DuckDB, SQL only*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)

---

## Problem framing

ODWB PEB extracts are flat files (one certificate, one municipality, one
indicator). A usable model needs shared geographic dimensions, two distinct
facts (existing vs new stock), and queries that aggregate without GIS.

---

## Approach and methodology

1. Profile both ODWB datasets (quality, columns, rating regimes).
2. Design a star schema: municipality / province dimensions, fact tables
   `certificats_existant` and `certificats_neuf`.
3. Python ETL → a reproducible DuckDB file.
4. 8–10 commented SQL queries (window functions, CTEs, comparison only
   where it is legitimate).
5. Short synthesis: results → recommendations.

A–G labels (existing) and Ew / Espec indicators (new) will not be merged
without a documented bridge.

---

## Tech stack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
ETL only: download, clean, load.

![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
Native analytical engine, no server, first-class window functions and
CTEs. Avoids replaying PostgreSQL, already used elsewhere in the
portfolio.

![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)
All business analysis stays in `sql/queries.sql`.

---

## Metrics and rationale

No predictive model. Business metrics will be those on the certificates
(Espec kWh/m²·year, label, volumes) plus geographic aggregates. Exact
choices come after profiling the real columns.

---

## Results analysis and limitations

No results yet. One limit is already set: the two certification regimes
are not comparable one-to-one; any new-vs-existing gap must state *which
quantity* is being compared.

---

## Code

Upcoming: `sql/schema.sql`, `sql/queries.sql`, import script under `src/`.
Decisions: `docs/decisions.md`.
