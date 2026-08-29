---
marp: true
theme: default
paginate: true
---

# Performance énergétique des bâtiments wallons

*Analyse SQL — synthèse*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-analytics-lightgrey)
![matplotlib](https://img.shields.io/badge/matplotlib-charts-steelblue)

---

## Le problème

La Wallonie connaît la performance énergétique de ses logements grâce aux
certificats PEB, mais ces données brutes ne disent pas, à elles seules,
où concentrer les rénovations. Un analyste doit pouvoir répondre vite :
quelles communes ont le plus de passoires ? le neuf est-il vraiment
meilleur, et où l'écart est-il le plus fort ?

---

## Les données

Deux jeux open data du SPW Énergie : **875 000** certificats de logements
existants et **111 000** de logements neufs, localisés à la commune —
sans carte, uniquement par jointures SQL.

---

## Ce qu'on peut comparer

Les deux jeux parlent la même langue chiffrée (consommation annuelle au
mètre carré). En revanche, presque tout le neuf est déjà « bon » : on ne
peut pas juger les passoires du parc ancien avec le même thermomètre
que le neuf sans le dire.

---

## Ce que les chiffres disent

Un tiers du parc existant est F ou G (médiane 339 kWh/m².an) contre
~88 pour le neuf. L'écart est le plus large en Hainaut.

Les m² à isoler sont dans les **grandes villes** (Charleroi, Liège) —
pas dans les petites communes les plus mauvaises au pourcentage.

![w:720](../../pictures/readme/taux-vs-volume-passoires.png)

---

## Recommandations

**Acteur public.** Budgéter le volume (Charleroi, Liège). Traiter
Hastière et communes rurales à part, pour l'équité. La vue
`v_priorite_renovation` fusionne les deux (60 % volume, 40 % taux).
Priorité Hainaut. Ne pas piloter au pourcentage de G neuf vs existant.

**Acteur privé.** Cibler les maisons existantes chauffées au poêle ou
à l'électrique. Les pompes à chaleur du parc ancien ressemblent déjà
au neuf : ce n'est pas là que le certificat bouge le plus.
