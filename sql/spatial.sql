-- Requêtes spatiales PEB Wallonie (extension DuckDB spatial)
--
-- Prérequis :
--   python scripts/etl_odwb.py
--   python scripts/download_odwb.py   (limites-communes-wallonie.geojson)
--   python scripts/load_spatial.py
-- Exécution : python scripts/run_spatial.py
--
-- Les certificats résidentiels ODWB n'ont pas de XY (anonymisés à la commune).
-- On ne peut donc pas faire un point-in-polygon bâtiment → polygone.
-- À la place : polygones officiels SPW (ADMUKEY = mun_code, Lambert 2008),
-- puis ce que le code INS ne permet pas : superficie, densité, adjacence
-- (ST_Touches). Pas de carte — uniquement du SQL spatial.

-- S01 — Densité de passoires (m² F/G par km² de commune)
-- Répond : une petite commune dense pèse-t-elle autant qu'une grande ville
--          étendue, une fois l'aire officielle prise en compte ?
-- Utile : Q10 classe au stock de m² ; ici on rapporte ce stock au territoire.
-- ST_Area sur du Lambert 2008 (mètres) → m², divisé par 1e6 → km².
SELECT
    p.commune,
    p.province,
    p.m2_passoires,
    s.superficie_km2,
    round(p.m2_passoires / nullif(s.superficie_km2, 0))::BIGINT
        AS m2_passoire_par_km2,
    p.pct_passoire_fg,
    p.score_priorite,
    p.rang_priorite
FROM v_priorite_renovation AS p
JOIN v_commune_spatiale AS s ON s.mun_code = p.mun_code
ORDER BY m2_passoire_par_km2 DESC
LIMIT 15;


-- S02 — Communes limitrophes de Charleroi (ST_Touches)
-- Répond : autour du plus gros gisement en m², qui touche Charleroi
--          et quel est leur score de priorité ?
-- Utile : un programme « bassin de Charleroi » plutôt que la seule commune.
-- Jointure spatiale vraie : aucun code INS ne encode le voisinage.
SELECT
    voisin.nom AS commune_voisine,
    voisin.province_id AS province,
    p.pct_passoire_fg,
    p.m2_passoires,
    p.score_priorite,
    p.rang_priorite
FROM limite_communale AS coeur
JOIN commune AS c_coeur ON c_coeur.mun_code = coeur.mun_code
JOIN limite_communale AS lim
    ON ST_Touches(coeur.geom, lim.geom)
JOIN commune AS voisin ON voisin.mun_code = lim.mun_code
JOIN v_priorite_renovation AS p ON p.mun_code = voisin.mun_code
WHERE c_coeur.nom = 'Charleroi'
ORDER BY p.rang_priorite;


-- S03 — Ilots de rénovation : top quartile avec au moins 2 voisins du même quartile
-- Répond : où un programme peut-il porter sur un bloc de communes jointives
--          plutôt que sur des cibles isolées ?
-- Utile : logistique (audits, entreprises, communication) d'un seul tenant.
-- Top quartile ≈ rang_priorite ≤ 65 (261 communes).
WITH top AS (
    SELECT mun_code, commune, province, score_priorite, rang_priorite
    FROM v_priorite_renovation
    WHERE rang_priorite <= 65
)
SELECT
    a.commune,
    a.province,
    a.score_priorite,
    a.rang_priorite,
    count(DISTINCT b.commune) AS n_voisins_top,
    string_agg(b.commune, ', ' ORDER BY b.commune) AS voisins_top
FROM top AS a
JOIN limite_communale AS ga ON ga.mun_code = a.mun_code
JOIN limite_communale AS gb
    ON ST_Touches(ga.geom, gb.geom)
JOIN top AS b ON b.mun_code = gb.mun_code
GROUP BY a.commune, a.province, a.score_priorite, a.rang_priorite
HAVING count(DISTINCT b.commune) >= 2
ORDER BY n_voisins_top DESC, a.score_priorite DESC
LIMIT 15;


-- S04 — Contrôle de calage INS (ODWB) vs ADMUKEY (SPW)
-- Répond : chaque commune PEB a-t-elle un polygone, et la somme des aires
--          ressemble-t-elle à la Wallonie (~16 900 km²) ?
-- Utile : valider la jointure ADMUKEY = mun_code avant d'interpréter S01–S03.
SELECT
    count(*) AS n_communes_peb,
    count(l.mun_code) AS n_avec_geom,
    count(*) - count(l.mun_code) AS n_sans_geom,
    round(sum(ST_Area(l.geom)) / 1e6, 0)::BIGINT AS superficie_totale_km2
FROM commune AS c
LEFT JOIN limite_communale AS l ON l.mun_code = c.mun_code;
