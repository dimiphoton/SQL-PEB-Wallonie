-- Chargement PEB Wallonie (DuckDB)
--
-- Prérequis : schéma déjà exécuté ; vues raw_existant et raw_neuf
-- (Parquet ODWB) créées par scripts/etl_odwb.py.
--
-- Règles :
--   * Grain = un certificat. Pas de dédup sur l'id source (déjà unique
--     dans l'extrait Parquet ; une fenêtre SQL pourra filtrer le plus
--     récent si un extrait futur se dédouble).
--   * Espec hors [-200, 1500] kWh/m².an → NULL (ligne conservée).
--     Les ++A négatifs modestes sont légitimes (production > conso) ;
--     -62 738 et les G > 1 500 faussent les médianes.
--   * Période de construction : cascade v2 > année > période > après.
--   * Types de logement : jointure sur type_logement (anglais ↔ français).
--   * mun_code manquant (~618 existant, Luxembourg) → NULL, pas de commune
--     inventée. Les noms de commune coïncident entre les deux extraits.

-- ---------------------------------------------------------------------------
-- Dimension commune (261 codes INS, identiques des deux côtés)
-- ---------------------------------------------------------------------------

INSERT INTO commune (mun_code, nom, arrondissement, province_id)
SELECT
    mun_code,
    any_value(nom) AS nom,
    any_value(arrondissement) AS arrondissement,
    any_value(province_id) AS province_id
FROM (
    SELECT
        mun_code,
        communes AS nom,
        arr_name_fr AS arrondissement,
        province AS province_id
    FROM raw_existant
    WHERE mun_code IS NOT NULL
    UNION ALL
    SELECT mun_code, commune, arr_name_fr, province
    FROM raw_neuf
    WHERE mun_code IS NOT NULL
)
GROUP BY mun_code;


-- ---------------------------------------------------------------------------
-- Fait existant
-- ---------------------------------------------------------------------------

INSERT INTO certificats_existant (
    certificat_id,
    id_batiment,
    date_certificat,
    mun_code,
    province_id,
    label_id,
    type_logement_id,
    espec,
    surface_chauffee,
    type_facade,
    periode_construction,
    annee_construction,
    systeme_chauffage
)
SELECT
    row_number() OVER (ORDER BY r.id01_building) AS certificat_id,
    r.id01_building,
    strptime(r.certificate_date, '%d-%m-%y')::DATE,
    r.mun_code,
    p.province_id,
    l.label_id,
    t.type_logement_id,
    CASE
        WHEN r.e_spec BETWEEN -200 AND 1500 THEN r.e_spec
    END,
    r.total_heated_floor,
    r.free_facade,
    -- Libellé lisible : BETWEEN_1919_AND_1945 → 1919-1945, BEFORE_x → avant x
    COALESCE(
        replace(replace(replace(
            r.build_period_v2, 'BETWEEN_', ''), '_AND_', '-'), 'BEFORE_', 'avant '),
        CASE
            WHEN r.build_year BETWEEN 1600 AND 2026
            THEN CAST(CAST(r.build_year AS INTEGER) AS VARCHAR)
        END,
        replace(replace(replace(replace(
            r.build_period, 'BETWEEN_', ''), '_AND_', '-'),
            'BEFORE_', 'avant '), 'AFTER_', 'après '),
        CASE
            WHEN r.build_after IS NOT NULL THEN 'après ' || r.build_after
        END
    ),
    CASE
        WHEN r.build_year BETWEEN 1600 AND 2026
        THEN CAST(r.build_year AS INTEGER)
    END,
    r.device
FROM raw_existant AS r
LEFT JOIN province p ON p.province_id = r.province
LEFT JOIN label_peb l ON l.label_id = r.e_spec_label
LEFT JOIN type_logement t ON t.code_existant = r.destination;


-- ---------------------------------------------------------------------------
-- Fait neuf
-- ---------------------------------------------------------------------------

INSERT INTO certificats_neuf (
    certificat_id,
    id_unite,
    date_certificat,
    annee_certification,
    annee_construction,
    mun_code,
    province_id,
    label_id,
    type_logement_id,
    espec,
    type_generateur,
    vecteur_energetique
)
SELECT
    row_number() OVER (ORDER BY r.pebunit_id) AS certificat_id,
    r.pebunit_id,
    r.dategeneration,
    CAST(r.annecertif AS INTEGER),
    CASE
        WHEN try_cast(r.cert_new_building_year_construct AS INTEGER)
             BETWEEN 1990 AND 2026
        THEN try_cast(r.cert_new_building_year_construct AS INTEGER)
    END,
    r.mun_code,
    p.province_id,
    l.label_id,
    t.type_logement_id,
    CASE
        WHEN try_cast(r.espec AS DOUBLE) BETWEEN -200 AND 1500
        THEN try_cast(r.espec AS DOUBLE)
    END,
    r.generator_type,
    r.generator_fuel_type
FROM raw_neuf AS r
LEFT JOIN province p ON p.province_id = r.province
LEFT JOIN label_peb l ON l.label_id = r.espec_label
LEFT JOIN type_logement t ON t.code_neuf = r.typeresidence;
