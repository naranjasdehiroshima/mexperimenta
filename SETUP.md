# Sincronización automática — Mexperimenta ↔ Airtable

Esto deja el sitio actualizándose solo cada vez que el equipo de Arkino
edite el Airtable. Son 4 pasos, una sola vez.

## 1. Sube estos archivos a la raíz de tu repositorio de GitHub

- `sync_arkino.py`
- `build_real_collections.py`
- `.github/workflows/sync-airtable.yml` (el archivo de flujo va **dentro**
  de una carpeta `.github/workflows/` — créala si no existe)
- Todas las páginas del sitio (`mexperimenta-home-v4.html`, `videoteca.html`,
  `avances-cinematograficos.html`, `gral-treegan.html`, `pieza.html`, y el
  resto), en la raíz del repositorio.
- El repositorio debe tener **GitHub Pages activado** apuntando a esa misma
  rama, para que el sitio quede visible en una URL pública.

## 2. Genera un token de Airtable (si no tienes uno ya)

Ver instrucciones completas en el dossier — resumen rápido:
[airtable.com/create/tokens](https://airtable.com/create/tokens) → scopes
`data.records:read` + `schema.bases:read` → acceso solo a la base
"ARKINO Revisión".

## 3. Guarda el token como *secret* del repositorio

En GitHub: **Settings → Secrets and variables → Actions → New repository
secret**

- Nombre: `AIRTABLE_TOKEN`
- Valor: el token que generaste (empieza con `pat...`)

Esto es lo único que reemplaza el pegar el token en una conversación: vive
cifrado en GitHub, nunca en texto plano en ningún archivo del repo.

## 4. Prueba que funcione

En la pestaña **Actions** del repositorio, busca "Sincronizar Airtable y
publicar el sitio" → botón **Run workflow**. Revisa el log: si dice
"Sin cambios en Airtable desde la última sincronización" o hace un commit
nuevo, quedó funcionando.

A partir de ahí corre solo, todos los días a las 09:00 UTC (ajustable en el
archivo `.yml`, línea del `cron`).

## Qué NO cubre todavía esta automatización

- **ULTRAcinema y Archivos X** — sus páginas siguen con datos de muestra
  del sitio público viejo, porque esas colecciones no están en este
  Airtable (ver conversación aparte con el equipo). Cuando existan, hay
  que sumarlas a `sync_arkino.py` con su propio ID de tabla.
- **Contraseña de contenido reservado** — sigue siendo la de
  demostración (`arkino2026`). Cámbiala antes de que esto proteja
  contenido real (instrucciones en el propio código, función
  `UNLOCK_HASH`).
- **Videoteca** — su estante de piezas está elegido a mano, no se
  actualiza solo con este flujo. Si quieres que también se autoactualice,
  es un paso adicional que no está armado todavía.
