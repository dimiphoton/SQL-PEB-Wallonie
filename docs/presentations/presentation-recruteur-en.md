---
marp: true
theme: default
paginate: true
---

# Energy performance of Walloon buildings

*SQL analysis — project framing*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)

---

## The problem

Wallonia publishes energy-performance certificates for homes, but the raw
files do not, by themselves, say where renovation should be concentrated.
An analyst needs fast answers: which municipalities have the most energy
sieves? does new housing actually perform better, and where is the gap
widest?

---

## The data

Two open datasets from the Walloon energy administration (existing homes
and new homes), located at municipality level — no maps, SQL joins only.

---

## The result

A clean database and SQL queries that turn certificates into concrete
priorities for a public body or an energy-audit firm.
*(Analysis still being built.)*
