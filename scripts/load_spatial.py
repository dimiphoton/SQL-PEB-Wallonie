"""Charge les limites communales SPW dans la base DuckDB (extension spatial)."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sql" / "schema.sql"
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "processed" / "peb_wallonie.duckdb"
GEOJSON = RAW / "limites-communes-wallonie.geojson"

# Wallonie ~ 16 844–16 901 km² selon les millésimes de limites.
SUPERFICIE_MIN_KM2 = 16_000
SUPERFICIE_MAX_KM2 = 18_000


def compte(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    """Renvoie le scalaire d'un SELECT count(...) / agrégat à une cellule."""
    return int(con.execute(sql).fetchone()[0])


def trouver_colonne(colonnes: list[str], candidats: list[str]) -> str:
    """Retrouve un nom de colonne sans se soucier de la casse."""
    lookup = {nom.lower(): nom for nom in colonnes}
    for candidat in candidats:
        if candidat.lower() in lookup:
            return lookup[candidat.lower()]
    raise SystemExit(
        f"Colonne introuvable parmi {candidats}. ST_Read a renvoyé : {colonnes}"
    )


def assurer_vue_priorite(con: duckdb.DuckDBPyConnection) -> None:
    """(Re)crée v_priorite_renovation si la base date d'avant ce stretch."""
    texte = SCHEMA.read_text(encoding="utf-8")
    marqueur = "CREATE VIEW v_priorite_renovation"
    try:
        debut = texte.index(marqueur)
    except ValueError as exc:
        raise SystemExit("v_priorite_renovation introuvable dans sql/schema.sql") from exc
    con.execute("CREATE OR REPLACE VIEW " + texte[debut + len("CREATE VIEW ") :])


def rapport(con: duckdb.DuckDBPyConnection) -> None:
    n_poly = compte(con, "SELECT count(*) FROM limite_communale")
    n_join = compte(
        con,
        """
        SELECT count(*) FROM commune c
        JOIN limite_communale l ON l.mun_code = c.mun_code
        """,
    )
    n_sans_geom = compte(
        con,
        """
        SELECT count(*) FROM commune c
        WHERE NOT EXISTS (
            SELECT 1 FROM limite_communale l WHERE l.mun_code = c.mun_code
        )
        """,
    )
    n_orphelins_spw = compte(
        con,
        """
        SELECT count(*) FROM limite_communale l
        WHERE NOT EXISTS (
            SELECT 1 FROM commune c WHERE c.mun_code = l.mun_code
        )
        """,
    )
    superficie = compte(
        con,
        "SELECT round(sum(ST_Area(geom)) / 1e6, 0)::BIGINT FROM limite_communale",
    )
    n_touches = compte(
        con,
        """
        SELECT count(*) FROM limite_communale a
        JOIN limite_communale b
            ON ST_Touches(a.geom, b.geom) AND a.mun_code < b.mun_code
        """,
    )

    print(f"Base            : {DB_PATH.relative_to(ROOT).as_posix()}")
    print(f"Polygones       : {n_poly}")
    print(f"Jointure INS    : {n_join} communes PEB avec geom")
    print(f"Sans polygone   : {n_sans_geom}")
    print(f"SPW hors PEB    : {n_orphelins_spw}")
    print(f"Superficie      : {superficie:,} km²")
    print(f"Paires ST_Touches : {n_touches}")

    if n_poly < 250:
        raise SystemExit("Échec : trop peu de polygones chargés.")
    if n_sans_geom:
        raise SystemExit("Échec : des communes PEB n'ont pas de polygone SPW.")
    if not SUPERFICIE_MIN_KM2 <= superficie <= SUPERFICIE_MAX_KM2:
        raise SystemExit(
            f"Échec : superficie {superficie} km² hors [{SUPERFICIE_MIN_KM2}, "
            f"{SUPERFICIE_MAX_KM2}] — CRS probablement faux."
        )
    if n_touches == 0:
        raise SystemExit(
            "Échec : ST_Touches n'a trouvé aucun voisin (topologie / CRS)."
        )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not DB_PATH.exists():
        raise SystemExit("Base absente. Lancer d'abord : python scripts/etl_odwb.py")
    if not GEOJSON.exists():
        raise SystemExit(
            "GeoJSON absent. Lancer : python scripts/download_odwb.py"
        )

    con = duckdb.connect(str(DB_PATH))
    try:
        print("Extension spatial …")
        con.execute("INSTALL spatial")
        con.execute("LOAD spatial")

        print("Vue priorité …")
        assurer_vue_priorite(con)

        print("Lecture GeoJSON …")
        # as_posix() : DuckDB attend des / même sous Windows.
        con.execute(
            f"CREATE OR REPLACE TEMP VIEW raw_limites AS "
            f"SELECT * FROM ST_Read('{GEOJSON.as_posix()}')"
        )
        colonnes = [row[0] for row in con.execute("DESCRIBE raw_limites").fetchall()]
        col_mun = trouver_colonne(colonnes, ["ADMUKEY", "mun_code"])
        col_nom = trouver_colonne(colonnes, ["NAMEFRE", "nom", "name"])
        col_geom = trouver_colonne(colonnes, ["geom", "geometry", "wkb_geometry"])

        con.execute("DROP VIEW IF EXISTS v_commune_spatiale")
        con.execute("DROP TABLE IF EXISTS limite_communale")
        con.execute(
            f"""
            CREATE TABLE limite_communale AS
            SELECT
                {col_mun} AS mun_code,
                {col_nom} AS nom_officiel,
                {col_geom} AS geom
            FROM raw_limites
            WHERE {col_mun} IS NOT NULL
            """
        )
        con.execute(
            "CREATE INDEX limite_communale_gix ON limite_communale USING RTREE (geom)"
        )
        con.execute(
            """
            CREATE VIEW v_commune_spatiale AS
            SELECT
                c.mun_code,
                c.nom,
                c.province_id,
                l.geom,
                round(ST_Area(l.geom) / 1e6, 2) AS superficie_km2
            FROM commune AS c
            JOIN limite_communale AS l ON l.mun_code = c.mun_code
            """
        )
        con.execute("DROP VIEW IF EXISTS raw_limites")

        rapport(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
