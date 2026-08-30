# Roadmap

**Statut : terminé** (2026-08-30). Aucune feature restante.

Projet **BI / SQL analytics** : base DuckDB + `queries.sql` + synthèse
courte illustrée par 2–3 graphiques matplotlib (pas de dashboard, pas
de carte). Les deux stretch optionnels (vue priorité, DuckDB spatial)
sont faits.

- [x] **Cadrage** — objectif, décisions (DuckDB, schéma étoile à deux
  faits), README et présentations de lancement. Réaligné le 2026-08-29
  sur le brief `sql-peb-batiments-wallonie.md` (neuf imposé, matplotlib,
  notebook de synthèse).
- [x] **Collecte et exploration** — extraits ODWB existant + neuf,
  profil colonnes / volume / qualité, pont Espec documenté (Ew absent)
- [x] **Schéma relationnel** — `sql/schema.sql` : dimensions partagées
  (commune via `mun_code`, province, label, type) + deux tables de faits
- [x] **Import et nettoyage** — `scripts/etl_odwb.py` + `sql/load.sql` :
  types, dates, Espec aberrant, cascade période → `data/processed/peb_wallonie.duckdb`
- [x] **Requêtes métier** — `sql/queries.sql` : 11 requêtes commentées
  (fenêtres RANK/LAG/QUALIFY, CTE, comparaison Espec neuf vs existant
  par province et par commune, avec mise en garde de régime ; Q11 lit
  la vue priorité)
- [x] **Vue priorité rénovation** *(optionnel)* — `v_priorite_renovation` :
  score 60 % volume (m² F/G) + 40 % taux, `percent_rank` par commune
- [x] **Synthèse et livrables portfolio** — diagramme entité-relation
  (`diagrams/modele_relationnel.png`), notebook
  `notebooks/synthese_resultats.ipynb` (3 graphiques matplotlib
  générés depuis les résultats SQL), recommandations public / privé,
  présentations à jour
- [x] **DuckDB spatial** *(optionnel, après les requêtes)* — polygones
  SPW (`limite_communale`), densité au km² et voisins (`ST_Touches`).
  Pas de XY bâtiment dans l'open data : pas de carte, pas de
  point-in-polygon.
