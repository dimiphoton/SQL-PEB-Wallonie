-- Requêtes métier PEB Wallonie (DuckDB)
--
-- Prérequis : data/processed/peb_wallonie.duckdb (python scripts/etl_odwb.py)
-- Exécution : python scripts/run_queries.py
--   ou une instruction à la fois dans un client DuckDB (chaque requête finit par ;).
--
-- Pont neuf vs existant = Espec (kWh/m².an), pas Ew (absent de l'open data)
-- et pas la part de G (0 % dans le neuf). Voir README et docs/exploration.md.
-- Grain = un certificat. Espec hors [-200, 1500] déjà mis à NULL à l'ETL.

-- Q01 — Portrait wallon : volumes, Espec, passoires
-- Répond : à quoi ressemble le parc certifié, neuf vs existant ?
-- Utile : pose le dénominateur avant tout classement de communes.
-- Garde-fou : le % de F/G n'est PAS comparable entre régimes (neuf ≈ 0 % de G).
SELECT
    v.regime,
    count(*) AS n_certificats,
    round(median(v.espec), 1) AS median_espec,
    round(avg(v.espec), 1) AS mean_espec,
    round(
        100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
        1
    ) AS pct_passoire_fg,
    round(
        100.0 * count(*) FILTER (WHERE l.label_id = 'G') / count(*),
        1
    ) AS pct_g
FROM v_certificats AS v
LEFT JOIN label_peb AS l ON l.label_id = v.label_id
GROUP BY v.regime
ORDER BY v.regime;


-- Q02 — Top 10 communes, pire performance de l'existant
-- Répond : où le parc ancien est-il le plus énergivore ?
-- Utile : prioriser les communes pour un acteur public (primes, audits).
-- Médiane plutôt que moyenne : plus robuste aux G encore hauts après l'ETL.
SELECT
    c.nom AS commune,
    c.province_id AS province,
    count(*) AS n_certificats,
    round(median(e.espec), 1) AS median_espec,
    round(avg(e.espec), 1) AS mean_espec,
    round(
        100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
        1
    ) AS pct_passoire_fg
FROM certificats_existant AS e
JOIN commune AS c ON c.mun_code = e.mun_code
LEFT JOIN label_peb AS l ON l.label_id = e.label_id
GROUP BY c.nom, c.province_id
ORDER BY median_espec DESC
LIMIT 10;


-- Q03 — Écart Espec neuf vs existant par province
-- Répond : le neuf performe-t-il vraiment mieux, et où l'écart est-il le plus
--          marqué ? (question imposée par le brief)
-- Utile : un écart large + un existant médiocre = gisement de rénovation.
-- Garde-fou : on compare l'Espec, pas les labels. Protocoles distincts.
-- Fenêtre : RANK du plus grand écart au plus petit.
WITH by_regime AS (
    SELECT
        province_id,
        regime,
        count(*) AS n_certificats,
        median(espec) AS median_espec
    FROM v_certificats
    WHERE province_id IS NOT NULL
      AND espec IS NOT NULL
    GROUP BY province_id, regime
),
pivoted AS (
    SELECT
        e.province_id AS province,
        e.n_certificats AS n_existant,
        n.n_certificats AS n_neuf,
        round(e.median_espec, 1) AS median_existant,
        round(n.median_espec, 1) AS median_neuf,
        round(e.median_espec - n.median_espec, 1) AS gap_espec
    FROM by_regime AS e
    JOIN by_regime AS n
        ON e.province_id = n.province_id
    WHERE e.regime = 'existant'
      AND n.regime = 'neuf'
)
SELECT
    province,
    n_existant,
    n_neuf,
    median_existant,
    median_neuf,
    gap_espec,
    rank() OVER (ORDER BY gap_espec DESC) AS rang_ecart
FROM pivoted
ORDER BY gap_espec DESC;


-- Q04 — Évolution annuelle des certificats (avec variation YoY)
-- Répond : le rythme de certification se maintient-il, et depuis quand le neuf
--          est-il massivement enregistré ?
-- Utile : un creux 2020 ou un pic récent change la lecture d'un stock « figé ».
-- Fenêtre : LAG pour le % d'une année sur l'autre, par régime.
-- 2010 existant et 2012–2013 neuf : montée en charge, YoY non interprétable.
WITH annual AS (
    SELECT
        regime,
        annee_certification AS annee,
        count(*) AS n_certificats,
        round(median(espec), 1) AS median_espec
    FROM v_certificats
    GROUP BY regime, annee_certification
)
SELECT
    regime,
    annee,
    n_certificats,
    median_espec,
    round(
        100.0 * (
            n_certificats
            - lag(n_certificats) OVER (PARTITION BY regime ORDER BY annee)
        ) / lag(n_certificats) OVER (PARTITION BY regime ORDER BY annee),
        1
    ) AS yoy_pct
FROM annual
ORDER BY regime, annee;


-- Q05 — Maisons vs appartements, existant et neuf
-- Répond : le type de logement change-t-il l'Espec, des deux côtés ?
-- Utile : une politique « passoires » visera surtout les maisons existantes.
-- Collectif : présent côté existant seulement (pas de code neuf équivalent).
SELECT
    v.regime,
    t.libelle AS type_logement,
    count(*) AS n_certificats,
    round(median(v.espec), 1) AS median_espec,
    round(
        100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
        1
    ) AS pct_passoire_fg
FROM v_certificats AS v
JOIN type_logement AS t ON t.type_logement_id = v.type_logement_id
LEFT JOIN label_peb AS l ON l.label_id = v.label_id
GROUP BY v.regime, t.libelle
ORDER BY v.regime, median_espec DESC;


-- Q06 — Âge du bâti existant (ères, pas 400 libellés de période)
-- Répond : le gisement de rénovation est-il surtout dans le pré-1971 ?
-- Utile : caler un programme sur l'âge du stock, pas seulement la commune.
-- ~47 % sans période ni année → « période inconnue ». Le libellé ODWB
-- « avant 1971 » (134 k lignes) n'est pas une ère : on le garde à part,
-- sinon il gonflerait artificiellement 1946-1970.
-- Année de référence : année renseignée, sinon bornes du libellé.
WITH with_year AS (
    SELECT
        e.espec,
        l.est_passoire,
        e.periode_construction,
        COALESCE(
            e.annee_construction,
            try_cast(e.periode_construction AS INTEGER),
            CASE
                WHEN e.periode_construction LIKE '%-%'
                    THEN try_cast(
                        split_part(e.periode_construction, '-', 1) AS INTEGER
                    )
                WHEN e.periode_construction LIKE 'avant %'
                     AND e.periode_construction <> 'avant 1971'
                    THEN try_cast(
                        replace(e.periode_construction, 'avant ', '') AS INTEGER
                    ) - 1
                WHEN e.periode_construction LIKE 'après %'
                    THEN try_cast(
                        replace(e.periode_construction, 'après ', '') AS INTEGER
                    )
            END
        ) AS annee_ref
    FROM certificats_existant AS e
    LEFT JOIN label_peb AS l ON l.label_id = e.label_id
),
with_era AS (
    SELECT
        espec,
        est_passoire,
        CASE
            WHEN periode_construction = 'avant 1971'
                THEN 'avant 1971 (âge imprécis)'
            WHEN annee_ref IS NULL THEN 'période inconnue'
            WHEN annee_ref < 1946 THEN 'avant 1946'
            WHEN annee_ref < 1971 THEN '1946-1970'
            WHEN annee_ref < 1991 THEN '1971-1990'
            WHEN annee_ref < 2006 THEN '1991-2005'
            ELSE '2006 et après'
        END AS ere
    FROM with_year
)
SELECT
    ere,
    count(*) AS n_certificats,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct_stock,
    round(median(espec), 1) AS median_espec,
    round(
        100.0 * count(*) FILTER (WHERE est_passoire) / count(*),
        1
    ) AS pct_passoire_fg
FROM with_era
GROUP BY ere
ORDER BY
    CASE ere
        WHEN 'avant 1946' THEN 1
        WHEN '1946-1970' THEN 2
        WHEN 'avant 1971 (âge imprécis)' THEN 3
        WHEN '1971-1990' THEN 4
        WHEN '1991-2005' THEN 5
        WHEN '2006 et après' THEN 6
        ELSE 7
    END;


-- Q07 — Système de chauffage de l'existant
-- Répond : un poêle ou un convecteur pèse-t-il autant qu'une chaudière sur l'Espec ?
-- Utile : levier technique (PAC, réseau) vs levier bâti (isolation).
-- Les PAC existantes (médiane ~145) se rapprochent du neuf ; les poêles non.
-- Fenêtre : rang du plus énergivore au plus sobre, hors modalités rares (< 500).
WITH by_system AS (
    SELECT
        CASE e.systeme_chauffage
            WHEN 'BOILER' THEN 'chaudière'
            WHEN 'STOVE' THEN 'poêle'
            WHEN 'ELECTRIC' THEN 'électrique direct'
            WHEN 'HEAT_PUMP' THEN 'pompe à chaleur'
            WHEN 'BUILD_IN_FIRE' THEN 'foyer intégré'
            WHEN 'EXTERNAL_SUPPLY' THEN 'réseau / externe'
            WHEN 'NONE' THEN 'aucun'
            WHEN 'COGENERATION' THEN 'cogénération'
            ELSE 'autre'
        END AS chauffage,
        count(*) AS n_certificats,
        round(median(e.espec), 1) AS median_espec,
        round(
            100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
            1
        ) AS pct_passoire_fg
    FROM certificats_existant AS e
    LEFT JOIN label_peb AS l ON l.label_id = e.label_id
    GROUP BY 1
)
SELECT
    chauffage,
    n_certificats,
    median_espec,
    pct_passoire_fg,
    rank() OVER (ORDER BY median_espec DESC) AS rang_espec
FROM by_system
WHERE n_certificats >= 500
ORDER BY median_espec DESC;


-- Q08 — Trois communes les plus « passoires » de chaque province
-- Répond : dans chaque province, où concentrer d'abord les audits ?
-- Utile : un classement wallon unique noie Liège/Hainaut sous leur poids
--         démographique ; le rang *intra-province* corrige ça.
-- Fenêtres : RANK dans la province + écart en points vs la moyenne provinciale.
-- QUALIFY : filtre sur la fenêtre sans CTE supplémentaire (idiome DuckDB).
WITH commune_stats AS (
    SELECT
        c.province_id AS province,
        c.nom AS commune,
        count(*) AS n_certificats,
        round(median(e.espec), 1) AS median_espec,
        round(
            100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
            1
        ) AS pct_passoire_fg
    FROM certificats_existant AS e
    JOIN commune AS c ON c.mun_code = e.mun_code
    LEFT JOIN label_peb AS l ON l.label_id = e.label_id
    GROUP BY c.province_id, c.nom
)
SELECT
    province,
    commune,
    n_certificats,
    median_espec,
    pct_passoire_fg,
    rank() OVER (
        PARTITION BY province ORDER BY pct_passoire_fg DESC
    ) AS rang_province,
    round(
        pct_passoire_fg - avg(pct_passoire_fg) OVER (PARTITION BY province),
        1
    ) AS ecart_vs_province_pp
FROM commune_stats
QUALIFY rang_province <= 3
ORDER BY province, rang_province;


-- Q09 — Dix communes où l'écart Espec neuf / existant est le plus large
-- Répond : où le neuf « décroche » le plus du parc ancien (même thermomètre Espec) ?
-- Utile : cible mixte rénovation + contrôle du neuf, à la commune.
-- Seuil : au moins 50 certificats neufs (toutes les communes en ont ≥ 46).
-- Garde-fou : même que Q03 — Espec seulement, protocoles distincts.
WITH by_regime AS (
    SELECT
        mun_code,
        regime,
        count(*) AS n_certificats,
        median(espec) AS median_espec
    FROM v_certificats
    WHERE mun_code IS NOT NULL
      AND espec IS NOT NULL
    GROUP BY mun_code, regime
)
SELECT
    c.nom AS commune,
    c.province_id AS province,
    e.n_certificats AS n_existant,
    n.n_certificats AS n_neuf,
    round(e.median_espec, 1) AS median_existant,
    round(n.median_espec, 1) AS median_neuf,
    round(e.median_espec - n.median_espec, 1) AS gap_espec
FROM by_regime AS e
JOIN by_regime AS n ON e.mun_code = n.mun_code
JOIN commune AS c ON c.mun_code = e.mun_code
WHERE e.regime = 'existant'
  AND n.regime = 'neuf'
  AND n.n_certificats >= 50
ORDER BY gap_espec DESC
LIMIT 10;


-- Q10 — Où sont les m² de passoires (F/G), pas seulement les certificats
-- Répond : quelles communes concentrent le volume à isoler ?
-- Utile : Q02 classe au taux (petite commune très mauvaise) ; ici on classe
--         à la surface chauffée des F/G (impact agrégé d'un programme).
-- Les grandes villes (Liège, Charleroi, Namur…) sortent par le volume.
SELECT
    c.nom AS commune,
    c.province_id AS province,
    count(*) FILTER (WHERE l.est_passoire) AS n_passoires,
    round(sum(e.surface_chauffee) FILTER (WHERE l.est_passoire))::BIGINT AS m2_passoires,
    round(
        100.0 * sum(e.surface_chauffee) FILTER (WHERE l.est_passoire)
        / sum(e.surface_chauffee),
        1
    ) AS pct_m2_passoires
FROM certificats_existant AS e
JOIN commune AS c ON c.mun_code = e.mun_code
LEFT JOIN label_peb AS l ON l.label_id = e.label_id
GROUP BY c.nom, c.province_id
ORDER BY m2_passoires DESC
LIMIT 10;


-- Q11 — Score de priorité de rénovation (vue stretch)
-- Répond : comment fusionner le classement « taux » (Q02) et le classement
--          « m² » (Q10) en une seule liste actionnable ?
-- Utile : un acteur public qui doit arbitrer budget (volume) et équité (taux).
-- Pondération figée dans v_priorite_renovation : 60 % volume, 40 % taux.
-- rang_pct_* = percent_rank × 100 (0 = plus petit, 100 = plus grand).
-- Charleroi / Liège ne sont pas #1 : volume max, mais taux proche de la
-- moyenne wallonne. Colfontaine combine les deux (Borinage). Pour un
-- budget calé sur les m² seuls, voir Q10.
SELECT
    commune,
    province,
    n_certificats,
    median_espec,
    pct_passoire_fg,
    m2_passoires,
    rang_pct_volume,
    rang_pct_taux,
    score_priorite,
    rang_priorite
FROM v_priorite_renovation
ORDER BY rang_priorite
LIMIT 15;
