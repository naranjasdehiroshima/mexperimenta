#!/usr/bin/env python3
"""Genera un still real (assets/stills/<archiveId>.jpg) para cada pieza con video en Internet Archive,
porque la miniatura automática de Archive.org suele ser solo su logo.
Reutiliza las funciones de build_destacados.py. Procesa un máximo de piezas por ejecución
(el workflow diario completa el resto poco a poco). No toca piezas marcadas como sensibles."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_destacados as bd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "stills")
MAX = int(os.environ.get("MAX_STILLS", "40"))
FILES = ["gral_treegan_final.json", "ultracinema_final.json", "archivos_x_final.json", "trailers_final.json"]
os.makedirs(OUT, exist_ok=True)


def still(aid):
    dest = os.path.join(OUT, aid + ".jpg")
    try:
        url, dur = bd.video_url(aid)
        if not url:
            return False
        best = None
        for k, fr in enumerate((0.2, 0.45, 0.7)):
            tmp = os.path.join(OUT, "_t%d.jpg" % k)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(dur * fr), "-i", url, "-frames:v", "1",
                            "-vf", "scale=800:-2", "-q:v", "5", tmp], capture_output=True, timeout=120)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 3000:
                c = bd.clean(Image.open(tmp).convert("RGB"))
                if c is not None:
                    sc = bd.score(c)
                    if best is None or sc > best[0]:
                        best = (sc, c)
            if os.path.exists(tmp):
                os.remove(tmp)
        if best:
            c = best[1]; c.thumbnail((640, 640)); c.save(dest, quality=74, optimize=True)
            return True
    except Exception as e:
        print("  sin still:", aid, str(e)[:70])
    return False


def main():
    ids = []
    for n in FILES:
        for p in bd.load(n):
            if p.get("archiveId") and not p.get("sensitive") and p["archiveId"] not in ids:
                ids.append(p["archiveId"])
    nuevos = 0
    for aid in ids:
        if nuevos >= MAX:
            break
        if not os.path.exists(os.path.join(OUT, aid + ".jpg")) and still(aid):
            nuevos += 1
            print("  still:", aid)
    print("stills: %d nuevos, %d en total" % (nuevos, len(os.listdir(OUT))))


if __name__ == "__main__":
    main()
