"""Génère le diagramme ER et 3 graphiques matplotlib depuis le SQL."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from run_queries import DB_PATH, query_by_id  # noqa: E402

ROOT = SCRIPTS.parent
DIAGRAMS = ROOT / "diagrams"
PICTURES = ROOT / "pictures" / "readme"

# Palette sobre, lisible en clair comme en sombre une fois exportée.
COULEUR_EXISTANT = "#3D5A80"
COULEUR_NEUF = "#98C1D9"
COULEUR_ACCENT = "#EE6C4D"
COULEUR_TEXTE = "#293241"
COULEUR_DIM = "#E8EEF4"
COULEUR_FAIT = "#F4E6DC"
COULEUR_VUE = "#EEF3EA"

COMMUNES_VOLUME = {"Charleroi", "Liège", "Mons", "Namur"}
COMMUNES_TAUX = {"Hastière", "Honnelles", "Rendeux"}

SQL_TAUX_VOLUME = """
SELECT
    c.nom AS commune,
    c.province_id AS province,
    count(*) AS n_certificats,
    round(
        100.0 * count(*) FILTER (WHERE l.est_passoire) / count(*),
        1
    ) AS pct_passoire_fg,
    round(sum(e.surface_chauffee) FILTER (WHERE l.est_passoire))::BIGINT
        AS m2_passoires
