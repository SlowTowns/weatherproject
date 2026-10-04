# Plan por fases: Clima Monterrey (pixel art)

## Contexto
Se construirá una web del clima de Monterrey, N.L. con estética pixel art (Blasphemous / Celeste), temas por estación, backend Python y solo APIs gratuitas. El stack está aprobado. El entorno ya está listo: `.venv` con las dependencias de Python y Node/npm instalados. Si falta algo, se avisa antes de instalar. No se crean API keys; si una fuente las necesita, se le piden al usuario.

## Stack (aprobado)
- Datos: Open-Meteo (clima, pronóstico) + Open-Meteo Air Quality. Sin key.
- Backend: FastAPI + httpx + uvicorn + Pydantic, caché en memoria (TTL ~10 min), pytest.
- Frontend: Vite + React (JavaScript), CSS con `image-rendering: pixelated`, fuente pixel local.
- Alertas con reglas propias (NWS no cubre México).

## Calidad de datos / falsos positivos
- Validar respuestas con Pydantic (rangos plausibles: temp -10..55 °C, humedad 0..100, etc.).
- Descartar valores atípicos y usar el último dato válido en caché si falla la API.
- Alertas con umbrales y persistencia: calor extremo (sensación ≥ 40 °C sostenida ≥ 2 h), tormenta (código WMO 95-99 o prob. lluvia ≥ 70 % con ráfagas altas), frente frío (caída ≥ 8 °C en 12 h).

## Diseño visual
- Paleta pixel art limitada (16–24 colores), alto contraste, sombras duras.
- Temas por estación: verano (naranjas/rojos cálidos), otoño (ocres/vino), invierno (azules fríos), primavera (verdes/rosas).
- Alertas sombrías (dorado/rojo sangre, estilo Blasphemous); cielos por bandas (estilo Celeste).
- Fondo del Cerro de la Silla y sprites animados por condición.

## Fases
Cada fase termina con commit + push. Indicaré "Fase N en curso / completada".

### Fase 0 — Preparación
- Verificar `.venv` (activarlo, `pip list`) y `node -v`/`npm -v` (solo lectura).
- `git init`, `.gitignore` (`.venv`, `node_modules`, `__pycache__`, `.env`), `README.md`.
- Conectar el remoto de GitHub (verificar la autenticación; pedir URL si no hay repo).
- Estructura `backend/` y `frontend/`.

### Fase 1 — Backend: datos
- Cliente Open-Meteo (actual, horario, diario) y Air Quality con httpx, con timeouts y reintentos.
- Esquemas Pydantic con rangos plausibles; descarte de valores atípicos.
- Caché TTL y respaldo con el último dato válido si falla la API.

### Fase 2 — Backend: API y alertas
- Endpoints `/api/clima`, `/api/pronostico`, `/api/aire`, `/api/alertas`.
- Alertas con umbrales y persistencia de varias horas (calor extremo, tormenta, frente frío).
- Errores: detalle en logs del servidor, mensaje genérico al usuario final.
- Tests pytest (validación, alertas, falla de API simulada).

### Fase 3 — Frontend: base y sistema de temas
- Scaffold Vite + React, cliente de la API, estados de carga/error.
- Temas por estación (variables CSS), seleccionados por fecha.
- Paleta limitada, fuente pixel, estilos base responsivos (móvil primero).

### Fase 4 — Frontend: componentes y arte pixel
- Layout de escritorio tipo dashboard (como las páginas de clima habituales); en móvil, una columna.
- Tarjeta de clima actual (sin presión), tipografía fina en los indicadores.
- Línea del tiempo de 24 h estilo Google (temperatura y lluvia), con cursor, teclado y tabla accesible.
- Pronóstico de 7 días con barra de rango de temperatura.
- Mapa de la ciudad (Leaflet + OpenStreetMap, sin API key) con la temperatura sobre el mapa.
- Calidad del aire con escala ICA; alertas con estilo sombrío (dorado/rojo sangre).
- Fecha actual (hora de Monterrey) arriba a la derecha.
- Hero con el Cerro de la Silla en pixel art y sprites del clima (sol, luna, nubes, lluvia, tormenta, niebla).
- Mascota: oso pixel art con accesorio por estación (flor, lentes, hoja, bufanda) y consejos según el clima.
- Temas: en la versión final solo por fecha real; la vista previa de temas existe únicamente en desarrollo.

### Fase 5 — Integración, accesibilidad y cierre
- FastAPI sirve el frontend compilado en producción, con cabeceras de seguridad (CSP, nosniff, X-Frame-Options).
- Contraste WCAG ≥ 4.5:1 en los cuatro temas (ajustados botón seleccionado y subtítulo), `prefers-reduced-motion`, textos alternativos.
- `requirements.txt` / `requirements-dev.txt` con versiones fijas; auditoría con `pip-audit` y `npm audit`.
- README y `CLAUDE.md` con el stack definitivo; push final.

## Estado
Fases 0 a 5 completadas.

## Estructura
```
AI projects/
  CLAUDE.md
  PLAN.md
  backend/  (app/main.py, app/services/openmeteo.py, app/schemas.py, app/alerts.py, tests/)
  frontend/ (Vite + React: src/components, src/themes, src/assets)
  README.md  .gitignore
```

## Verificación
- `pytest` en backend; `uvicorn app.main:app` y consulta de endpoints.
- `npm run dev` y revisión visual de los 4 temas en móvil y escritorio.
- Simular caída de la API: mensaje genérico en el cliente, detalle en logs.
