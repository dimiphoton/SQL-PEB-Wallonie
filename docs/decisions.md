# Décisions

| Date | Décision | Alternative envisagée | Raison |
|---|---|---|---|
| 2026-08-25 | DuckDB comme moteur SQL | SQLite ; PostgreSQL | DuckDB est un moteur analytique natif (fenêtrage et CTE de premier ordre, pas des extensions tardives). Zéro serveur, reproductible en une commande. PostgreSQL est déjà représenté dans d'autres projets du portfolio (PostGIS) ; DuckDB diversifie le signal. |
| 2026-08-25 | Deux tables de faits (existant + neuf) partageant les mêmes dimensions | Une seule table plate mélangeant les deux régimes ; existant seulement | Le brief d'origine ne couvrait que l'existant. Le schéma étoile rend les jointures légitimes et ouvre la question « le neuf performe-t-il vraiment mieux, et où l'écart est-il le plus marqué ? ». |
| 2026-08-25 | Ne pas comparer lettre A–G et indicateurs Ew/Espec terme à terme | Harmoniser de force les deux notations dans une colonne unique | Ce sont deux régimes de certification distincts. L'incomparabilité doit être vérifiée sur les colonnes réelles à l'exploration, puis documentée. Un éventuel pont (ex. Espec en kWh/m².an si présent des deux côtés) sera justifié, pas présumé. |
| 2026-08-25 | Python pour l'ETL uniquement ; analyse 100 % SQL | Pandas pour les agrégations métier ; notebook unique | Le brief est un démonstrateur SQL. Pandas resterait un raccourci qui dilue le signal visé par le portfolio. |
| 2026-08-25 | Pas de cartographie / SIG | Folium, GeoPandas, PostGIS | Contrainte explicite du brief : agrégations géographiques via clés et `GROUP BY` seulement. |