FROM certificats_existant AS e
JOIN commune AS c ON c.mun_code = e.mun_code
LEFT JOIN label_peb AS l ON l.label_id = e.label_id
GROUP BY c.nom, c.province_id
"""


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "medium",
            "axes.edgecolor": COULEUR_TEXTE,
            "axes.labelcolor": COULEUR_TEXTE,
            "xtick.color": COULEUR_TEXTE,
            "ytick.color": COULEUR_TEXTE,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _sauver(fig: plt.Figure, chemin: Path) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(chemin, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return chemin


def _boite(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    titre: str,
    lignes: list[str],
    facecolor: str,
) -> None:
    """Rectangle arrondi : titre + quelques colonnes (PK/FK)."""
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor=facecolor,
            edgecolor=COULEUR_TEXTE,
            linewidth=1.1,
        )
    )
    ax.text(
        x + w / 2,
        y + h - 0.14,
        titre,
        ha="center",
        va="top",
        fontsize=8.5,
        fontweight="bold",
        color=COULEUR_TEXTE,
        fontfamily="monospace",
    )
    ax.text(
        x + 0.1,
        y + h - 0.38,
        "\n".join(lignes),
        ha="left",
        va="top",
        fontsize=7,
        color=COULEUR_TEXTE,
        fontfamily="monospace",
        linespacing=1.35,
    )


def _fleche(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=0.9,
            color=COULEUR_TEXTE,
            shrinkA=0,
            shrinkB=1,
        )
    )


def figure_er(chemin: Path | None = None) -> Path:
    """Schéma étoile : dimensions partagées, deux faits, vue pont Espec."""
    if chemin is None:
        chemin = DIAGRAMS / "modele_relationnel.png"

    fig, ax = plt.subplots(figsize=(11.2, 7.4))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    ax.set_title(
        "Star schema — Walloon PEB certificates (DuckDB)",
        color=COULEUR_TEXTE,
        pad=8,
    )

    _boite(
        ax, 4.1, 6.15, 3.0, 1.05,
        "province",
        ["PK  province_id", "    nis_prefixe"],
        COULEUR_DIM,
    )
    _boite(
        ax, 3.85, 4.55, 3.5, 1.2,
        "commune",
        ["PK  mun_code  (INS)", "FK  province_id", "    nom, arrondissement"],
        COULEUR_DIM,
    )
    _boite(
        ax, 0.25, 4.55, 3.15, 1.2,
        "label_peb",
        ["PK  label_id  (++A…G)", "    espec_min / max", "    est_passoire"],
        COULEUR_DIM,
    )
    _boite(
        ax, 7.8, 4.55, 3.15, 1.2,
        "type_logement",
        ["PK  type_logement_id", "    maison | appart. | collectif", "    codes ODWB EN / FR"],
        COULEUR_DIM,
    )
    _boite(
        ax, 0.35, 1.55, 4.9, 2.15,
        "certificats_existant",
        [
            "PK  certificat_id",
            "    id_batiment, date_certificat",
            "FK  mun_code, province_id",
            "FK  label_id, type_logement_id",
            "    espec, surface_chauffee",
            "    periode_construction, systeme_chauffage",
        ],
        COULEUR_FAIT,
    )
    _boite(
        ax, 5.95, 1.55, 4.9, 2.15,
        "certificats_neuf",
        [
            "PK  certificat_id",
            "    id_unite, date_certificat",
            "FK  mun_code, province_id",
            "FK  label_id, type_logement_id",
            "    espec, type_generateur",
            "    vecteur_energetique",
        ],
        COULEUR_FAIT,
    )
    _boite(
        ax, 2.6, 0.12, 6.0, 1.05,
        "v_certificats  (view)",
        ["UNION ALL  +  regime  (existant | neuf)", "Bridge = Espec (kWh/m²·year). Not Ew, not G-share."],
        COULEUR_VUE,
    )

    # Pas de flèches croisées : les FK label/type vers *les deux* faits
    # sont écrites dans les boîtes.
    _fleche(ax, 5.6, 6.15, 5.6, 5.75)  # province → commune
    _fleche(ax, 4.8, 4.55, 2.7, 3.70)  # commune → existant
    _fleche(ax, 6.4, 4.55, 8.5, 3.70)  # commune → neuf
    _fleche(ax, 1.8, 4.55, 1.8, 3.70)  # label → existant
    _fleche(ax, 9.4, 4.55, 9.4, 3.70)  # type → neuf
    _fleche(ax, 2.8, 1.55, 4.4, 1.17)  # existant → vue
    _fleche(ax, 8.4, 1.55, 6.8, 1.17)  # neuf → vue

    ax.text(
        0.25,
        7.15,
        "Grain = one certificate. Two facts: protocols differ; dimensions are shared.",
        fontsize=8,
        color=COULEUR_TEXTE,
        style="italic",
    )
    return _sauver(fig, chemin)


def figure_ecart_provinces(
    con: duckdb.DuckDBPyConnection, chemin: Path | None = None
) -> Path:
    """Q03 : médiane Espec existant vs neuf par province."""
    if chemin is None:
        chemin = PICTURES / "ecart-espec-provinces.png"
    _style()
    lignes = con.sql(query_by_id("Q03")).fetchall()
    # Q03 est déjà trié par gap décroissant : on inverse pour barh (haut = plus grand écart).
    lignes = list(reversed(lignes))
    provinces = [r[0] for r in lignes]
    med_ex = [r[3] for r in lignes]
    med_neuf = [r[4] for r in lignes]
    gaps = [r[5] for r in lignes]
    y = range(len(provinces))

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    h = 0.36
    ax.barh([i + h / 2 for i in y], med_ex, height=h, color=COULEUR_EXISTANT, label="Existing")
    ax.barh([i - h / 2 for i in y], med_neuf, height=h, color=COULEUR_NEUF, label="New")
    for i, gap in enumerate(gaps):
        xmax = max(med_ex[i], med_neuf[i])
        ax.text(xmax + 8, i, f"+{gap:.0f}", va="center", fontsize=8, color=COULEUR_ACCENT)
    ax.set_yticks(list(y), provinces)
    ax.set_xlabel("Median Espec (kWh/m²·year)")
    ax.set_title("New vs existing stock — Espec gap by province")
    ax.legend(frameon=False, loc="lower right")
    ax.set_xlim(0, 430)
    fig.text(
        0.01,
        -0.02,
        "Source: sql/queries.sql Q03 · DuckDB · bridge = Espec, not G-share. Numbers = gap (existing − new).",
        fontsize=7.5,
        color=COULEUR_TEXTE,
    )
    fig.tight_layout()
    return _sauver(fig, chemin)


def figure_taux_vs_volume(
    con: duckdb.DuckDBPyConnection, chemin: Path | None = None
) -> Path:
    """Toutes les communes : % F/G vs m² de passoires (Q02 vs Q10 en un nuage)."""
    if chemin is None:
        chemin = PICTURES / "taux-vs-volume-passoires.png"
    _style()
    lignes = con.sql(SQL_TAUX_VOLUME).fetchall()
    xs = [r[3] for r in lignes]
    ys = [r[4] / 1_000_000 for r in lignes]
    noms = [r[0] for r in lignes]

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.scatter(xs, ys, s=22, alpha=0.45, c=COULEUR_EXISTANT, linewidths=0)
    a_annoter = COMMUNES_VOLUME | COMMUNES_TAUX
    for nom, x, y in zip(noms, xs, ys, strict=True):
        if nom not in a_annoter:
            continue
        couleur = COULEUR_ACCENT if nom in COMMUNES_TAUX else COULEUR_EXISTANT
        ax.scatter([x], [y], s=55, c=couleur, zorder=3)
        offset = {
            "Charleroi": (8, 8),
            "Liège": (8, -12),
            "Mons": (8, 6),
            "Namur": (-52, 8),
            "Hastière": (8, 6),
            "Honnelles": (8, -12),
            "Rendeux": (8, 6),
        }[nom]
        ax.annotate(
            nom,
            (x, y),
            textcoords="offset points",
            xytext=offset,
            fontsize=8,
            color=couleur,
            fontweight="medium",
        )
    ax.set_xlabel("Share of F/G certificates (%)")
    ax.set_ylabel("Heated floor of F/G (million m²)")
    ax.set_title("Energy sieves: worst rate ≠ largest volume")
    fig.text(
        0.01,
        -0.02,
        "Source: certificats_existant × label_peb · orange = worst rates (Q02) · dark = largest m² (Q10).",
        fontsize=7.5,
        color=COULEUR_TEXTE,
    )
    fig.tight_layout()
    return _sauver(fig, chemin)


def figure_chauffage(
    con: duckdb.DuckDBPyConnection, chemin: Path | None = None
) -> Path:
    """Q07 : médiane Espec selon le système de chauffage de l'existant."""
    if chemin is None:
        chemin = PICTURES / "chauffage-existant.png"
    _style()
    lignes = [r for r in reversed(con.sql(query_by_id("Q07")).fetchall()) if r[0] != "aucun"]
    noms = [r[0] for r in lignes]
    med = [r[2] for r in lignes]
    y = range(len(noms))

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    couleurs = [
        COULEUR_ACCENT if nom in {"poêle", "aucun", "foyer intégré", "électrique direct"} else COULEUR_EXISTANT
        for nom in noms
    ]
    ax.barh(list(y), med, color=couleurs, height=0.65)
    ax.set_yticks(list(y), noms)
    ax.set_xlabel("Median Espec (kWh/m²·year)")
    ax.set_title("Existing stock — heating system vs Espec")
    ax.axvline(88, color=COULEUR_NEUF, linewidth=1.4, linestyle="--")
    ax.text(90, len(noms) - 0.65, "new-build median (88)", fontsize=8, color=COULEUR_TEXTE)
    fig.text(
        0.01,
        -0.02,
        "Source: sql/queries.sql Q07 · orange = high-Espec · dashed = new-build median (Q01). "
        "'aucun' (n=1,155, median 843) omitted so the scale stays readable.",
        fontsize=7.5,
        color=COULEUR_TEXTE,
    )
    fig.tight_layout()
    return _sauver(fig, chemin)


def exporter_tout(con: duckdb.DuckDBPyConnection | None = None) -> list[Path]:
    """Écrit le diagramme ER et les 3 figures de synthèse."""
    fermer = False
    if con is None:
        if not DB_PATH.exists():
            raise SystemExit("Base absente. Lancer : python scripts/etl_odwb.py")
        con = duckdb.connect(str(DB_PATH), read_only=True)
        fermer = True
    try:
        chemins = [
            figure_er(),
            figure_ecart_provinces(con),
            figure_taux_vs_volume(con),
            figure_chauffage(con),
        ]
    finally:
        if fermer:
            con.close()
    return chemins


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for chemin in exporter_tout():
        print(chemin.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
