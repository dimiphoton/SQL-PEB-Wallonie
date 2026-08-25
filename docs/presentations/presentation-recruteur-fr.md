---
marp: true
theme: default
paginate: true
---

# Performance énergétique des bâtiments wallons

*Analyse SQL — cadrage*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)

---

## Le problème

La Wallonie connaît la performance énergétique de ses logements grâce aux
certificats PEB, mais ces données brutes ne disent pas, à elles seules,
où concentrer les rénovations. Un analyste doit pouvoir répondre vite :
quelles communes ont le plus de passoires ? le neuf est-il vraiment
meilleur, et où l'écart est-il le plus fort ?

---

## Les données

Deux jeux open data du SPW Énergie (logements existants et logements
neufs), localisés à la commune — sans carte, uniquement par jointures SQL.

---

## Le résultat

Une base propre et des requêtes SQL qui transforment ces certificats en
priorités concrètes pour un acteur public ou un bureau d'audit.
*(Analyse en cours de construction.)*
