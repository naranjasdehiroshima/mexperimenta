/* Corrección de color para la ventana de video de las colecciones.
   Se añade sola: solo hace falta <script src="cc-modal.js"></script> en la página. */
(function () {
  const iframe = document.getElementById('modal-iframe');
  const wrap = document.getElementById('modal-screen-wrap');
  const backdrop = document.getElementById('modal-backdrop');
  if (!iframe || !wrap || !backdrop) return;

  const st = document.createElement('style');
  st.textContent = `
  #mcc-bar{display:none;padding:0 26px 6px;font-family:'Courier New',monospace}
  #modal-card.has-video #mcc-bar{display:block}
  #mcc-btn{font:10px 'Courier New',monospace;letter-spacing:1px;text-transform:uppercase;background:#17140f;border:1px solid #4d4536;color:#b8b1a0;padding:8px 14px;border-radius:4px;cursor:pointer}
  #mcc-btn.on{border-color:#9dffb0;color:#9dffb0}
  #mcc-panel{display:none;margin-top:10px;background:#17140f;border:1px solid #4d4536;border-radius:6px;padding:12px 16px;font-size:10px;letter-spacing:1px;color:#b8b1a0}
  #mcc-panel.on{display:block}
  #mcc-panel .row{display:flex;align-items:center;gap:10px;margin:6px 0;text-transform:uppercase}
  #mcc-panel .row label{width:84px;flex:none}
  #mcc-panel .row input{flex:1;accent-color:#9dffb0;min-width:0}
  #mcc-panel .row output{width:34px;text-align:right;color:#efebdc}
  #mcc-panel .pre{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px}
  #mcc-panel .pre button{font:10px 'Courier New',monospace;letter-spacing:1px;text-transform:uppercase;background:#2e2820;border:1px solid #4d4536;color:#b8b1a0;padding:6px 10px;border-radius:4px;cursor:pointer}
  #mcc-panel .pre button:hover{border-color:#9dffb0;color:#9dffb0}
  #mcc-panel .note{margin-top:8px;color:#8a8370;font-size:9px;line-height:1.5;text-transform:none}
  #mcc-tint{display:none;position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;z-index:3}
  #modal-card.mcc-on #mcc-tint{display:block}
  #modal-card.mcc-on #modal-iframe{filter:saturate(var(--cc-sat,1)) contrast(var(--cc-con,1)) brightness(var(--cc-gain,1))}`;
  document.head.appendChild(st);

  iframe.insertAdjacentHTML('afterend', '<div id="mcc-tint"></div>');
  const svg = document.createElement('div');
  svg.innerHTML = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="mcc-filter" color-interpolation-filters="sRGB"><feComponentTransfer><feFuncR id="mcc-fr" type="linear" slope="1"/><feFuncG id="mcc-fg" type="linear" slope="1"/><feFuncB id="mcc-fb" type="linear" slope="1"/></feComponentTransfer></filter></svg>';
  document.body.appendChild(svg.firstChild);

  const bar = document.createElement('div');
  bar.id = 'mcc-bar';
  bar.innerHTML = `<button id="mcc-btn" type="button">Corrección de color</button>
  <div id="mcc-panel">
    <div class="pre"><button data-p="off">Original</button><button data-p="rosa">Viraje rosa (70s)</button></div>
    <div class="row"><label>Rojo</label><input type="range" id="mcc-r" min="0.5" max="1.5" step="0.01" value="1"><output></output></div>
    <div class="row"><label>Verde</label><input type="range" id="mcc-g" min="0.5" max="1.5" step="0.01" value="1"><output></output></div>
    <div class="row"><label>Azul</label><input type="range" id="mcc-b" min="0.5" max="1.5" step="0.01" value="1"><output></output></div>
    <div class="row"><label>Saturación</label><input type="range" id="mcc-s" min="0.4" max="2" step="0.01" value="1"><output></output></div>
    <div class="row"><label>Contraste</label><input type="range" id="mcc-c" min="0.7" max="1.5" step="0.01" value="1"><output></output></div>
    <div class="note">Corrección visual en tu navegador: no modifica el archivo original.</div>
  </div>`;
  wrap.insertAdjacentElement('afterend', bar);

  const card = document.getElementById('modal-card');
  const ids = ['r', 'g', 'b', 's', 'c'];
  const presets = { off: { r: 1, g: 1, b: 1, s: 1, c: 1 }, rosa: { r: 0.80, g: 1.08, b: 1.16, s: 1.12, c: 1.05 } };
  const $ = id => document.getElementById('mcc-' + id);
  function apply(v) {
    const mx = Math.max(v.r, v.g, v.b, 1);
    card.style.setProperty('--cc-gain', mx);
    $('tint').style.background = 'rgb(' + [v.r, v.g, v.b].map(x => Math.round(255 * x / mx)).join(',') + ')';
    card.style.setProperty('--cc-sat', v.s); card.style.setProperty('--cc-con', v.c);
    ids.forEach(k => { $(k).value = v[k]; $(k).nextElementSibling.textContent = (+v[k]).toFixed(2); });
    const on = !(v.r == 1 && v.g == 1 && v.b == 1 && v.s == 1 && v.c == 1);
    card.classList.toggle('mcc-on', on);
    $('btn').classList.toggle('on', on);
  }
  const read = () => { const v = {}; ids.forEach(k => v[k] = +$(k).value); return v; };
  $('btn').addEventListener('click', () => $('panel').classList.toggle('on'));
  ids.forEach(k => $(k).addEventListener('input', () => apply(read())));
  bar.querySelectorAll('.pre button').forEach(b => b.addEventListener('click', () => apply(presets[b.dataset.p])));
  // al cerrar la ventana, volver al original
  new MutationObserver(() => { if (!backdrop.classList.contains('open')) { apply(presets.off); $('panel').classList.remove('on'); } })
    .observe(backdrop, { attributes: true, attributeFilter: ['class'] });
})();
