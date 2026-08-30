# Changelog

## [1.0.0] — 2026-08-30

Clôture du projet. Brief livré (schéma étoile DuckDB, 11 requêtes,
synthèse matplotlib) et stretch inclus (vue priorité, DuckDB spatial).

- Stretch : vue `v_priorite_renovation` (score 60 % volume / 40 % taux)
  et extension spatiale DuckDB (limites SPW, densité, `ST_Touches`).
- Synthèse : diagramme ER, 3 graphiques matplotlib (Q03, taux vs
  volume, Q07), notebook de recommandations public / privé.
- 11 requêtes métier commentées (`sql/queries.sql`) : fenêtres SQL,
  comparaison Espec neuf vs existant, classement communes / m², Q11
  sur la vue priorité. Exécution : `python scripts/run_queries.py`.
- Cadrage réaligné sur le brief 2026-08-29 : deux faits imposés,
  synthèse matplotlib (pas de dashboard), notebook de synthèse et
  diagramme ER, extension spatiale DuckDB en option (livrée).
- ETL reproductible (`scripts/etl_odwb.py`, `sql/load.sql`) : schéma
  étoile chargé dans `data/processed/peb_wallonie.duckdb` (985 460
  certificats, 261 communes). Espec hors [-200, 1500] mis à NULL
  (631 + 5 lignes) ; dates, types de logement et période de
  construction normalisés.
- Schéma étoile DuckDB (`sql/schema.sql`) : 4 dimensions partagées,
  2 faits au grain certificat, vue `v_certificats` (pont Espec).
- Exploration ODWB : 874 605 certificats existants, 110 855 neufs ;
  pont documenté = Espec (Ew absent de l'open data) ; qualité
  (re-certifications, Espec aberrant, types de logement hétérogènes).
- Cadrage du projet PEB Wallonie : DuckDB, schéma étoile à deux tables de
  faits (existant + neuf), analyse 100 % SQL.
- Initialisation du projet à partir du template portfolio.
