"""Exécute sql/spatial.sql requête par requête et affiche un aperçu."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import duckdb

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from run_queries import apercu  # noqa: E402

ROOT = SCRIPTS.parent
DB_PATH = ROOT / "data" / "processed" / "peb_wallonie.duckdb"
SPATIAL = ROOT / "sql" / "spatial.sql"


def iter_spatial(sql: str) -> list[tuple[str, str]]:
    """Découpe le fichier sur les en-têtes `-- S01`, `-- S02`, …"""
    chunks = re.split(r"(?=^-- S\d{2} )", sql, flags=re.MULTILINE)
    queries: list[tuple[str, str]] = []
    for chunk in chunks:
        header = re.match(r"-- (S\d{2}) — (.+)", chunk)
        if not header:
            continue
        query_id, title = header.group(1), header.group(2).strip()
        match = re.search(r"\n(WITH|SELECT)\b", chunk)
        if not match:
            raise SystemExit(f"Pas de SELECT dans {query_id}.")
        body = chunk[match.start() + 1 :].strip()
        if body.endswith(";"):
            body = body[:-1]
        queries.append((f"{query_id} — {title}", body))
    return queries


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not DB_PATH.exists():
        raise SystemExit("Base absente. Lancer d'abord : python scripts/etl_odwb.py")

    queries = iter_spatial(SPATIAL.read_text(encoding="utf-8"))
    if len(queries) < 3:
        raise SystemExit(f"Attendu au moins 3 requêtes spatiales, trouvé {len(queries)}.")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        con.execute("LOAD spatial")
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        if "limite_communale" not in tables:
            raise SystemExit(
                "Table limite_communale absente. Lancer : python scripts/load_spatial.py"
            )
        for title, body in queries:
            print("=" * 72)
            print(title)
            print("=" * 72)
            apercu(con, body, max_rows=40)
            print()
    finally:
        con.close()


if __name__ == "__main__":
    main()
