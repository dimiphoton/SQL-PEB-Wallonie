# Performance énergétique des bâtiments wallons (PEB) — analyse SQL

## Contexte et problématique

La Wallonie publie en open data les certificats de performance énergétique des bâtiments (PEB), un indicateur clé de la qualité du bâti et un levier majeur de la politique climatique régionale. Un analyste travaillant pour une administration, un bureau d'audit énergétique ou un fournisseur d'énergie doit pouvoir répondre rapidement à des questions comme : quelles communes concentrent le plus de passoires énergétiques ? quel est le potentiel de rénovation par province ?

Ce projet est volontairement centré sur le SQL : c'est le repo où la rigueur de modélisation et la complexité des requêtes doivent parler d'elles-mêmes. travail solo, pas de PR

## Objectif

Construire une base de données relationnelle propre à partir des données PEB et y répondre à une série de questions métier via des requêtes SQL avancées, sans recourir à un outil de cartographie.

## Compétences démontrées

- Modélisation relationnelle (normalisation, clés, table de dimension commune/province)
- Requêtes SQL avancées : jointures multiples, fonctions de fenêtrage, sous-requêtes, CTE
- Agrégations à plusieurs niveaux géographiques (commune, province, région) — uniquement via des clés et des `GROUP BY`, sans SIG
- Détection et traitement des anomalies de données (doublons, valeurs aberrantes)

## Sources de données

- **ODWB — Open Data Wallonie-Bruxelles** ([odwb.be](https://www.odwb.be)), données PEB publiées par le SPW Énergie : certificats de performance énergétique des bâtiments, avec localisation à la commune.

## Livrables attendus

1. Script d'import et de nettoyage des données PEB.
2. Base SQL avec schéma documenté (diagramme entité-relation dans le README).
3. Un fichier `queries.sql` regroupant 8 à 10 requêtes commentées répondant à des questions métier précises (ex. : top 10 des communes avec la plus mauvaise performance moyenne, évolution du nombre de certificats par an, répartition par type de bâtiment).
4. Une synthèse courte traduisant 2-3 résultats SQL en recommandations pour un acteur public ou privé.

## Structure de repo attendue

```
projet-peb-wallonie-sql/
├── README.md
├── data/
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── src/
│   └── import_clean.py
└── diagrams/
    └── modele_relationnel.png
```

## Critères de qualité (definition of done)

- Chaque requête SQL est commentée : ce qu'elle répond, pourquoi c'est utile.
- Le schéma relationnel est justifié dans le README (pourquoi ces tables, ces clés).
- Au moins une requête utilise une fonction de fenêtrage ou une CTE complexe — pas seulement des `GROUP BY` simples.

## Pour aller plus loin (optionnel)

- Ajouter une vue SQL exposant un "score de priorité de rénovation" par commune.
