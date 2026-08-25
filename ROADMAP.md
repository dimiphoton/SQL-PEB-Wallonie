# Roadmap

Projet **BI / SQL analytics** : base DuckDB + `queries.sql` + synthèse
courte. Pas de cartographie, pas de dashboard.

- [x] **Cadrage** — objectif, décisions (DuckDB, schéma étoile à deux
  faits), README et présentations de lancement
- [ ] **Collecte et exploration** — télécharger les deux jeux ODWB
  (existant + neuf), profiler colonnes / volume / qualité, documenter
  l'incomparabilité des régimes de notation
- [ ] **Schéma relationnel** — `sql/schema.sql` : dimensions partagées
  (commune, province, …) + deux tables de faits
- [ ] **Import et nettoyage** — script Python d'ETL (doublons, aberrants,
  types) vers un fichier DuckDB reproductible
- [ ] **Requêtes métier** — `sql/queries.sql` : 8–10 requêtes commentées,
  dont au moins une fenêtre ou CTE complexe, et une comparaison neuf vs
  existant là où elle est légitime
- [ ] **Vue priorité rénovation** *(optionnel)* — vue SQL exposant un
  score de priorité par commune
- [ ] **Synthèse et livrables portfolio** — diagramme entité-relation,
  recommandations pour un acteur public ou privé, présentations à jour
