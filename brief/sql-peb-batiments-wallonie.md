# Performance énergétique des bâtiments wallons (PEB) — analyse SQL

## Contexte et problématique

La Wallonie publie en open data les certificats de performance énergétique des bâtiments (PEB), un indicateur clé de la qualité du bâti et un levier majeur de la politique climatique régionale. Un analyste travaillant pour une administration, un bureau d'audit énergétique ou un fournisseur d'énergie doit pouvoir répondre rapidement à des questions comme : quelles communes concentrent le plus de passoires énergétiques ? quel est le potentiel de rénovation par province ?

Ce projet est volontairement centré sur le SQL : c'est le repo où la rigueur de modélisation et la complexité des requêtes doivent parler d'elles-mêmes.

## Objectif

Construire une base de données relationnelle propre (DuckDB) à partir des données PEB — bâtiments existants et constructions neuves — et y répondre à une série de questions métier via des requêtes SQL avancées, sans recourir à un outil de cartographie.

## Compétences démontrées

- Modélisation relationnelle (normalisation, clés, table de dimension commune/province)
- Modélisation en schéma multi-tables de faits (existant / neuf) partageant les mêmes dimensions — un design proche d'un schéma en étoile
- Requêtes SQL avancées : jointures multiples, fonctions de fenêtrage, sous-requêtes, CTE
- Agrégations à plusieurs niveaux géographiques (commune, province, région) — uniquement via des clés et des `GROUP BY`, sans SIG
- Détection et traitement des anomalies de données (doublons, valeurs aberrantes)

## Sources de données

- **ODWB — Open Data Wallonie-Bruxelles** ([odwb.be](https://www.odwb.be)), données PEB publiées par le SPW Énergie : deux jeux de données à mobiliser — certificats PEB des bâtiments existants (indicateur en lettre A-G) et déclarations PEB des constructions neuves (indicateurs Ew/Espec). À vérifier lors de la collecte : la disponibilité effective des deux jeux sur ODWB et la compatibilité de la clé géographique (commune) entre les deux.

## Livrables attendus

1. Script d'import et de nettoyage des données PEB (existant et neuf).
2. Base DuckDB avec schéma documenté : deux tables de faits (existant, neuf) partageant les mêmes dimensions (commune, province, type de bâtiment) — diagramme entité-relation dans le README.
3. Un fichier `queries.sql` regroupant 8 à 10 requêtes commentées répondant à des questions métier précises (ex. : top 10 des communes avec la plus mauvaise performance moyenne sur l'existant, écart de performance neuf vs existant par province, évolution du nombre de certificats par an).
4. Une synthèse courte traduisant 2-3 résultats SQL en recommandations pour un acteur public ou privé, illustrée par 2-3 graphiques statiques (matplotlib) générés directement depuis les résultats de requêtes — pas de dashboard interactif : la visualisation reste au service de la lecture, elle ne devient pas une couche BI à part entière.

## Structure de repo attendue

```
projet-peb-wallonie-sql/
├── README.md
├── data/
│   └── peb_wallonie.duckdb
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── src/
│   └── import_clean.py
├── notebooks/
│   └── synthese_resultats.ipynb
└── diagrams/
    └── modele_relationnel.png
```

## Règles strictes de professionnalisme

- Environnement figé et reproductible : base DuckDB régénérée par script à partir des données brutes, en une seule commande documentée — pas de fichier de base binaire committé sans le script qui le reconstruit.
- Chaque requête SQL est commentée : ce qu'elle répond, pourquoi c'est utile.
- Le schéma relationnel est justifié dans le README (pourquoi ces tables, ces clés, pourquoi deux tables de faits plutôt qu'une).
- Au moins une requête utilise une fonction de fenêtrage ou une CTE complexe — pas seulement des `GROUP BY` simples.
- Toute divergence méthodologique entre les deux régimes PEB (lettre A-G pour l'existant, indicateurs Ew/Espec pour le neuf) explicitée dans le README — aucune comparaison chiffrée entre les deux sans cette mise en garde.
- Aucune donnée brute ni secret commité sans vérification préalable des conditions de réutilisation ODWB.
- Commits atomiques avec messages conventionnels.

## Pour aller plus loin (optionnel)

- Ajouter une vue SQL exposant un "score de priorité de rénovation" par commune.
- Activer l'extension spatiale de DuckDB pour une jointure géographique directe (ex. bâtiments PEB agrégés par commune à partir de leurs limites administratives), plutôt qu'une jointure sur un simple code INS — pratique du DuckDB spatial resté non couvert ailleurs dans le parcours de compétences.
