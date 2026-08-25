# Walloon building energy performance (PEB) — SQL analysis

| | |
|---|---|
| **Stack** | ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white) ![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey) |
| **Level** | Intermediate |
| **Data specialty** | BI |

## Objective

Turn Wallonia's open PEB (building energy performance) certificates into a
clean star-schema database, then answer policy-relevant questions with
advanced SQL only — no maps, no dashboard. Typical questions: which
municipalities concentrate energy sieves? does new housing actually
outperform the existing stock, and where is the gap widest?

## Data

Two ODWB / SPW Énergie datasets, joined through shared geographic
dimensions (municipality, province, INS code):

- [PEB — existing residential buildings](https://www.odwb.be/explore/dataset/peb-certification-residentielle-batiment-existant/)
- [PEB — new residential buildings](https://www.odwb.be/explore/dataset/peb-batiments-residentiels-neufs/)

Existing stock is labelled A–G; new buildings are assessed with Ew / Espec
indicators. The two regimes are **not** compared one-to-one without an
explicit, documented bridge.

## Result

A reproducible DuckDB database, a documented relational schema, 8–10
commented SQL queries, and a short synthesis translating a few results into
recommendations for a public or private actor. *(Pipeline not built yet —
see `ROADMAP.md`.)*

## Reproduce

Not applicable until the ETL step lands. Planned flow:

```bash
pip install -e .
python -m mon_projet.cli --help
```

## Repo structure

Template plus the PEB brief; analysis code is still to come.

- `brief/` — raw goal and original SQL brief
- `sql/` — `schema.sql` and `queries.sql` *(upcoming)*
- `src/` — Python ETL only *(upcoming)*
- `docs/decisions.md` — why DuckDB, why two fact tables
- `ROADMAP.md` / `JOURNAL.md` — progress (kept in French)

## Presentations

- [Recruiter overview (EN)](docs/slides/presentation-recruteur-en.html)
- [Technical deep dive (EN)](docs/slides/presentation-technique-en.html)
- [Présentation grand public (FR)](docs/slides/presentation-recruteur-fr.html)
- [Présentation technique (FR)](docs/slides/presentation-technique-fr.html)
