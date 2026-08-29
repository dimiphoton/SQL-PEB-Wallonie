"""Construit data/processed/peb_wallonie.duckdb depuis les Parquet ODWB."""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SCHEMA = ROOT / "sql" / "schema.sql"
LOAD = ROOT / "sql" / "load.sql"
DB_PATH = PROCESSED / "peb_wallonie.duckdb"
EXISTANT = RAW / "peb-certification-residentielle-batiment-existant.parquet"
NEUF = RAW / "peb-batiments-residentiels-neufs.parquet"


def exec_sql_file(con: duckdb.DuckDBPyConnection, path: Path) -> None:
    """Exécute un fichier SQL pouvant contenir plusieurs instructions."""
    con.execute(path.read_text(encoding="utf-8"))


def compte(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    """Renvoie le scalaire d'un SELECT count(...) / agrégat à une cellule."""
    return int(con.execute(sql).fetchone()[0])


def rapport(con: duckdb.DuckDBPyConnection) -> None:
    n_com = compte(con, "SELECT count(*) FROM commune")
    n_ex = compte(con, "SELECT count(*) FROM certificats_existant")
    n_neuf = compte(con, "SELECT count(*) FROM certificats_neuf")
    n_espec_ex = compte(
        con, "SELECT count(*) FROM certificats_existant WHERE espec IS NULL"
    )
    n_espec_neuf = compte(
        con, "SELECT count(*) FROM certificats_neuf WHERE espec IS NULL"
    )
    n_id_ex = compte(
        con, "SELECT count(DISTINCT id_batiment) FROM certificats_existant"
    )
    n_id_neuf = compte(
        con, "SELECT count(DISTINCT id_unite) FROM certificats_neuf"
    )
    orphelins = compte(
        con,
        """
        SELECT count(*) FROM certificats_existant e
        WHERE e.mun_code IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM commune c WHERE c.mun_code = e.mun_code
          )
        """,
    ) + compte(
        con,
        """
        SELECT count(*) FROM certificats_neuf f
        WHERE f.mun_code IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM commune c WHERE c.mun_code = f.mun_code
          )
        """,
    )
    sans_mun = compte(
        con,
        "SELECT count(*) FROM certificats_existant WHERE mun_code IS NULL",
    )
    v_n = compte(con, "SELECT count(*) FROM v_certificats")

    print(f"Base          : {DB_PATH.relative_to(ROOT).as_posix()}")
    print(f"Communes      : {n_com}")
    print(f"Existant      : {n_ex:,} certificats ({n_id_ex:,} id_batiment)")
    print(f"Neuf          : {n_neuf:,} certificats ({n_id_neuf:,} id_unite)")
    print(f"Vue pont      : {v_n:,} lignes")
    print(f"Espec NULL    : existant {n_espec_ex:,} · neuf {n_espec_neuf:,}")
    print(f"Sans mun_code : {sans_mun:,} (existant)")
    print(f"FK orphelines : {orphelins}")

    if orphelins:
        raise SystemExit("Échec : des mun_code ne sont pas dans commune.")
    if n_ex == 0 or n_neuf == 0 or n_com == 0:
        raise SystemExit("Échec : table vide après chargement.")


def main() -> None:
    if not EXISTANT.exists() or not NEUF.exists():
        raise SystemExit(
            "Fichiers Parquet absents. Lancer d'abord : python scripts/download_odwb.py"
        )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    try:
        print("Schéma …")
        exec_sql_file(con, SCHEMA)

        # as_posix() : DuckDB attend des / même sous Windows.
        con.execute(
            f"CREATE VIEW raw_existant AS SELECT * FROM read_parquet('{EXISTANT.as_posix()}')"
        )
        con.execute(
            f"CREATE VIEW raw_neuf AS SELECT * FROM read_parquet('{NEUF.as_posix()}')"
        )

        print("Chargement …")
        exec_sql_file(con, LOAD)

        con.execute("DROP VIEW IF EXISTS raw_existant")
        con.execute("DROP VIEW IF EXISTS raw_neuf")
        con.execute("ANALYZE")

        rapport(con)
        taille_mo = DB_PATH.stat().st_size / 1_000_000
        print(f"Fichier       : {taille_mo:.1f} Mo")
    finally:
        con.close()


if __name__ == "__main__":
    main()
