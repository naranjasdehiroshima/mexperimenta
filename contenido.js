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
      var a = c.avisos || {};
      document.querySelectorAll('[data-aviso]').forEach(function (el) {
        if (a[el.getAttribute('data-aviso')] === false) el.style.display = 'none';
      });
    })
    .catch(function () {});
})();
