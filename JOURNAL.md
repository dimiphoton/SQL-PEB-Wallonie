# Journal de développement

## 2026-08-29 — Stretch optionnels

- Vue `v_priorite_renovation` : score 60 % volume (m² F/G) + 40 % taux
  (`percent_rank`). Q11 dans `sql/queries.sql`.
- DuckDB spatial : limites communales SPW (Lambert 2008), table
  `limite_communale`, densité au km² et adjacence `ST_Touches`.
  Les certificats n'ont pas de XY ; pas de carte.

## 2026-08-29 — Synthèse portfolio

- Diagramme ER (`diagrams/modele_relationnel.png`) et 3 figures
  matplotlib depuis le SQL (`scripts/synthese_figures.py`).
- Notebook `notebooks/synthese_resultats.ipynb` : Hainaut, taux vs
  volume, chauffage ; reco public / privé.

## 2026-08-29 — Requêtes métier

- `sql/queries.sql` : 10 requêtes commentées (portrait, top communes,
  écart Espec par province et par commune, série annuelle + LAG,
  type de logement, âge du bâti, chauffage, rang intra-province,
  m² de passoires). Runner : `scripts/run_queries.py`.
- Prochaine étape : synthèse (diagramme ER, notebook matplotlib).

## 2026-08-29 — Réalignement sur le brief révisé

- Brief `sql-peb-batiments-wallonie.md` : neuf + deux faits imposés
  (déjà en place), matplotlib + notebook de synthèse ajoutés à la
  roadmap, DuckDB spatial en stretch. Arborescence `scripts/` conservée.
- Prochaine étape inchangée : `sql/queries.sql`.

## 2026-08-29 — Import et nettoyage

- ETL Python + SQL : `scripts/etl_odwb.py` exécute `sql/schema.sql`
  puis `sql/load.sql` vers `data/processed/peb_wallonie.duckdb`.
- 261 communes, 874 605 certificats existants, 110 855 neufs.
  IDs sources uniques dans le Parquet (contrairement au count DISTINCT
  de l'API Explore). Espec aberrant → NULL (631 + 5), lignes gardées.
- Prochaine étape : `sql/queries.sql` (8–10 requêtes commentées).

## 2026-08-29 — Schéma relationnel

- `sql/schema.sql` : dimensions `province`, `commune`, `label_peb`,
  `type_logement` + faits `certificats_existant` / `certificats_neuf`.
- Vue `v_certificats` = pont Espec (UNION ALL, régime en légende).

## 2026-08-29 — Collecte et exploration

- Extraits ODWB téléchargés (`scripts/download_odwb.py`).
- Pont neuf vs existant = Espec ; Ew absent de l'open data.

## 2026-08-25 — Cadrage

- DuckDB, schéma étoile à deux faits, Python réservé à l'ETL.
- Pas de cartographie ni de dashboard. Niveau : intermédiaire.
