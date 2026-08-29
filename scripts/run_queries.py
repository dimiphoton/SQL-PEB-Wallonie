"""Exécute sql/queries.sql requête par requête et affiche un aperçu."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import duckdb

# Windows : la console est souvent cp1252, les titres SQL sont en UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "peb_wallonie.duckdb"
QUERIES = ROOT / "sql" / "queries.sql"


def iter_queries(sql: str) -> list[tuple[str, str]]:
    """Découpe le fichier sur les en-têtes `-- Q01`, `-- Q02`, …"""
    chunks = re.split(r"(?=^-- Q\d{2} )", sql, flags=re.MULTILINE)
    queries: list[tuple[str, str]] = []
    for chunk in chunks:
        header = re.match(r"-- (Q\d{2}) — (.+)", chunk)
        if not header:
            continue
        query_id, title = header.group(1), header.group(2).strip()
        # Corps = à partir du premier WITH / SELECT jusqu'au `;` final.
        match = re.search(r"\n(WITH|SELECT)\b", chunk)
        if not match:
            raise SystemExit(f"Pas de SELECT dans {query_id}.")
        body = chunk[match.start() + 1 :].strip()
        if body.endswith(";"):
            body = body[:-1]
        queries.append((f"{query_id} — {title}", body))
    return queries


def query_by_id(query_id: str) -> str:
    """Renvoie le corps SQL d'une requête (`Q03`, `Q07`, …)."""
    for title, body in iter_queries(QUERIES.read_text(encoding="utf-8")):
        if title.startswith(query_id):
            return body
    raise KeyError(f"Requête {query_id} introuvable dans {QUERIES}.")


def apercu(con: duckdb.DuckDBPyConnection, body: str, max_rows: int = 20) -> None:
    """Affiche colonnes + lignes sans les cadres Unicode de Relation.show()."""
    relation = con.sql(body)
    colonnes = list(relation.columns)
    lignes = relation.fetchmany(max_rows)
    cellules = [
        ["" if valeur is None else str(valeur) for valeur in ligne]
        for ligne in lignes
    ]
    largeurs = [len(nom) for nom in colonnes]
    for ligne in cellules:
        for i, cellule in enumerate(ligne):
            largeurs[i] = max(largeurs[i], len(cellule))
    # Alignement simple : une largeur par colonne.
    fmt = "  ".join(f"{{:<{w}}}" for w in largeurs)
    print(fmt.format(*colonnes))
    print(fmt.format(*["-" * w for w in largeurs]))
    for ligne in cellules:
        print(fmt.format(*ligne))
    if len(lignes) == max_rows:
        print(f"… aperçu limité à {max_rows} lignes")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(
            "Base absente. Lancer d'abord : python scripts/etl_odwb.py"
        )

    queries = iter_queries(QUERIES.read_text(encoding="utf-8"))
    if len(queries) < 8:
        raise SystemExit(f"Attendu au moins 8 requêtes, trouvé {len(queries)}.")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
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
