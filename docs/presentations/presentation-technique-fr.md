---
marp: true
theme: default
paginate: true
---

# PEB Wallonie — présentation technique

*Synthèse — Espec comme pont, Ew absent*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)

---

## Cadrage du problème

Les extraits ODWB sont plats. Il faut un schéma étoile : dimensions
géographiques partagées (`mun_code`), deux faits (existant vs neuf),
des agrégats sans SIG.

---

## Données profilées

- Existant : 874 605 certificats (IDs uniques dans le Parquet).
- Neuf : 110 855 certificats (IDs uniques).
- 261 communes, 5 provinces, des deux côtés.
- Espec + label lettre **des deux côtés** ; **pas de colonne Ew**.

---

## Pont de mesure

Les seuils empiriques du label (++A…G) coïncident avec l'échelle Espec
wallonne (ex. B = 85–170 kWh/m².an). On compare l'**Espec**, pas la
part de G (0 % dans le neuf, 21 % dans l'existant).

Limite : certificat d'existant ≠ protocole construction neuve.

---

## Schéma étoile

Deux faits, dimensions partagées. Vue `v_certificats` = UNION ALL
avec `regime` en légende. Grain = certificat.

![w:780](../../diagrams/modele_relationnel.png)

---

## Requêtes (11)

`sql/queries.sql` : RANK, LAG, QUALIFY, CTE. Écart Espec neuf vs
existant : **272** kWh/m².an en Hainaut, **200** en Brabant wallon.
Taux de passoires ≠ volume en m² (Hastière vs Charleroi). Vue
`v_priorite_renovation` = 60 % volume + 40 % taux. Spatial : limites
SPW, densité et `ST_Touches` — pas de carte.

![w:680](../../pictures/readme/ecart-espec-provinces.png)

---

## Recommandations

**Public.** Volume → Charleroi / Liège ; taux → communes rurales ;
priorité régionale = Hainaut. Interdire le % de G comme KPI
neuf vs existant.

**Privé.** Maisons + poêles / électrique direct. PAC existantes
(médiane 145) déjà proches du neuf (88).

Limites : certificats ≠ parc ; 47 % sans période ; protocoles distincts.

---

## Stack technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
ETL + figures (`scripts/etl_odwb.py`, `scripts/synthese_figures.py`).

![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
Moteur analytique, zéro serveur.

![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)
Analyse métier dans `sql/queries.sql`. matplotlib n'illustre que le SQL.

---

## Code

`sql/schema.sql`, `sql/load.sql`, `sql/queries.sql`, `sql/spatial.sql`,
`notebooks/synthese_resultats.ipynb`, `docs/exploration.md`,
`scripts/download_odwb.py`, `scripts/etl_odwb.py`,
`scripts/run_queries.py`, `scripts/synthese_figures.py`,
`scripts/load_spatial.py`, `scripts/run_spatial.py`.
