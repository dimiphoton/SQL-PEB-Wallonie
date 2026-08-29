-- Schéma étoile PEB Wallonie (DuckDB)
--
-- À exécuter sur une base vide : scripts/etl_odwb.py lance ce fichier
-- puis sql/load.sql.
-- Les dimensions de référence (province, label, type de logement) sont seedées
-- ici. commune et les deux faits restent vides jusqu'à l'import.
--
--          province 1 ── * commune
--                             ▲
--          label_peb ─────────┼──── certificats_existant
--          type_logement ─────┤
--                             └──── certificats_neuf
--
-- Pont neuf vs existant = Espec (kWh/m².an), pas Ew (absent de l'open data).
-- Grain des faits = un certificat (les id sources se répètent : re-certifs).
-- Vocabulaires chauffage distincts → attributs dégénérés, pas une dim partagée.
-- Stretch : vue v_priorite_renovation (score 60 % volume / 40 % taux).
-- Stretch spatial : sql/spatial.sql + scripts/load_spatial.py (limites SPW).
--
-- Voir docs/exploration.md et docs/decisions.md.

DROP VIEW IF EXISTS v_priorite_renovation;
DROP VIEW IF EXISTS v_certificats;
DROP TABLE IF EXISTS certificats_existant;
DROP TABLE IF EXISTS certificats_neuf;
DROP TABLE IF EXISTS commune;
DROP TABLE IF EXISTS type_logement;
DROP TABLE IF EXISTS label_peb;
DROP TABLE IF EXISTS province;


-- ---------------------------------------------------------------------------
-- Dimensions partagées
-- ---------------------------------------------------------------------------

CREATE TABLE province (
    province_id VARCHAR PRIMARY KEY,  -- libellé ODWB, clé de jointure directe
    nis_prefixe VARCHAR NOT NULL      -- 1er chiffre du code INS commune
);

INSERT INTO province (province_id, nis_prefixe) VALUES
    ('Brabant Wallon', '2'),
    ('Hainaut',        '5'),
    ('Liège',          '6'),
    ('Luxembourg',     '8'),
    ('Namur',          '9');


CREATE TABLE commune (
    mun_code       VARCHAR PRIMARY KEY,  -- code INS à 5 chiffres, ex. '92094'
    nom            VARCHAR NOT NULL,     -- libellé canonique choisi à l'ETL
    arrondissement VARCHAR,
    province_id    VARCHAR NOT NULL,
    FOREIGN KEY (province_id) REFERENCES province (province_id)
);


-- Seuils empiriques observés sur l'existant (docs/exploration.md).
-- ++A peut être négatif (production > consommation). G n'a pas de plafond.
CREATE TABLE label_peb (
    label_id     VARCHAR PRIMARY KEY,  -- ++A … G, identique des deux côtés
    rang         INTEGER NOT NULL,     -- 1 = meilleur, 9 = pire (ORDER BY)
    espec_min    INTEGER,              -- kWh/m².an, NULL = pas de plancher (++A)
    espec_max    INTEGER,              -- kWh/m².an, NULL = pas de plafond (G)
    est_passoire BOOLEAN NOT NULL      -- F et G : cibles typiques de rénovation
);

INSERT INTO label_peb (label_id, rang, espec_min, espec_max, est_passoire) VALUES
    ('++A', 1, NULL,    0, FALSE),
    ('+A',  2,    0,   45, FALSE),
    ('A',   3,   45,   85, FALSE),
    ('B',   4,   85,  170, FALSE),
    ('C',   5,  170,  255, FALSE),
    ('D',   6,  255,  340, FALSE),
    ('E',   7,  340,  425, FALSE),
    ('F',   8,  425,  510, TRUE),
    ('G',   9,  510, NULL, TRUE);


-- Mapping anglais (existant) ↔ français (neuf) vers un code canonique.
CREATE TABLE type_logement (
    type_logement_id VARCHAR PRIMARY KEY,  -- maison | appartement | collectif
    libelle          VARCHAR NOT NULL,
    code_existant    VARCHAR,              -- destination ODWB (NULL si absent)
    code_neuf        VARCHAR               -- typeresidence ODWB (NULL si absent)
);

INSERT INTO type_logement (
    type_logement_id, libelle, code_existant, code_neuf
) VALUES
    ('maison',      'Maison unifamiliale', 'SINGLE_FAMILY_HOUSE', 'Maison unifamiliale'),
    ('appartement', 'Appartement',         'APARTMENT',           'Appartement'),
    ('collectif',   'Logement collectif',  'COMMUNAL',            NULL);


-- ---------------------------------------------------------------------------
-- Faits — PK technique : l'id source n'est pas unique (re-certifications)
-- ---------------------------------------------------------------------------

CREATE TABLE certificats_existant (
    certificat_id         INTEGER PRIMARY KEY,  -- attribué par l'ETL
    id_batiment           BIGINT NOT NULL,      -- id01_building (peut se répéter)
    date_certificat       DATE,                 -- parsée depuis JJ-MM-AA
    mun_code              VARCHAR,              -- NULL possible (~618 lignes)
    province_id           VARCHAR,              -- dénormalisé (étoile, pas flocon)
    label_id              VARCHAR,
    type_logement_id      VARCHAR,
    espec                 DOUBLE,               -- kWh/m².an ; aberrants à filtrer à l'ETL
    surface_chauffee      DOUBLE,               -- m² (total_heated_floor)
    type_facade           VARCHAR,              -- DETACHED, THREE_FREE, TWO_FREE, ONE_FREE
    periode_construction  VARCHAR,              -- cascade ETL : v2 > année > période > après
    annee_construction    INTEGER,
    systeme_chauffage     VARCHAR,              -- device : BOILER, STOVE, HEAT_PUMP…
    FOREIGN KEY (mun_code)         REFERENCES commune (mun_code),
    FOREIGN KEY (province_id)      REFERENCES province (province_id),
    FOREIGN KEY (label_id)         REFERENCES label_peb (label_id),
    FOREIGN KEY (type_logement_id) REFERENCES type_logement (type_logement_id)
);

CREATE TABLE certificats_neuf (
    certificat_id         INTEGER PRIMARY KEY,
    id_unite              BIGINT NOT NULL,      -- pebunit_id (peut se répéter)
    date_certificat       DATE,                 -- dategeneration (ISO)
    annee_certification   INTEGER,              -- annecertif
    annee_construction    INTEGER,              -- cert_new_building_year_construct
    mun_code              VARCHAR,              -- rempli à 100 % dans l'extrait
    province_id           VARCHAR,
    label_id              VARCHAR,
    type_logement_id      VARCHAR,
    espec                 DOUBLE,               -- CAST du texte ODWB ("127", "-27")
    type_generateur       VARCHAR,              -- vocabulaire propre au neuf
    vecteur_energetique   VARCHAR,              -- ~26 % manquant (souvent PAC)
    FOREIGN KEY (mun_code)         REFERENCES commune (mun_code),
    FOREIGN KEY (province_id)      REFERENCES province (province_id),
    FOREIGN KEY (label_id)         REFERENCES label_peb (label_id),
    FOREIGN KEY (type_logement_id) REFERENCES type_logement (type_logement_id)
);


-- ---------------------------------------------------------------------------
-- Pont d'analyse : mêmes dimensions, même Espec, régime rappelé en légende
-- Ne pas s'en servir pour comparer la part de G (0 % dans le neuf).
-- ---------------------------------------------------------------------------

CREATE VIEW v_certificats AS
SELECT
    'existant' AS regime,
    certificat_id,
    id_batiment AS id_source,
    date_certificat,
    EXTRACT(YEAR FROM date_certificat)::INTEGER AS annee_certification,
    mun_code,
    province_id,
    label_id,
    type_logement_id,
    espec
FROM certificats_existant
UNION ALL
SELECT
    'neuf',
    certificat_id,
    id_unite,
    date_certificat,
    annee_certification,
    mun_code,
    province_id,
    label_id,
    type_logement_id,
    espec
FROM certificats_neuf;


-- ---------------------------------------------------------------------------
-- Stretch : score de priorité de rénovation par commune (parc existant)
--
-- Q02 classe au taux F/G (Hastière) ; Q10 classe aux m² (Charleroi).
-- La reco de synthèse dit : le budget suit le volume, l'équité le taux.
-- Pondération : 60 % volume (percent_rank des m² F/G) + 40 % taux.
-- percent_rank = 0 pour le plus petit, 1 pour le plus grand (261 communes).
-- n_certificats reste exposé : un taux sur un petit effectif se lit avec prudence.
-- ---------------------------------------------------------------------------

CREATE VIEW v_priorite_renovation AS
WITH stats AS (
    SELECT
        c.mun_code,
        c.nom AS commune,
        c.province_id AS province,
        count(*) AS n_certificats,
        median(e.espec) AS median_espec,
        100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*)
            AS pct_passoire_fg,
        coalesce(
            sum(e.surface_chauffee) FILTER (WHERE l.est_passoire),
            0
        ) AS m2_passoires
    FROM certificats_existant AS e
    JOIN commune AS c ON c.mun_code = e.mun_code
    LEFT JOIN label_peb AS l ON l.label_id = e.label_id
    GROUP BY c.mun_code, c.nom, c.province_id
),
ranked AS (
    SELECT
        *,
        percent_rank() OVER (ORDER BY m2_passoires) AS pr_volume,
        percent_rank() OVER (ORDER BY pct_passoire_fg) AS pr_taux
    FROM stats
)
SELECT
    mun_code,
    commune,
    province,
    n_certificats,
    round(median_espec, 1) AS median_espec,
    round(pct_passoire_fg, 1) AS pct_passoire_fg,
    round(m2_passoires)::BIGINT AS m2_passoires,
    round(100 * pr_volume, 1) AS rang_pct_volume,
    round(100 * pr_taux, 1) AS rang_pct_taux,
    round(100 * (0.6 * pr_volume + 0.4 * pr_taux), 1) AS score_priorite,
    rank() OVER (
        ORDER BY 0.6 * pr_volume + 0.4 * pr_taux DESC
    ) AS rang_priorite
FROM ranked;
