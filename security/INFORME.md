# Informe de pruebas de seguridad — API weatherproject (local, 2026-10-05)

Alcance: `http://127.0.0.1:8000` (build de producción: FastAPI + `frontend/dist`). Upstream (Open-Meteo) simulado en la prueba de carga; no se envió tráfico de prueba a hosts externos.
Reproducir: `scripts/manual_tests.sh`, `scripts/cache_stampede.py`, `scripts/run_failing_upstream.py {upstream503|malformed|unexpected}` (puerto 8001) y `scripts/asvs_checklist.py`.
Herramientas: nuclei 3.11.1 (`-rl 20 -c 5`, sin dos/fuzz/intrusive), bandit 1.9.4, pip-audit, npm audit, curl y scripts propios (`scripts/`). Evidencia en `reports/`.

## Línea base
- pytest: 32 pasan. pip-audit: 0 vulnerabilidades. npm audit: 0 vulnerabilidades.
- bandit: 1 hallazgo Low (B101 `assert` en `openmeteo.py:186`; se elimina con `python -O`, usar `if ... raise`).
- nuclei: 10 hallazgos, todos `info` (docs/openapi/redoc expuestos; faltan COEP/COOP/CORP/HSTS/Permissions-Policy/X-Permitted-Cross-Domain-Policies; tech-detect uvicorn).

## Hallazgos
| # | Sev. | Hallazgo | Evidencia | Corrección sugerida |
|---|------|----------|-----------|---------------------|
| 1 | Media | Sin rate limiting ni single-flight en la caché: con caché vacío, 100 solicitudes concurrentes generan 300 llamadas upstream (3 por solicitud, por los reintentos). Amplificación/DoS y riesgo de bloqueo por Open-Meteo. | `reports/cache_stampede.txt` | `asyncio.Lock` por clave en `_cached`; límite de tasa (slowapi o proxy). |
| 2 | Baja | `/docs`, `/redoc` y `/openapi.json` públicos. Swagger carga de `cdn.jsdelivr.net` y la CSP (`default-src 'self'`) lo bloquea, así que `/docs` probablemente queda roto (no verificado en navegador). | nuclei, `manual_tests.txt` | `docs_url=None, redoc_url=None, openapi_url=None` en producción. |
| 3 | Baja | Faltan HSTS (al servir por HTTPS), Permissions-Policy, COOP/CORP y `Cache-Control` en `/api/*`. | nuclei; curl sin `cache-control` | Añadir a `SECURITY_HEADERS` (`main.py:33`); `Cache-Control` adecuado en `/api/*`. |
| 4 | Baja | CSP con `style-src 'unsafe-inline'`. | cabecera CSP | Hashes/nonces si React/Leaflet lo permiten. |
| 5 | Info | CORS `allow_headers=["*"]`: el preflight refleja cualquier cabecera. Orígenes ajenos y `null` no reciben `Access-Control-Allow-Origin`. | `manual_tests.txt` | Listar cabeceras explícitas. |
| 6 | Info | Host falso y cabecera de 70 KB aceptados (200). Sin `TrustedHostMiddleware`. | `manual_tests.txt` | `TrustedHostMiddleware`; límites en el proxy inverso. |
| 7 | Info | El README arranca prod con `--host 0.0.0.0` y sin TLS. | README.md:39 | Escuchar en 127.0.0.1 tras un proxy con TLS, o documentar. |
| 8 | Info | Sin límite de tamaño de la respuesta upstream. | revisión de código | Tope de bytes al leer la respuesta. |
| 9 | Baja | Las respuestas 500 salen **sin ninguna cabecera de seguridad** (ni CSP, nosniff, XFO, Referrer-Policy). El handler de `Exception` corre en `ServerErrorMiddleware`, fuera del middleware `security_headers`. Las 503 sí las llevan. | `reports/live_errors_headers.txt` | Añadir las cabeceras dentro de `unexpected_error_handler` (`main.py:101`) o usar un middleware ASGI puro que envuelva toda la app; agregar un test. |
| 10 | Info | Falta documentación de seguridad: reglas de validación, límites de uso, plazos de remediación de dependencias, SBOM, inventario de logs y datos. | ASVS V2.1, V15.1, V16.1 | Sección "Seguridad" en README o `SECURITY.md`; SBOM con `cyclonedx-py`/`npm sbom`. |
| 11 | Baja | En producción (`uvicorn app.main:app`) los logs de la app salen **sin fecha, nivel ni origen**: el logging de Python no está configurado y se usa el handler de último recurso. | prueba con `uvicorn.config.LOGGING_CONFIG` | `logging.config.dictConfig` al iniciar (formato con timestamp UTC, nivel, logger), idealmente JSON. |

## Controles que pasaron
- Métodos distintos de GET en `/api/clima`: 405 sin fuga. Traversal y archivos sensibles (`/.env`, `/.git/config`, `main.py`, `requirements.txt`, `%2e%2e`, `%00`): todos 404. Los parámetros de consulta se ignoran (sin reflejo).
- CORS restringido a `localhost:5173`. nosniff, XFO DENY y CSP presentes también en 404 y estáticos.
- Errores en vivo (`reports/live_errors.txt`, upstream simulado en `127.0.0.1:8001`): upstream 503 y JSON malformado → 503; excepción inesperada → 500. En los tres casos el cuerpo es solo el mensaje genérico y el detalle queda en el log del servidor.
- Sin SSRF: URLs salientes constantes. Sin secretos ni API keys. Sin listado de directorios. TRACE devuelve 405.
- Frontend: sin `dangerouslySetInnerHTML`/`innerHTML`/`eval`/`postMessage`/almacenamiento del navegador. El único HTML construido a mano (`L.divIcon`, `MapCard.jsx:13`) recibe un número formateado. Sin sourcemaps en `dist`.

## ASVS 5.0.0 (niveles 1 y 2)
Detalle por requisito en [`ASVS-checklist.md`](ASVS-checklist.md), generado desde el CSV oficial con `scripts/asvs_checklist.py`.

253 requisitos: 180 N/A (sin autenticación, sesiones, autorización, OAuth, WebRTC, archivos ni cripto propia), 73 aplicables:

| Cumple | Parcial | No cumple | Despliegue |
|---|---|---|---|
| 40 | 13 | 12 | 8 |

- **No cumple:** V2.1.3, V2.3.2, V2.4.1, V15.2.2 (H1); V3.4.1 (H3); V13.4.5 (H2); V15.1.1, V15.1.3 (H10); V16.1.1, V16.2.1, V16.2.2, V16.2.4 (H11).
- **Parcial:** V3.2.1, V3.4.3, V3.4.4, V3.4.6 (H9, H4); V15.2.3 (H2); el resto por documentación faltante (H10).
- **Despliegue:** TLS, HSTS, redirección HTTPS, restricción de salida y protección y envío de logs (V4.1.2, V12.1.x, V12.2.x, V13.2.5, V16.4.2-3). Revisar al publicar.

## No cubierto
- TLS real (requiere proxy). semgrep no instalado. Nivel 3 de ASVS. No se corrigió código de la app.
