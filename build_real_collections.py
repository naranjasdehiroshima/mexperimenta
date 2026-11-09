import json, re

# La marca de "contenido reservado" ahora viene calculada en los datos mismos
# (campo `sensitive`, derivado del tag oficial "Erótico" de Arkino + una red de
# seguridad manual documentada). Ya no se decide aquí.
UNLOCK_HASH = "0fca5a7c222d663d44f7b84c54983db7fc1d323e03c05c5095df48ea1430bc3a"

def build_page(cfg):
    items = json.load(open(cfg['data_file'], encoding='utf-8'))
    items.sort(key=lambda x: x['idn'] or '')

    n_total = len(items)
    n_video = sum(1 for x in items if x['archiveId'])
    years = []
    for x in items:
        m = re.findall(r'(1[6-9]\d\d|20[0-2]\d)', x['year'] or '')
        years += [int(y) for y in m]
    year_range = f"{min(years)}–{max(years)}" if years else "s/f"

    from collections import Counter
    genre_counts = Counter(x['genre'] for x in items if x['genre'])
    top_genres = [g for g, _ in genre_counts.most_common(5)]

    items_json = json.dumps(items, ensure_ascii=False)
    chips_html = '\n      '.join(
        f'<div class="chip" data-genre="{g}">{g}</div>' for g in top_genres
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Mexperimenta — {cfg['name']}</title>
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: #221e17;
    color: #efebdc;
    font-family: 'Georgia', 'Times New Roman', serif;
  }}
  .mono {{ font-family: 'Courier New', monospace; }}
  #topbar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 32px; border-bottom: 1px solid #453e30;
  }}
  #topbar .word {{
    font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 3px;
    font-size: 13px; color: #efebdc; text-decoration: none;
  }}
  #topbar nav a {{
    font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 1.5px;
    color: #b8b19c; text-decoration: none; margin-left: 26px; text-transform: uppercase;
  }}
  #topbar nav a:hover, #topbar nav a.active {{ color: #9dffb0; }}
  #crumb {{
    padding: 16px 32px 0; max-width: 1080px; margin: 0 auto;
    font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 1px; color: #a39c88;
  }}
  #crumb a {{ color: #a39c88; text-decoration: none; }}
  #crumb a:hover {{ color: #9dffb0; }}
  #crumb span {{ color: #efebdc; }}
  #coll-hero {{ max-width: 1080px; margin: 18px auto 0; padding: 0 32px; }}
  #coll-hero-inner {{
    border-radius: 10px; border: 1px solid #4d4536; background: #2e2820;
    padding: 40px 42px 34px;
  }}
  #coll-hero-inner .eyebrow {{
    font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 2.5px;
    color: #9dffb0; text-transform: uppercase; margin-bottom: 12px;
  }}
  #coll-hero-inner h1 {{
    font-family: 'Courier New', monospace; font-size: clamp(30px,5vw,44px);
    color: #f7f2e4; margin: 0 0 14px; letter-spacing: 1px;
  }}
  #coll-hero-inner p {{ font-size: 14.5px; line-height: 1.7; color: #c9c4b2; margin: 0 0 22px; max-width: 680px; }}
  #coll-stats {{ display: flex; gap: 30px; flex-wrap: wrap; }}
  #coll-stats .s .n {{ font-family: 'Courier New', monospace; font-size: 17px; font-weight: bold; color: #eee7d4; }}
  #coll-stats .s .l {{ font-family: 'Courier New', monospace; font-size: 9.5px; color: #a39c88; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px; }}
  #toolbar {{
    max-width: 1080px; margin: 28px auto 0; padding: 0 32px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
  }}
  #toolbar .count {{ font-family: 'Courier New', monospace; font-size: 11px; color: #a39c88; letter-spacing: 1px; }}
  #filter-chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .chip {{
    font-family: 'Courier New', monospace; font-size: 10.5px; color: #b8b1a0;
    border: 1px solid #4d4536; padding: 5px 11px; border-radius: 20px; cursor: pointer;
    background: #2e2820; text-transform: uppercase;
  }}
  .chip:hover {{ border-color: #a39c88; color: #efebdc; }}
  .chip.active {{ background: #9dffb0; color: #14120d; border-color: #9dffb0; }}
  #grid-wrap {{ max-width: 1080px; margin: 22px auto 60px; padding: 0 32px; }}
  #piece-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px,1fr)); gap: 18px; }}
  .piece-card {{
    background: #2e2820; border: 1px solid #453e30; border-radius: 4px; overflow: hidden;
    cursor: pointer; transition: transform .15s, border-color .15s;
    opacity: 0; transform: translateY(8px);
  }}
  .piece-card.show {{ opacity: 1; transform: translateY(0); transition: opacity .35s ease, transform .35s ease, border-color .15s; }}
  .piece-card:hover {{ transform: translateY(-3px); border-color: #a39c88; }}
  .piece-card .thumb {{ position: relative; aspect-ratio: 4/3; overflow: hidden; background: #17140f; }}
  .piece-card .thumb img {{ width: 100%; height: 100%; object-fit: cover; filter: grayscale(.25) brightness(.85) contrast(1.05); }}
  .piece-card .thumb.noimg {{ display: flex; align-items: center; justify-content: center; }}
  .piece-card .thumb.noimg .ph {{
    font-family: 'Courier New', monospace; font-size: 9.5px; color: #4d4536; text-align: center; letter-spacing: .5px; padding: 10px;
  }}
  .piece-card .thumb.noimg.locked {{ background: #241a14; }}
  .piece-card .thumb.noimg.locked .ph {{ color: #7a5a3a; line-height: 1.8; }}
  .piece-card .thumb .idn {{
    position: absolute; top: 6px; left: 6px; font-family: 'Courier New', monospace; font-size: 9px;
    color: #9dffb0; background: rgba(20,18,13,.8); padding: 2px 6px; border-radius: 2px;
  }}
  .piece-card .thumb .vidmark {{
    position: absolute; bottom: 6px; right: 6px; font-family: 'Courier New', monospace; font-size: 8.5px;
    color: #14120d; background: #9dffb0; padding: 2px 6px; border-radius: 2px; letter-spacing: .5px;
  }}
  .piece-card .meta {{ padding: 10px 12px 12px; }}
  .piece-card .meta .t {{
    font-family: 'Courier New', monospace; font-size: 12px; color: #f7f2e4; line-height: 1.35;
    margin: 0 0 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 32px;
  }}
  .piece-card .meta .y {{ font-family: 'Courier New', monospace; font-size: 10px; color: #a39c88; }}

  #modal-backdrop {{
    position: fixed; inset: 0; background: rgba(10,9,7,.86); backdrop-filter: blur(2px);
    display: none; align-items: center; justify-content: center; z-index: 100; padding: 24px;
  }}
  #modal-backdrop.open {{ display: flex; }}
  #modal-card {{
    background: #2e2820; border: 1px solid #4d4536; border-radius: 10px; max-width: 960px; width: 100%;
    max-height: 88vh; overflow-y: auto; display: flex; flex-wrap: wrap; position: relative;
  }}
  #modal-close {{
    position: absolute; top: 18px; right: 24px; font-family: 'Courier New', monospace; font-size: 20px;
    color: #d4cfbc; background: none; border: none; cursor: pointer; z-index: 5; opacity: .75;
  }}
  #modal-close:hover {{ opacity: 1; }}
  #modal-media {{ flex: 0 0 400px; padding: 28px; display: flex; align-items: center; justify-content: center; background: #221e17; }}
  #modal-video-wrap {{ width: 100%; aspect-ratio: 4/3; background: #060706; border-radius: 6px; overflow: hidden; position: relative; }}
  #modal-video-wrap iframe {{ width: 100%; height: 100%; border: 0; }}
  #modal-digitizing {{
    width: 100%; height: 100%; display: none; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
    position: absolute; inset: 0; background: rgba(6,7,6,.7);
  }}
  #modal-digitizing.on {{ display: flex; }}
  #modal-digitizing img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .4; filter: grayscale(.4) brightness(.6); z-index: -1; }}
  #modal-reel {{ width: 40px; height: 40px; animation: reelspin 2.6s linear infinite; }}
  @keyframes reelspin {{ to {{ transform: rotate(360deg); }} }}
  #modal-digitizing .dtext {{ font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 1.5px; color: #9dffb0; text-transform: uppercase; }}
  #modal-digitizing .dsub {{ font-family: 'Courier New', monospace; font-size: 9.5px; color: #a39c88; text-align: center; max-width: 80%; line-height: 1.5; }}
  #modal-body {{ flex: 1; min-width: 320px; padding: 46px 34px 30px; }}
  #modal-body .eyebrow {{ font-family: 'Courier New', monospace; font-size: 10.5px; letter-spacing: 2px; color: #9dffb0; text-transform: uppercase; margin-bottom: 10px; }}
  #modal-body h2 {{ font-family: 'Courier New', monospace; font-size: 21px; color: #f7f2e4; margin: 0 0 6px; }}
  #modal-body .title-es {{ font-size: 13px; color: #a39c88; font-style: italic; margin: 0 0 14px; }}
  #modal-meta-row {{ display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #4d4536; }}
  #modal-meta-row .m .n {{ font-family: 'Courier New', monospace; font-size: 12.5px; color: #efebdc; }}
  #modal-meta-row .m .l {{ font-family: 'Courier New', monospace; font-size: 8.5px; color: #a39c88; letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }}
  #modal-desc {{ font-size: 13.5px; line-height: 1.7; color: #c9c4b2; white-space: pre-line; margin: 0 0 18px; max-height: 220px; overflow-y: auto; }}
  #modal-tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  #modal-tags .tg {{ font-family: 'Courier New', monospace; font-size: 10px; color: #a39c88; border: 1px solid #4d4536; padding: 4px 10px; border-radius: 20px; }}

  footer {{ border-top: 1px solid #453e30; padding: 28px 32px 40px; text-align: center; }}
  footer .orgs {{ font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 1.5px; color: #b8b19c; text-transform: uppercase; }}
  footer .orgs span {{ color: #6b6350; margin: 0 8px; }}
  footer .src {{ font-family: 'Courier New', monospace; font-size: 9.5px; color: #736c5b; margin-top: 10px; }}

  /* ---- contenido reservado (mosaico + contraseña) ---- */
  .piece-card .thumb canvas.pixelated {{
    width: 100%; height: 100%; display: block;
    image-rendering: pixelated; image-rendering: crisp-edges;
  }}
  .piece-card .thumb .lockmark {{
    position: absolute; bottom: 6px; right: 6px; font-family: 'Courier New', monospace; font-size: 8.5px;
    color: #f2c98a; background: rgba(20,18,13,.85); padding: 2px 7px; border-radius: 2px; letter-spacing: .5px;
    display: flex; align-items: center; gap: 4px;
  }}
  #modal-gate {{
    position: absolute; inset: 0; display: none; flex-direction: column; align-items: center; justify-content: center;
    gap: 14px; background: rgba(10,9,7,.55); z-index: 3; padding: 20px; text-align: center;
  }}
  #modal-gate.on {{ display: flex; }}
  #modal-gate .lock-icon {{ font-size: 26px; }}
  #modal-gate .gate-title {{
    font-family: 'Courier New', monospace; font-size: 11.5px; letter-spacing: 1.5px; color: #f2c98a; text-transform: uppercase;
  }}
  #modal-gate .gate-sub {{
    font-family: 'Courier New', monospace; font-size: 9.5px; color: #b8b1a0; max-width: 260px; line-height: 1.6;
  }}
  #modal-gate input {{
    font-family: 'Courier New', monospace; font-size: 12px; background: #17140f; border: 1px solid #4d4536;
    color: #efebdc; padding: 8px 12px; border-radius: 4px; text-align: center; width: 160px;
  }}
  #modal-gate button {{
    font-family: 'Courier New', monospace; font-size: 10.5px; letter-spacing: 1px; text-transform: uppercase;
    background: #9dffb0; color: #14120d; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;
  }}
  #modal-gate .gate-error {{ font-family: 'Courier New', monospace; font-size: 9.5px; color: #e08a6a; height: 12px; }}
</style>
</head>
<body>

  <div id="topbar">
    <a class="word" href="mexperimenta-home-v4.html">MEXPERIMENTA</a>
    <nav>
      <a href="mexperimenta-home-v4.html#collections" class="active">Colecciones</a>
      <a href="videoteca.html">Videoteca</a>
      <a href="mexperimenta-home-v4.html#about">Acerca de</a>
    </nav>
  </div>

  <div id="crumb">
    <a href="mexperimenta-home-v4.html">Inicio</a> / <a href="mexperimenta-home-v4.html#collections">Colecciones</a> / <span>{cfg['name']}</span>
  </div>

  <div id="coll-hero">
    <div id="coll-hero-inner">
      <div class="eyebrow">Colección · datos en vivo desde Airtable</div>
      <h1>{cfg['name']}</h1>
      <p>{cfg['desc']}</p>
      <div id="coll-stats">
        <div class="s"><div class="n">{n_total}</div><div class="l">piezas publicadas</div></div>
        <div class="s"><div class="n">{year_range}</div><div class="l">rango</div></div>
        <div class="s"><div class="n">{n_video}</div><div class="l">con video disponible</div></div>
        <div class="s"><div class="n">{cfg['formato']}</div><div class="l">formato original</div></div>
      </div>
    </div>
  </div>

  <div id="toolbar">
    <div class="count" id="result-count">{n_total} piezas</div>
    <div id="filter-chips">
      <div class="chip active" data-genre="">Todas</div>
      {chips_html}
    </div>
  </div>

  <div id="grid-wrap"><div id="piece-grid"></div></div>

  <div id="modal-backdrop">
    <div id="modal-card">
      <button id="modal-close" aria-label="Cerrar">✕</button>
      <div id="modal-media">
        <div id="modal-video-wrap">
          <img id="modal-poster" src="" alt="" style="width:100%;height:100%;object-fit:cover;">
          <canvas id="modal-pixelated" style="position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated;display:none;"></canvas>
          <iframe id="modal-iframe" src="" style="display:none;" allowfullscreen></iframe>
          <div id="modal-digitizing">
            <svg id="modal-reel" viewBox="0 0 60 60">
              <circle cx="30" cy="30" r="26" fill="none" stroke="#9dffb0" stroke-width="2" opacity="0.35"/>
              <circle cx="30" cy="30" r="26" fill="none" stroke="#9dffb0" stroke-width="2" stroke-dasharray="8 10" opacity="0.85"/>
              <circle cx="30" cy="30" r="6" fill="#9dffb0" opacity="0.85"/>
            </svg>
            <div class="dtext">en digitalización</div>
            <div class="dsub">esta pieza todavía vive solo en el acervo físico — vuelve pronto</div>
          </div>
          <div id="modal-gate">
            <div class="lock-icon">🔒</div>
            <div class="gate-title">Contenido reservado</div>
            <div class="gate-sub">Arkino restringe el acceso a esta pieza. Si tienes autorización, ingresa la contraseña.</div>
            <input type="password" id="gate-input" placeholder="contraseña" autocomplete="off">
            <button id="gate-submit">Desbloquear</button>
            <div class="gate-error" id="gate-error"></div>
          </div>
        </div>
      </div>
      <div id="modal-body">
        <div class="eyebrow" id="modal-eyebrow">{cfg['name']}</div>
        <h2 id="modal-title">—</h2>
        <div class="title-es" id="modal-title-es"></div>
        <div id="modal-meta-row">
          <div class="m"><div class="n" id="modal-year">—</div><div class="l">Año</div></div>
          <div class="m"><div class="n" id="modal-idn">—</div><div class="l">Código</div></div>
          <div class="m"><div class="n" id="modal-creator">—</div><div class="l">Realización</div></div>
          <div class="m"><div class="n" id="modal-fmt">—</div><div class="l">Formato</div></div>
          <div class="m"><div class="n" id="modal-duration">—</div><div class="l">Duración</div></div>
        </div>
        <p id="modal-desc"></p>
        <div id="modal-tags"></div>
        <a id="modal-full-link" href="#" style="display:inline-block;margin-top:18px;font-family:'Courier New',monospace;font-size:10.5px;letter-spacing:1px;text-transform:uppercase;color:#9dffb0;text-decoration:none;">Ver ficha completa ↗</a>
      </div>
    </div>
  </div>

  <footer>
    <div class="orgs">Festival ULTRAcinema <span>·</span> ARKINO, Archivo Abierto de Cine Experimental <span>·</span> SAPEURS MX</div>
    <div class="src">datos sincronizados desde Airtable · video desde Internet Archive (@arkino_archivo_abierto)</div>
  </footer>

<script>
const ITEMS = {items_json};

const grid = document.getElementById('piece-grid');
const countEl = document.getElementById('result-count');

function pixelateInto(canvas, imgSrc, blocks) {{
  const ctx = canvas.getContext('2d');
  const img = new Image();
  img.onload = () => {{
    const w = blocks, h = Math.round(blocks * 0.75);
    canvas.width = w; canvas.height = h;
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(img, 0, 0, w, h);
  }};
  img.onerror = () => {{
    canvas.width = blocks; canvas.height = Math.round(blocks * 0.75);
    ctx.fillStyle = '#2e2820';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }};
  img.src = imgSrc;
}}

function render(genre) {{
  grid.innerHTML = '';
  const filtered = genre ? ITEMS.filter(it => it.genre === genre) : ITEMS;
  countEl.textContent = filtered.length + (filtered.length === 1 ? ' pieza' : ' piezas');
  filtered.forEach((it, i) => {{
    const el = document.createElement('div');
    el.className = 'piece-card';
    const thumbSrc = it.archiveId ? `https://archive.org/services/img/${{it.archiveId}}` : null;

    if (it.sensitive && thumbSrc) {{
      el.innerHTML = `<div class="thumb"><canvas class="pixelated"></canvas><div class="idn">${{it.idn||''}}</div><div class="lockmark">🔒 RESERVADO</div></div>`;
    }} else if (it.sensitive) {{
      el.innerHTML = `<div class="thumb noimg locked"><div class="idn">${{it.idn||''}}</div><div class="ph">🔒<br>contenido reservado</div></div>`;
    }} else if (thumbSrc) {{
      el.innerHTML = `<div class="thumb"><img src="${{thumbSrc}}" loading="lazy" alt=""><div class="idn">${{it.idn||''}}</div><div class="vidmark">VIDEO</div></div>`;
    }} else {{
      el.innerHTML = `<div class="thumb noimg"><div class="idn">${{it.idn||''}}</div><div class="ph">sin material visual<br>todavía</div></div>`;
    }}
    el.innerHTML += `<div class="meta"><p class="t">${{it.sensitive ? '🔒 ' + it.title : it.title}}</p><p class="y">${{it.year || 's/f'}} · ${{it.fmt || '—'}}</p></div>`;
    el.addEventListener('click', () => openModal(it));
    grid.appendChild(el);
    setTimeout(() => el.classList.add('show'), 12 * i);

    if (it.sensitive && thumbSrc) {{
      const cv = el.querySelector('canvas.pixelated');
      pixelateInto(cv, thumbSrc, 14);
    }}
  }});
}}

document.querySelectorAll('.chip').forEach(chip => {{
  chip.addEventListener('click', () => {{
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    render(chip.dataset.genre);
  }});
}});

const modalBackdrop = document.getElementById('modal-backdrop');
const modalPoster = document.getElementById('modal-poster');
const modalPixelated = document.getElementById('modal-pixelated');
const modalIframe = document.getElementById('modal-iframe');
const modalDigitizing = document.getElementById('modal-digitizing');
const modalGate = document.getElementById('modal-gate');
const gateInput = document.getElementById('gate-input');
const gateSubmit = document.getElementById('gate-submit');
const gateError = document.getElementById('gate-error');
const modalEyebrow = document.getElementById('modal-eyebrow');
const modalTitle = document.getElementById('modal-title');
const modalTitleEs = document.getElementById('modal-title-es');
const modalYear = document.getElementById('modal-year');
const modalIdn = document.getElementById('modal-idn');
const modalCreator = document.getElementById('modal-creator');
const modalFmt = document.getElementById('modal-fmt');
const modalDuration = document.getElementById('modal-duration');
const modalDesc = document.getElementById('modal-desc');
const modalTags = document.getElementById('modal-tags');

const UNLOCK_HASH = "{UNLOCK_HASH}";
async function sha256Hex(text) {{
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}}
function isUnlockedThisSession() {{
  return sessionStorage.getItem('arkino_unlocked') === '1';
}}

let currentItem = null;

function showMediaFor(it) {{
  modalIframe.src = ''; modalIframe.style.display = 'none';
  modalPoster.style.display = 'none';
  modalPixelated.style.display = 'none';
  modalDigitizing.classList.remove('on');
  modalGate.classList.remove('on');

  if (it.archiveId) {{
    modalIframe.src = `https://archive.org/embed/${{it.archiveId}}`;
    modalIframe.style.display = 'block';
  }} else {{
    modalPoster.style.display = 'block';
    modalPoster.src = '';
    modalDigitizing.classList.add('on');
  }}
}}

function openModal(it) {{
  currentItem = it;
  modalBackdrop.classList.add('open');
  modalTitle.textContent = it.title || '(sin título)';
  modalTitleEs.textContent = (it.title_es && it.title_es !== it.title) ? it.title_es : '';
  modalYear.textContent = it.year || 's/f';
  modalIdn.textContent = it.idn || '—';
  modalCreator.textContent = it.creator || '—';
  modalFmt.textContent = (it.fmt || '—') + (it.medium ? ' · ' + it.medium : '');
  modalDuration.textContent = it.duration || '—';
  modalDesc.textContent = it.desc || 'Sin sinopsis disponible.';
  modalTags.innerHTML = (it.tags||[]).slice(0,12).map(t => `<span class="tg">${{t}}</span>`).join('');
  document.getElementById('modal-full-link').href = `pieza.html?id=${{it.idn}}`;
  gateInput.value = ''; gateError.textContent = '';

  if (it.sensitive && !isUnlockedThisSession()) {{
    modalIframe.src = ''; modalIframe.style.display = 'none';
    modalDigitizing.classList.remove('on');
    modalPoster.style.display = 'none';
    modalPixelated.style.display = 'block';
    const thumbSrc = it.archiveId ? `https://archive.org/services/img/${{it.archiveId}}` : null;
    if (thumbSrc) pixelateInto(modalPixelated, thumbSrc, 22);
    modalGate.classList.add('on');
  }} else {{
    showMediaFor(it);
  }}
}}

async function tryUnlock() {{
  const hash = await sha256Hex(gateInput.value);
  if (hash === UNLOCK_HASH) {{
    sessionStorage.setItem('arkino_unlocked', '1');
    gateError.textContent = '';
    modalGate.classList.remove('on');
    if (currentItem) showMediaFor(currentItem);
    render(document.querySelector('.chip.active').dataset.genre);
  }} else {{
    gateError.textContent = 'contraseña incorrecta';
    gateInput.value = '';
  }}
}}
gateSubmit.addEventListener('click', tryUnlock);
gateInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') tryUnlock(); }});

function closeModal() {{
  modalBackdrop.classList.remove('open');
  modalIframe.src = '';
}}
document.getElementById('modal-close').addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', e => {{ if (e.target === modalBackdrop) closeModal(); }});
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

render('');
</script>
</body>
</html>
"""
    with open(cfg['out'], 'w', encoding='utf-8') as f:
        f.write(html)
    print(cfg['out'], '->', n_total, 'piezas,', n_video, 'con video')


build_page({
    'name': 'Avances Cinematográficos',
    'data_file': 'trailers_final.json',
    'out': 'avances-cinematograficos.html',
    'desc': 'Trailers de cine de explotación y género en 35mm, reapropiados como materia prima — found footage comercial reunido como archivo de referencia visual. Datos y video sincronizados en vivo desde el Airtable y el Internet Archive oficiales de Arkino.',
    'formato': '35mm',
})

build_page({
    'name': 'Gral. Treegan',
    'data_file': 'gral_treegan_final.json',
    'out': 'gral-treegan.html',
    'desc': 'Cine casero y registros familiares o cotidianos, incorporados al archivo como material de valor tanto afectivo como histórico. Datos y video sincronizados en vivo desde el Airtable y el Internet Archive oficiales de Arkino.',
    'formato': '16mm',
})


def rebuild_pieza_page(pieza_path, all_pieces_file):
    """Reinyecta el dataset combinado (todas las piezas) en pieza.html,
    conservando el resto de la plantilla intacta."""
    items = json.load(open(all_pieces_file, encoding='utf-8'))
    with open(pieza_path, encoding='utf-8') as f:
        content = f.read()
    new_json = json.dumps(items, ensure_ascii=False)
    content = re.sub(
        r'const ITEMS = \[.*?\];',
        lambda m: 'const ITEMS = ' + new_json + ';',
        content, flags=re.DOTALL, count=1,
    )
    with open(pieza_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(pieza_path, '->', len(items), 'piezas')


rebuild_pieza_page('pieza.html', 'all_pieces.json')

