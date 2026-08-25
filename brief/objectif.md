# Objectif du projet

- **But** : construire une base relationnelle propre (schéma étoile) à
  partir des certificats PEB wallons, puis répondre à des questions métier
  via des requêtes SQL avancées — sans cartographie ni dashboard. Livrables :
  script d'import, schéma documenté, `queries.sql` (8–10 requêtes commentées)
  et une synthèse courte (2–3 résultats → recommandations).
- **Origine** : brief portfolio SQL (`brief/03-sql-peb-batiments-wallonie.md`),
  données open data ODWB / SPW Énergie. Travail solo, pas de PR.
- **Contraintes de départ** :
  - SQL uniquement pour l'analyse (pas de SIG, pas de carte).
  - Python réservé à l'ETL (téléchargement, nettoyage, chargement).
  - Moteur analytique : DuckDB (zéro serveur, reproductible en une commande).
  - Périmètre : résidentiel **existant** et **neuf**, deux tables de faits
    partageant les mêmes dimensions (commune, province, etc.).
  - Les deux régimes de notation ne se comparent pas terme à terme (lettre
    A–G côté existant vs indicateurs Ew / Espec côté neuf) : à vérifier
    sur les colonnes réelles et à documenter explicitement.

Ce fichier capture le but brut, tel qu'il a été formulé au départ. Les
versions polies destinées au portfolio vivent dans `README.md` et `docs/`.
