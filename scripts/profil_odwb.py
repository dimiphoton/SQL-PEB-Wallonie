"""Profil brut des deux extraits PEB ODWB — reproductible, pas de nettoyage."""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXISTANT = RAW / "peb-certification-residentielle-batiment-existant.parquet"
NEUF = RAW / "peb-batiments-residentiels-neufs.parquet"


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show(con: duckdb.DuckDBPyConnection, sql: str) -> None:
    print(con.sql(sql))


def main() -> None:
    if not EXISTANT.exists() or not NEUF.exists():
        raise SystemExit(
            "Fichiers Parquet absents. Lancer d'abord : python scripts/download_odwb.py"
        )

    con = duckdb.connect()
    con.execute(
        f"CREATE VIEW existant AS SELECT * FROM read_parquet('{EXISTANT.as_posix()}')"
    )
    con.execute(f"CREATE VIEW neuf AS SELECT * FROM read_parquet('{NEUF.as_posix()}')")

    section("Volumes")
    show(
        con,
        """
        SELECT 'existant' AS jeu, count(*) AS n,
               count(DISTINCT id01_building) AS n_id
        FROM existant
        UNION ALL
        SELECT 'neuf', count(*), count(DISTINCT pebunit_id) FROM neuf
        """,
    )

    section("Labels existant")
    show(
        con,
        """
        SELECT e_spec_label AS label, count(*) AS n,
               min(e_spec) AS min_espec, max(e_spec) AS max_espec
        FROM existant
        GROUP BY 1
        ORDER BY 1
        """,
    )

    section("Labels neuf")
    show(
        con,
        """
        SELECT espec_label AS label, count(*) AS n,
               min(try_cast(espec AS DOUBLE)) AS min_espec,
               max(try_cast(espec AS DOUBLE)) AS max_espec
        FROM neuf
        GROUP BY 1
        ORDER BY 1
        """,
    )

    section("Aberrants Espec existant")
    show(
        con,
        """
        SELECT count(*) FILTER (WHERE e_spec < 0) AS n_neg,
               count(*) FILTER (WHERE e_spec > 1500) AS n_gt_1500
        FROM existant
        """,
    )


if __name__ == "__main__":
    main()
