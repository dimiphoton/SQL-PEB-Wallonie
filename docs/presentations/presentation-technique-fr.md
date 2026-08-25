---
marp: true
theme: default
paginate: true
---

# PEB Wallonie — présentation technique

*Cadrage — schéma étoile, DuckDB, SQL uniquement*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)

---

## Cadrage du problème

Les certificats PEB ODWB sont des extraits plats (un certificat, une
commune, un indicateur). Pour un usage métier, il faut un modèle
relationnel : dimensions géographiques partagées, deux faits distincts
(existant vs neuf), et des requêtes qui agrègent sans SIG.

---

## Approche et méthodologie

1. Explorer les deux jeux ODWB (qualité, colonnes, régimes de notation).
2. Modéliser un schéma étoile : dimensions commune / province, faits
   `certificats_existant` et `certificats_neuf`.
3. ETL Python → fichier DuckDB reproductible.
4. 8–10 requêtes SQL commentées (fenêtres, CTE, comparaison là où elle
   est légitime).
5. Synthèse courte : résultats → recommandations.

Les lettres A–G (existant) et les indicateurs Ew / Espec (neuf) ne seront
pas fusionnés sans pont documenté.

---

## Stack technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
ETL uniquement : téléchargement, nettoyage, chargement.

![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
Moteur analytique natif, zéro serveur, fenêtrage et CTE de premier ordre.
Évite de rejouer PostgreSQL déjà présent ailleurs dans le portfolio.

![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)
Toute l'analyse métier reste dans `sql/queries.sql`.

---

## Métriques et justification

Pas de modèle prédictif. Les indicateurs métier seront ceux des
certificats (Espec kWh/m².an, label, volumes) plus des agrégats
géographiques. Choix précis après exploration des colonnes réelles.

---

## Analyse des résultats et limites

Pas encore de résultats. Limite déjà posée : deux régimes de certification
incomparables terme à terme ; tout écart neuf vs existant devra dire
*sur quelle grandeur* on compare.

---

## Code

À venir : `sql/schema.sql`, `sql/queries.sql`, script d'import dans `src/`.
Décisions : `docs/decisions.md`.
