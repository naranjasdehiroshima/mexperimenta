/* Aplica contenido.json (editado desde admin.html) sobre la página.
   - [data-edit="clave"]  -> reemplaza el texto
   - [data-aviso="slug"]  -> se oculta si avisos[slug] === false
   Si no se puede leer el archivo, la página se queda con su texto original. */
(function () {
  fetch('contenido.json?v=' + Date.now(), { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (c) {
      if (!c) return;
      var t = c.textos || {};
      document.querySelectorAll('[data-edit]').forEach(function (el) {
        var v = t[el.getAttribute('data-edit')];
        if (typeof v === 'string' && v.trim()) el.textContent = v;
      });
      var e = c.enlaces || {};
      document.querySelectorAll('[data-enlace]').forEach(function (el) {
        var u = (e[el.getAttribute('data-enlace')] || '').trim();
        if (!/^https?:\/\//i.test(u)) return;
        var a = document.createElement('a');
        a.href = u; a.target = '_blank'; a.rel = 'noopener';
        a.style.color = 'inherit'; a.style.textDecoration = 'underline'; a.style.textUnderlineOffset = '3px';
        a.textContent = el.textContent; el.textContent = ''; el.appendChild(a);
      });
      var a = c.avisos || {};
      document.querySelectorAll('[data-aviso]').forEach(function (el) {
        if (a[el.getAttribute('data-aviso')] === false) el.style.display = 'none';
      });
    })
    .catch(function () {});
})();
