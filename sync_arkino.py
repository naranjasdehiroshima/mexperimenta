#!/usr/bin/env python3
"""
sync_arkino.py — Sincroniza el sitio de Mexperimenta/Arkino con los datos
reales de Airtable y los videos publicados en Internet Archive.

Uso:
    export AIRTABLE_TOKEN="pat..."
    python3 sync_arkino.py

Qué hace, en orden:
  1. Lee las 3 tablas de la base "ARKINO Revisión" (Vocabulario Controlado,
     Trailers, Gral. Treegan) vía la API de Airtable.
  2. Corrige el problema de BOM en nombres de campo (visto en Gral. Treegan).
  3. Filtra: solo pasan al sitio los registros con `publicado = true`.
  4. Cruza cada `dc:identifier` contra el catálogo real de
     @arkino_archivo_abierto en Internet Archive, para saber qué piezas
     tienen video disponible.
  5. Marca como `sensitive` cualquier pieza con el tag oficial "Erótico"
     en `dc:type` (más una red de seguridad manual documentada abajo).
  6. Regenera avances-cinematograficos.html, gral-treegan.html y
     pieza.html con los datos frescos.

Pensado para correr sin supervisión desde un GitHub Action (ver
.github/workflows/sync-airtable.yml en este mismo entrega).
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
import urllib.parse

BASE_ID = "app5g5osDdgSJeUKg"
TABLES = {
    "Vocabulario Controlado": "tbllHFNsIDREcSzdV",
    "Trailers": "tblSz21Ki0wmif4nV",
    "Gral. Treegan": "tblEn8x8PBhdJhlF2",
}
IA_UPLOADER = "arkino.archivoabierto@gmail.com"

# Piezas con evidencia clara de contenido explícito en su propia descripción
# pero sin el tag oficial "Erótico" -- hueco de catalogación real, ya
# reportado a Arkino. Quitar de aquí en cuanto lo corrijan en el origen.
MANUAL_SAFETY_NET = {"GT-010"}

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def airtable_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"ERROR HTTP {e.code} en {url}\n{body}", file=sys.stderr)
        raise


def fetch_table(table_id, token):
    """Trae todos los registros de una tabla, paginando si hace falta."""
    records = []
    offset = None
    while True:
        url = f"https://api.airtable.com/v0/{BASE_ID}/{table_id}?pageSize=100"
        if offset:
            url += f"&offset={offset}"
        data = airtable_get(url, token)
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records


def clean_fields(fields):
    """Quita el BOM (\\ufeff) que aparece pegado a algunos nombres de campo."""
    return {k.lstrip("\ufeff").strip(): v for k, v in fields.items()}


def field_text(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return v if v is not None else ""


def fetch_ia_identifiers():
    """Lista completa de identificadores ya subidos por Arkino a Internet Archive."""
    url = (
        "https://archive.org/advancedsearch.php?q=uploader:%22"
        + urllib.parse.quote(IA_UPLOADER)
        + "%22&fl[]=identifier&rows=500&output=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return [d["identifier"] for d in data.get("response", {}).get("docs", [])]


def find_archive_match(dc_identifier, ia_ids):
    if not dc_identifier:
        return None
    key = dc_identifier.strip().lower()
    if key in ia_ids:
        return key
    candidates = sorted([i for i in ia_ids if i.startswith(key)], key=len)
    return candidates[0] if candidates else None


def process_table(records, coll_name, ia_ids):
    out = []
    for r in records:
        f = clean_fields(r["fields"])
        if not f.get("publicado"):
            continue
        dc_id = f.get("dc:identifier", "")
        dctype = f.get("dc:type")
        types = dctype if isinstance(dctype, list) else ([dctype] if dctype else [])
        out.append({
            "id": r["id"],
            "idn": dc_id,
            "title": f.get("dc:title") or f.get("dc:title_es") or "(sin título)",
            "title_es": f.get("dc:title_es", ""),
            "year": str(f.get("dc:date", "")) or "",
            "creator": field_text(f.get("dc:creator")),
            "desc": f.get("dc:description", ""),
            "fmt": f.get("dc:format", ""),
            "medium": f.get("dc:medium", ""),
            "genre": field_text(f.get("dc:genre")),
            "type": types,
            "tags": [t.strip() for t in field_text(f.get("dc:subject")).split(",") if t.strip()],
            "lang": field_text(f.get("dc:language")),
            "coverage": field_text(f.get("dc:coverage")),
            "duration": f.get("extra:duracion", ""),
            "color": f.get("extra:color", ""),
            "coll": coll_name,
            "archiveId": find_archive_match(dc_id, ia_ids),
            "sensitive": ("Erótico" in types) or (dc_id in MANUAL_SAFETY_NET),
        })
    return out


def main():
    token = os.environ.get("AIRTABLE_TOKEN")
    if not token:
        print("Falta la variable de entorno AIRTABLE_TOKEN.", file=sys.stderr)
        sys.exit(1)

    print("Descargando tablas de Airtable...")
    trailers_raw = fetch_table(TABLES["Trailers"], token)
    gt_raw = fetch_table(TABLES["Gral. Treegan"], token)
    voc_raw = fetch_table(TABLES["Vocabulario Controlado"], token)
    print(f"  Trailers: {len(trailers_raw)} registros")
    print(f"  Gral. Treegan: {len(gt_raw)} registros")
    print(f"  Vocabulario Controlado: {len(voc_raw)} términos")

    print("Consultando catálogo de video en Internet Archive...")
    ia_ids = fetch_ia_identifiers()
    print(f"  {len(ia_ids)} piezas con video confirmado")

    trailers = process_table(trailers_raw, "Avances Cinematográficos", ia_ids)
    gt = process_table(gt_raw, "Gral. Treegan", ia_ids)

    with open(os.path.join(OUT_DIR, "trailers_final.json"), "w", encoding="utf-8") as f:
        json.dump(trailers, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, "gral_treegan_final.json"), "w", encoding="utf-8") as f:
        json.dump(gt, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, "all_pieces.json"), "w", encoding="utf-8") as f:
        json.dump(trailers + gt, f, ensure_ascii=False)

    n_video = sum(1 for x in trailers + gt if x["archiveId"])
    n_sensitive = sum(1 for x in trailers + gt if x["sensitive"])
    print(f"Listo: {len(trailers)+len(gt)} piezas publicadas, {n_video} con video, {n_sensitive} reservadas.")
    print("Ahora corre build_real_collections.py para regenerar el HTML del sitio.")


if __name__ == "__main__":
    main()
