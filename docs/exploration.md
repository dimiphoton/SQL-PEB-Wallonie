# Exploration des extraits PEB ODWB

Profilage des deux jeux publiés par le SPW Énergie (métadonnées
traitées le 2026-06-22). Agrégats obtenus via l’API Explore v2.1, sur
les mêmes extraits que les exports Parquet de `data/raw/`.

## Volumes

| Jeu | Identifiant ODWB | Lignes | IDs distincts | Codes INS | Provinces |
|---|---|---|---|---|---|
| Résidentiel existant | `peb-certification-residentielle-batiment-existant` | 874 605 | 842 937 (`id01_building`) | 258 | 5 |
| Résidentiel neuf | `peb-batiments-residentiels-neufs` | 110 855 | 110 439 (`pebunit_id`) | 258 | 5 |

Licence CC BY. Granule observé : **un certificat**, pas un bâtiment —
des identifiants se répètent (re-certifications probables : ~31 700
lignes en trop côté existant, ~400 côté neuf).

## Schémas

**Existant** — `id01_building`, `communes`, `e_spec` (entier),
`e_spec_label`, `destination`, `free_facade`, `build_period`,
`build_period_v2`, `build_year`, `build_after`, `certificate_date`,
`device`, `arr_name_fr`, `province`, `mun_code`, `city`,
`total_heated_floor`.

**Neuf** — `pebunit_id`, `dategeneration`, `annecertif`,
`cert_new_building_year_construct`, `commune`, `espec` (**texte**),
`espec_label`, `typeresidence`, `generator_type`,
`generator_fuel_type`, `mun_code`, `province`, `arr_name_fr`.

Aucune colonne `Ew` des deux côtés.

## Régimes de notation — ce que les colonnes disent vraiment

Le brief (`brief/sql-peb-batiments-wallonie.md`) oppose lettre A–G
(existant) et indicateurs Ew / Espec (neuf). **L’open data ne reflète
pas cette opposition.**

- Les deux jeux ont un Espec en kWh/m².an **et** un label lettre.
- Ew, indicateur réglementaire du neuf, **n’est pas publié**.
- Les seuils empiriques du label existant collent à l’échelle wallonne
  classique :

| Label | Espec min | Espec max | n existant | n neuf |
|---|---|---|---|---|
| ++A | ≤ 0 (négatif possible) | 0 | 261 | 3 514 |
| +A | 0 | 45 | 1 528 | 10 611 |
| A | 45 | 85 | 12 224 | 38 228 |
| B | 85 | 170 | 113 645 | 58 267 |
| C | 170 | 255 | 154 535 | 199 |
| D | 255 | 340 | 157 670 | 27 |
| E | 340 | 425 | 138 671 | 8 |
| F | 425 | 510 | 113 190 | 1 |
| G | 510 | 8 427 | 182 881 | 0 |

Côté neuf, les ++A échantillonnés ont un Espec négatif ; les C
échantillonnés sont autour de 172–193 kWh/m².an — même bande que
l’existant. Le **pont numérique légitime est l’Espec**, éventuellement
le label (même alphabet). Ce n’est pas une fusion des protocoles :
certificat d’existant ≠ certificat de construction neuve, et le neuf
est presque entièrement A/B (99,8 % en ++A…B, zéro G).

Comparer la part de G entre les deux faits serait tautologique.
Comparer des médianes d’Espec par commune, à protocoles distincts
rappelés en légende, est défendable.

## Qualité (à traiter à l’ETL, pas ici)

- **Espec existant** : 250 valeurs < 0 (dont un min à −62 738, aberrant) ;
  622 valeurs > 1 500 ; moyenne 372 kWh/m².an.
- **Espec neuf** : stocké en texte (`"127"`, `"-27"`) → `CAST` à
  l’import.
- **Géographie** : `mun_code` rempli à 100 % sur le neuf, 618 manquants
  sur l’existant. Clé de jointure naturelle vers une dimension commune.
  Noms (`communes` vs `commune`) à normaliser, pas à utiliser comme clé.
- **Période de construction (existant)** : `build_period` ~77 % vide,
  `build_period_v2` ~84 % vide, `build_year` ~84 % vide — cascade de
  fallback, pas une seule colonne.
- **Types de logement** : codes anglais (`SINGLE_FAMILY_HOUSE`,
  `APARTMENT`, `COMMUNAL`) vs libellés français (`Maison unifamiliale`,
  `Appartement`) → table de correspondance.
- **Vecteur énergétique (neuf)** : `generator_fuel_type` manquant pour
  ~26 % des lignes (souvent pompes à chaleur).
- **Dates** : existant en texte `JJ-MM-AA` ; neuf en date ISO + année
  de certification 2012–2026.

## Implications pour le schéma étoile

Implémenté dans `sql/schema.sql` :

1. Dimensions partagées : `commune` (PK `mun_code`), `province`,
   `label_peb`, `type_logement` (après mapping).
2. Deux faits : `certificats_existant`, `certificats_neuf` — grain =
   certificat (PK technique ; l’extrait Parquet a des IDs uniques).
3. Ne pas coller Ew (absent). Pont documenté = Espec via la vue
   `v_certificats` (+ label, avec biais de population).
4. Pas de dédup à l’ETL : tous les certificats sont chargés. Un filtre
   « plus récent » se fera en fenêtre SQL à l’étape requêtes si besoin.

## Note après import (2026-08-29)

L’extrait Parquet a les **mêmes volumes** que l’API (874 605 / 110 855),
mais les IDs sources y sont **uniques** — pas de re-certification
visible. 261 codes INS (l’API en dénombrait 258). Espec mis à NULL si
hors [-200, 1500] : 631 existants, 5 neufs. Règles : `sql/load.sql`.
Base : `data/processed/peb_wallonie.duckdb` (`scripts/etl_odwb.py`).

## Stretch spatial (2026-08-29)

Aucune colonne de coordonnées dans les extraits résidentiels (anonymat).
Les limites communales officielles (SPW / SPF Finances, ADMUKEY = code
INS, Lambert 2008) sont chargées via l'extension DuckDB `spatial`
(`scripts/load_spatial.py`). Ce que le `mun_code` ne donne pas :
superficie, densité de passoires au km², communes `ST_Touches`. Pas de
carte. Requêtes : `sql/spatial.sql`.
