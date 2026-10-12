#!/usr/bin/env python3
"""Genera capturas.json (manifiesto de fotogramas por pieza) y miniaturas ligeras.

Lee las carpetas  capturas/TR_###_*  (capturas de VLC: vlcsnap-AAAA-MM-DD-HHhMMmSSsMMM.png),
las ordena cronológicamente y crea:
  - capturas_min/TR-###/NN.jpg   miniaturas de 520 px (solo si no existen)
  - capturas.json                {"TR-001": {"full": [...], "min": [...]}, ...}
Las miniaturas necesitan Pillow (pip install pillow); si no está, se omiten y la web usa el original.
Uso:  python3 build_capturas.py   (desde la raíz del repo)
"""
import json, os, re, sys
SRC = 'capturas'; DST = 'capturas_min'
try:
    from PIL import Image
except ImportError:
    Image = None
    print('Aviso: Pillow no instalado, sin miniaturas', file=sys.stderr)

def main():
    manifest = {}
    if not os.path.isdir(SRC):
        print('No existe', SRC); return
    for folder in sorted(os.listdir(SRC)):
        m = re.match(r'^TR_(\d{3})', folder)
        path = os.path.join(SRC, folder)
        if not m or not os.path.isdir(path):
            continue
        pid = 'TR-' + m.group(1)
        files = sorted(f for f in os.listdir(path)
                       if f.lower().startswith('vlcsnap') and f.lower().endswith(('.png', '.jpg', '.jpeg')))
        if not files:
            continue
        full, mins = [], []
        os.makedirs(os.path.join(DST, pid), exist_ok=True) if Image else None
        for i, f in enumerate(files, 1):
            src = os.path.join(path, f)
            full.append(src.replace(os.sep, '/'))
            if Image:
                out = os.path.join(DST, pid, '%02d.jpg' % i)
                if not os.path.exists(out):
                    try:
                        im = Image.open(src).convert('RGB')
                        im.thumbnail((520, 520))
                        im.save(out, 'JPEG', quality=72, optimize=True)
                    except Exception as e:
                        print('Error', src, e, file=sys.stderr); continue
                mins.append(out.replace(os.sep, '/'))
        manifest[pid] = {'full': full, 'min': mins}
    with open('capturas.json', 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    print('capturas.json:', len(manifest), 'piezas,', sum(len(v['full']) for v in manifest.values()), 'fotogramas')

main()
