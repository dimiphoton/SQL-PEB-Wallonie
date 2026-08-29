# Objectif du projet

- **But** : construire une base relationnelle propre (schéma étoile,
  DuckDB) à partir des certificats PEB wallons — existant **et** neuf —
  puis répondre à des questions métier via des requêtes SQL avancées,
  sans cartographie ni dashboard. Livrables : script d'import, schéma
  documenté (justifié dans le README + diagramme ER), `queries.sql`
  (8–10 requêtes commentées) et une synthèse courte (2–3 résultats →
  recommandations) illustrée par 2–3 graphiques matplotlib générés
  depuis le SQL, dans `notebooks/synthese_resultats.ipynb`.
- **Origine** : brief portfolio SQL
  (`brief/sql-peb-batiments-wallonie.md`, version 2026-08-29), données
  open data ODWB / SPW Énergie. Travail solo, pas de PR.
- **Contraintes de départ** :
  - SQL uniquement pour l'analyse (pas de SIG, pas de carte, pas de
    dashboard). matplotlib n'illustre que des résultats SQL déjà
    calculés — il ne remplace pas les agrégations.
  - Python réservé à l'ETL (téléchargement, nettoyage, chargement) et
    aux graphiques de synthèse.
  - Moteur analytique : DuckDB (imposé par le brief ; zéro serveur,
    reproductible en une commande).
  - Périmètre : résidentiel existant et neuf, **deux tables de faits**
    partageant les mêmes dimensions (commune, province, type, label).
  - Les deux régimes de notation ne se comparent pas terme à terme :
    le brief oppose lettre A–G (existant) et Ew/Espec (neuf). L'open
    data publie Espec + label des deux côtés ; Ew est absent. Pont
    retenu = Espec, avec mise en garde (voir README et
    `docs/exploration.md`).
  - Arborescence réelle : `scripts/` + `sql/load.sql` + `data/raw` /
    `data/processed` plutôt que `src/import_clean.py` et un `.duckdb`
    à la racine de `data/` (voir `docs/decisions.md`).
  - Stretch (faits) : vue `v_priorite_renovation` (score 60 % volume /
    40 % taux) ; extension spatiale DuckDB sur les limites communales
    SPW (densité, `ST_Touches`) — pas de XY bâtiment, pas de carte.
