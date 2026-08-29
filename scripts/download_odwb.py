"""Télécharge les extraits PEB ODWB (et les limites communales SPW) dans data/raw/."""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

DATASETS = {
    "peb-certification-residentielle-batiment-existant.parquet": (
        "https://www.odwb.be/api/explore/v2.1/catalog/datasets/"
        "peb-certification-residentielle-batiment-existant/exports/parquet"
    ),
    "peb-batiments-residentiels-neufs.parquet": (
        "https://www.odwb.be/api/explore/v2.1/catalog/datasets/"
        "peb-batiments-residentiels-neufs/exports/parquet"
    ),
}

# Limites officielles (SPF Finances / SPW), situation wallonne au 1er janvier.
# ADMUKEY = code INS à 5 chiffres (= mun_code). Lambert 2008 (EPSG:3812, mètres).
# Catalogue : https://geoportail.wallonie.be/catalogue/56d7efe4-b25b-4d82-adca-c2c193b1b4fa.html
LIMITES_URL = (
    "https://geoservices.wallonie.be/arcgis/rest/services/"
    "LIMITES/LIMITES_ADMINISTRATIVES/MapServer/3/query"
)
LIMITES_FICHIER = "limites-communes-wallonie.geojson"
LIMITES_PAGE = 200


def _opener() -> urllib.request.OpenerDirector:
    ctx = ssl.create_default_context(cafile=certifi.where())
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


def download_limites(dest: Path) -> int:
    """Télécharge les 261 polygones communaux (GeoJSON paginé, Lambert 2008)."""
    features: list[dict] = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": "1=1",
                "outFields": "ADMUKEY,NAMEFRE,ADPRKEY,ADDIKEY",
                "returnGeometry": "true",
                "outSR": "3812",
                "f": "geojson",
                "resultRecordCount": LIMITES_PAGE,
                "resultOffset": offset,
            }
        )
        with urllib.request.urlopen(f"{LIMITES_URL}?{query}") as reponse:
            payload = json.loads(reponse.read().decode("utf-8"))
        batch = payload.get("features") or []
        features.extend(batch)
        # Le service signale encore des pages via exceededTransferLimit.
        encore = bool(payload.get("exceededTransferLimit")) and len(batch) > 0
        if not encore:
            break
        offset += len(batch)

    collection = {"type": "FeatureCollection", "features": features}
    dest.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")
    return len(features)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    urllib.request.install_opener(_opener())
    for filename, url in DATASETS.items():
        dest = RAW / filename
        print(f"Téléchargement {filename} …")
        urllib.request.urlretrieve(url, dest)
        size_mo = dest.stat().st_size / 1_000_000
        print(f"  OK — {size_mo:.1f} Mo")

    dest_limites = RAW / LIMITES_FICHIER
    print(f"Téléchargement {LIMITES_FICHIER} …")
    n_poly = download_limites(dest_limites)
    size_mo = dest_limites.stat().st_size / 1_000_000
    print(f"  OK — {n_poly} polygones, {size_mo:.1f} Mo")
    if n_poly < 250:
        raise SystemExit(f"Échec : {n_poly} communes téléchargées, attendu ~261.")


if __name__ == "__main__":
    main()
