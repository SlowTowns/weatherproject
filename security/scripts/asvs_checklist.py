"""Genera security/ASVS-checklist.md a partir del CSV oficial de OWASP ASVS 5.0.0.

Alcance: requisitos de nivel 1 y 2. Cada requisito toma su evaluación de EVAL (por id),
o de SECTION_NA / CHAPTER_NA si toda la sección o capítulo no aplica. Lo que no tenga
evaluación sale como "Sin evaluar" y el script termina con código 1.
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "asvs" / "OWASP_Application_Security_Verification_Standard_5.0.0_en.csv"
OUT = ROOT / "ASVS-checklist.md"

OK, PARTIAL, FAIL, NA, DEPLOY = "Cumple", "Parcial", "No cumple", "N/A", "Despliegue"
STATES = [OK, PARTIAL, FAIL, DEPLOY, NA]

NO_AUTH = "La app no tiene usuarios, autenticación, sesiones, tokens ni cookies: API pública de solo lectura."
CHAPTER_NA = {
    "V6": NO_AUTH,
    "V7": NO_AUTH,
    "V8": "Sin autorización: todos los recursos son públicos por diseño (datos del clima abiertos).",
    "V9": NO_AUTH,
    "V10": "No usa OAuth ni OIDC.",
    "V17": "No usa WebRTC.",
}
SECTION_NA = {
    "V1.4": "Python y JavaScript gestionan la memoria; no hay código nativo propio.",
    "V3.3": "La app no emite cookies (verificado con curl en todas las respuestas).",
    "V4.3": "No usa GraphQL.",
    "V4.4": "No usa WebSocket.",
    "V5.1": "No hay subida ni descarga de archivos de usuario.",
    "V5.2": "No hay subida de archivos.",
    "V5.4": "No hay descarga de archivos con nombre controlado por el usuario.",
    "V11.1": "La app no gestiona claves ni cripto propia; TLS lo aporta httpx/ssl de la biblioteca estándar.",
    "V11.3": "No cifra datos.",
    "V11.4": "No usa hashes criptográficos ni contraseñas.",
    "V11.5": "No genera valores aleatorios con fines de seguridad.",
    "V11.6": "No usa criptografía de clave pública propia.",
    "V13.3": "No hay secretos: Open-Meteo y OSM no requieren API key (grep de claves sin resultados).",
}

M = "reports/manual_tests.txt"
L = "reports/live_errors.txt"

# id -> (estado, evidencia / justificación, hallazgo del INFORME o "")
EVAL = {
    # V1 Codificación y sanitización
    "V1.1.1": (NA, "No hay entrada de usuario que decodificar; la API no recibe parámetros ni cuerpo.", ""),
    "V1.1.2": (OK, "FastAPI/Pydantic serializan JSON al final; React escapa al renderizar.", ""),
    "V1.2.1": (OK, "JSON con Content-Type correcto; React escapa texto. El único HTML construido (`L.divIcon` en `MapCard.jsx:13`) recibe `Number(...).toLocaleString()`, que solo produce dígitos.", ""),
    "V1.2.2": (OK, "URLs salientes constantes (`config.py`) con params codificados por httpx; en el cliente, `URLSearchParams` (`themes.js:41`).", ""),
    "V1.2.3": (OK, "JSON generado por el serializador de FastAPI/Pydantic, nunca por concatenación.", ""),
    "V1.2.4": (NA, "No hay base de datos.", ""),
    "V1.2.5": (NA, "No hay llamadas al sistema operativo (bandit sin B602/B603/B605).", ""),
    "V1.2.6": (NA, "No usa LDAP.", ""),
    "V1.2.7": (NA, "No usa XPath.", ""),
    "V1.2.8": (NA, "No usa LaTeX.", ""),
    "V1.2.9": (NA, "No construye expresiones regulares con datos externos.", ""),
    "V1.3.1": (NA, "No acepta HTML de usuario.", ""),
    "V1.3.2": (OK, "Sin `eval`/`new Function` en `frontend/src` (grep) ni en backend (bandit).", ""),
    "V1.3.3": (OK, "Único contexto peligroso: HTML de `divIcon`, alimentado con un número formateado.", ""),
    "V1.3.4": (NA, "Los SVG son recursos propios del build; no hay SVG de usuario.", ""),
    "V1.3.5": (NA, "No procesa Markdown, plantillas ni CSS de usuario.", ""),
    "V1.3.6": (OK, "Sin SSRF: destinos y parámetros salientes son constantes (`config.py:6-7`); ninguna entrada llega a la URL.", ""),
    "V1.3.7": (NA, "No usa plantillas del servidor.", ""),
    "V1.3.8": (NA, "No usa JNDI.", ""),
    "V1.3.9": (NA, "Caché en memoria con claves constantes (`forecast`, `air_quality`); no usa memcache.", ""),
    "V1.3.10": (OK, "Los logs usan formato `%s` con argumentos; no hay format strings con datos externos.", ""),
    "V1.3.11": (NA, "No envía correo.", ""),
    "V1.5.1": (NA, "No procesa XML.", ""),
    "V1.5.2": (OK, "Solo deserializa JSON de Open-Meteo hacia modelos Pydantic tipados; sin pickle/yaml.", ""),
    # V2 Validación y lógica de negocio
    "V2.1.1": (PARTIAL, "Las reglas existen en código (`RANGES`/`clean()` en `schemas.py:11-32`) pero no están documentadas.", "H10"),
    "V2.1.2": (NA, "No hay combinaciones de datos de usuario que validar.", ""),
    "V2.1.3": (FAIL, "No hay límites documentados de uso (por cliente ni globales).", "H1, H10"),
    "V2.2.1": (OK, "Sin entrada de usuario; los datos upstream se validan contra rangos y se descartan si no cumplen.", ""),
    "V2.2.2": (OK, "La validación ocurre en el backend (`openmeteo.py:38-148`).", ""),
    "V2.2.3": (NA, "No hay datos relacionados de entrada.", ""),
    "V2.3.1": (NA, "No hay flujos de varios pasos.", ""),
    "V2.3.2": (FAIL, "Sin límites implementados (ni de tasa ni de concurrencia hacia upstream).", "H1"),
    "V2.3.3": (NA, "No hay transacciones.", ""),
    "V2.3.4": (NA, "No hay recursos de cantidad limitada.", ""),
    "V2.4.1": (FAIL, "Sin anti-automatización ni rate limit; 100 solicitudes concurrentes producen 300 llamadas upstream (`reports/cache_stampede.txt`).", "H1"),
    # V3 Seguridad del frontend web
    "V3.2.1": (PARTIAL, f"nosniff, CSP y Content-Type correctos en 200/404/503; las respuestas 500 salen sin cabeceras de seguridad (`{L}`).", "H9"),
    "V3.2.2": (OK, "React inserta texto con nodos de texto; sin `dangerouslySetInnerHTML`/`innerHTML` (grep).", ""),
    "V3.4.1": (FAIL, "No se envía Strict-Transport-Security (nuclei). Aplica al servir por HTTPS.", "H3, H7"),
    "V3.4.2": (OK, f"`Access-Control-Allow-Origin` solo para `localhost:5173`/`127.0.0.1:5173`; orígenes ajenos y `null` no lo reciben (`{M}`).", ""),
    "V3.4.3": (PARTIAL, "CSP restrictiva (`default-src 'self'`, `frame-ancestors 'none'`), pero `style-src 'unsafe-inline'` y ausente en respuestas 500.", "H4, H9"),
    "V3.4.4": (PARTIAL, "nosniff en todas las respuestas salvo las 500.", "H9"),
    "V3.4.5": (OK, "`Referrer-Policy: strict-origin-when-cross-origin` (OSM recibe solo el origen).", ""),
    "V3.4.6": (PARTIAL, "`frame-ancestors 'none'` + `X-Frame-Options: DENY`, salvo en respuestas 500.", "H9"),
    "V3.5.1": (NA, "No hay funcionalidad sensible; todo es lectura pública.", ""),
    "V3.5.2": (NA, "No hay funcionalidad sensible.", ""),
    "V3.5.3": (NA, f"No hay operaciones sensibles; los métodos no-GET devuelven 405 (`{M}`).", ""),
    "V3.5.4": (OK, "Una sola aplicación en un solo origen (FastAPI sirve API y frontend).", ""),
    "V3.5.5": (NA, "No usa `postMessage` (grep).", ""),
    "V3.7.1": (OK, "React 19, Leaflet 1.9 y Vite 8 vigentes; sin tecnologías obsoletas (`npm audit` limpio).", ""),
    "V3.7.2": (OK, "La app no redirige a otros dominios; los enlaces externos son constantes (Open-Meteo, OSM).", ""),
    # V4 API y servicios web
    "V4.1.1": (OK, "JSON `application/json`, HTML y JS con `charset=utf-8`.", ""),
    "V4.1.2": (DEPLOY, "Sin HTTPS en local; definir la redirección HTTP→HTTPS solo para la UI en el proxy.", "H7"),
    "V4.1.3": (NA, "No hay intermediarios hoy. Nota: uvicorn confía en `X-Forwarded-*` solo desde 127.0.0.1 por defecto.", ""),
    "V4.2.1": (OK, "Un solo componente HTTP (uvicorn con h11/httptools); revalidar si se añade un proxy.", ""),
    # V5 Archivos
    "V5.3.1": (NA, "No se almacenan archivos subidos; `dist` solo contiene el build estático.", ""),
    "V5.3.2": (OK, f"`StaticFiles` resuelve rutas dentro de `dist` y no sigue symlinks; traversal y `%2e%2e`/`%00` devuelven 404 (`{M}`).", ""),
    # V11 Criptografía
    "V11.2.1": (OK, "TLS saliente vía httpx sobre el módulo `ssl` estándar (OpenSSL).", ""),
    "V11.2.2": (NA, "No hay algoritmos criptográficos propios que rotar.", ""),
    "V11.2.3": (NA, "No hay primitivas criptográficas propias.", ""),
    # V12 Comunicaciones seguras
    "V12.1.1": (DEPLOY, "En local se sirve HTTP; versiones de TLS a definir en el proxy. Saliente: httpx negocia TLS 1.2+.", "H7"),
    "V12.1.2": (DEPLOY, "Suites de cifrado a definir en el proxy.", "H7"),
    "V12.1.3": (NA, "No usa mTLS.", ""),
    "V12.2.1": (DEPLOY, "Saliente a Open-Meteo siempre HTTPS (`config.py:6-7`); entrante sin TLS en local.", "H7"),
    "V12.2.2": (DEPLOY, "Certificado público a configurar en el despliegue.", "H7"),
    "V12.3.1": (PARTIAL, "Conexiones salientes cifradas; la entrante no (README sugiere `--host 0.0.0.0` sin TLS).", "H7"),
    "V12.3.2": (OK, "httpx valida certificados por defecto (`verify=True`, no se desactiva).", ""),
    "V12.3.3": (NA, "No hay servicios internos.", ""),
    "V12.3.4": (NA, "No hay servicios internos.", ""),
    # V13 Configuración
    "V13.1.1": (PARTIAL, "CLAUDE.md/README mencionan Open-Meteo y OSM, sin una sección formal de comunicaciones.", "H10"),
    "V13.2.1": (NA, "No hay otros componentes backend.", ""),
    "V13.2.2": (NA, "No hay otros componentes backend.", ""),
    "V13.2.3": (NA, "No hay credenciales de servicio.", ""),
    "V13.2.4": (OK, "Allowlist en código (`config.py`) y en el navegador (CSP `connect-src 'self'`, `img-src` solo OSM).", ""),
    "V13.2.5": (DEPLOY, "Sin restricción de salida a nivel de servidor/red; definir en el despliegue.", ""),
    "V13.4.1": (OK, f"`/.git/config` y `/.env` devuelven 404; solo se sirve `frontend/dist` (`{M}`).", ""),
    "V13.4.2": (OK, "FastAPI sin `debug`; sin `--reload` en el comando de producción.", ""),
    "V13.4.3": (OK, "`/assets/` y directorios sin `index.html` devuelven 404 (sin listado).", ""),
    "V13.4.4": (OK, f"TRACE devuelve 405 en `/api/*` y en `/` (`{M}`).", ""),
    "V13.4.5": (FAIL, "`/docs`, `/redoc` y `/openapi.json` públicos en producción (nuclei).", "H2"),
    # V14 Protección de datos
    "V14.1.1": (PARTIAL, "No se procesan datos sensibles (solo clima público), pero no está documentado.", "H10"),
    "V14.1.2": (NA, "No hay niveles de protección que definir sin datos sensibles.", ""),
    "V14.2.1": (OK, "No hay datos sensibles; las URLs no llevan información privada.", ""),
    "V14.2.2": (NA, "La caché del servidor solo guarda datos públicos del clima.", ""),
    "V14.2.3": (OK, "Sin rastreadores; terceros: OSM (mosaicos) recibe IP y origen, inherente al mapa y documentado en la atribución.", ""),
    "V14.2.4": (NA, "No hay datos sensibles.", ""),
    "V14.3.1": (NA, "No hay datos autenticados en el cliente.", ""),
    "V14.3.2": (NA, "Datos públicos; aun así falta `Cache-Control` explícito.", "H3"),
    "V14.3.3": (OK, "No usa localStorage/sessionStorage/IndexedDB/cookies (grep).", ""),
    # V15 Codificación segura y arquitectura
    "V15.1.1": (FAIL, "No hay plazos documentados para remediar dependencias vulnerables.", "H10"),
    "V15.1.2": (PARTIAL, "Dependencias fijadas (`requirements.txt`, `package-lock.json`), sin SBOM formal.", "H10"),
    "V15.1.3": (FAIL, "No se documenta que las llamadas a Open-Meteo son la operación costosa ni cómo protegerla.", "H1, H10"),
    "V15.2.1": (PARTIAL, "`pip-audit` y `npm audit` sin vulnerabilidades, pero sin plazos documentados contra los que medir.", "H10"),
    "V15.2.2": (FAIL, "Sin single-flight ni límite de tasa; tampoco límite de tamaño de respuesta upstream.", "H1, H8"),
    "V15.2.3": (PARTIAL, "Producción expone la documentación interactiva de la API.", "H2"),
    "V15.3.1": (OK, "Cada endpoint usa `response_model` con solo los campos necesarios.", ""),
    "V15.3.2": (OK, "httpx no sigue redirecciones por defecto y no se activa `follow_redirects`.", ""),
    "V15.3.3": (NA, "No hay escrituras ni enlace de cuerpo a modelos.", ""),
    "V15.3.4": (NA, "La app no usa la IP del cliente.", ""),
    "V15.3.5": (OK, "Tipos estrictos con Pydantic; conversiones explícitas en `openmeteo.py` (`_code`, `_dt`).", ""),
    "V15.3.6": (OK, "Sin fusiones de objetos con claves externas (`Object.assign`, spread de respuestas: grep sin resultados).", ""),
    "V15.3.7": (NA, "La API no lee parámetros.", ""),
    # V16 Registro y manejo de errores
    "V16.1.1": (FAIL, "No hay inventario de logs.", "H10, H11"),
    "V16.2.1": (FAIL, "Con `uvicorn app.main:app` los logs de la app salen sin fecha, nivel ni origen (logging sin configurar).", "H11"),
    "V16.2.2": (FAIL, "Sin marca de tiempo en los logs de la app.", "H11"),
    "V16.2.3": (PARTIAL, "Solo se escribe a stderr; no hay destino documentado.", "H11"),
    "V16.2.4": (FAIL, "Formato libre sin estructura.", "H11"),
    "V16.2.5": (OK, "No se registran datos sensibles; solo ruta y tipo de error.", ""),
    "V16.3.1": (NA, "No hay autenticación.", ""),
    "V16.3.2": (NA, "No hay autorización.", ""),
    "V16.3.3": (PARTIAL, "No hay eventos de seguridad definidos; 404/405 solo quedan en el access log de uvicorn.", "H10"),
    "V16.3.4": (OK, f"Fallos upstream (incluidos errores TLS/transporte) y errores inesperados se registran con detalle (`{L}`).", ""),
    "V16.4.1": (OK, "Las rutas registradas son las de endpoints ya resueltos (constantes); uvicorn codifica la ruta en el access log.", ""),
    "V16.4.2": (DEPLOY, "Depende de dónde se guarde stderr en el despliegue.", "H11"),
    "V16.4.3": (DEPLOY, "No hay envío a un sistema separado.", "H11"),
    "V16.5.1": (OK, f"Prueba en vivo: 503 (upstream caído o JSON malformado) y 500 (excepción) devuelven solo el mensaje genérico; el detalle queda en el log (`{L}`).", ""),
    "V16.5.2": (OK, "Degradación controlada: datos en caché marcados `stale=true` si upstream falla; reintentos con backoff.", ""),
    "V16.5.3": (OK, "Ante error se responde 5xx; no hay estados que puedan quedar abiertos.", ""),
}


def evaluate(req):
    if req["req_id"] in EVAL:
        return EVAL[req["req_id"]]
    if req["section_id"] in SECTION_NA:
        return (NA, SECTION_NA[req["section_id"]], "")
    if req["chapter_id"] in CHAPTER_NA:
        return (NA, CHAPTER_NA[req["chapter_id"]], "")
    return ("Sin evaluar", "", "")


def esc(text):
    return text.replace("|", "\\|").replace("\n", " ")


def main():
    with CSV.open(encoding="utf-8-sig") as f:
        reqs = [r for r in csv.DictReader(f) if r["L"] in ("1", "2")]

    rows = [(r, *evaluate(r)) for r in reqs]
    by_chapter = defaultdict(Counter)
    names = {}
    for r, state, _, _ in rows:
        by_chapter[r["chapter_id"]][state] += 1
        names[r["chapter_id"]] = r["chapter_name"]
    total = Counter(state for _, state, _, _ in rows)
    unevaluated = [r["req_id"] for r, state, _, _ in rows if state == "Sin evaluar"]
    chapters = sorted(by_chapter, key=lambda c: int(c[1:]))

    out = [
        "# Checklist OWASP ASVS 5.0.0 — API weatherproject",
        "",
        "Generado por `scripts/asvs_checklist.py` desde el CSV oficial (`asvs/`). Alcance: niveles 1 y 2 "
        f"({len(reqs)} requisitos). Evaluación local del 2026-10-05. Hallazgos `H#` en `INFORME.md`.",
        "",
        "Estados: **Cumple**; **Parcial**; **No cumple**; **Despliegue** (no evaluable en local: TLS, proxy, "
        "almacenamiento de logs); **N/A** (la funcionalidad no existe en la app).",
        "",
        "## Resumen",
        "",
        "| Capítulo | " + " | ".join(STATES) + " | Total |",
        "|---" * (len(STATES) + 2) + "|",
    ]
    for c in chapters:
        cnt = by_chapter[c]
        out.append(f"| {c} {names[c]} | " + " | ".join(str(cnt[s]) for s in STATES) + f" | {sum(cnt.values())} |")
    out.append("| **Total** | " + " | ".join(f"**{total[s]}**" for s in STATES) + f" | **{len(reqs)}** |")
    applicable = len(reqs) - total[NA]
    out += [
        "",
        f"Aplicables (sin N/A): {applicable}. Cumplen {total[OK]}, parciales {total[PARTIAL]}, "
        f"no cumplen {total[FAIL]}, pendientes de despliegue {total[DEPLOY]}.",
        "",
    ]

    for c in chapters:
        out += [f"## {c} {names[c]}", ""]
        chapter_rows = [x for x in rows if x[0]["chapter_id"] == c]
        if c in CHAPTER_NA and all(s == NA for _, s, _, _ in chapter_rows):
            out += [f"**N/A** ({len(chapter_rows)} requisitos): {CHAPTER_NA[c]}", ""]
            continue
        out += ["| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |", "|---|---|---|---|---|---|"]
        for r, state, evidence, finding in chapter_rows:
            desc = r["req_description"]
            short = desc if len(desc) <= 160 else desc[:157] + "…"
            out.append(f"| {r['req_id']} | L{r['L']} | {esc(short)} | {state} | {esc(evidence)} | {finding} |")
        out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"{OUT.name}: {len(reqs)} requisitos; " + ", ".join(f"{s}={total[s]}" for s in STATES))
    if unevaluated:
        print("Sin evaluar:", ", ".join(unevaluated))
        sys.exit(1)


if __name__ == "__main__":
    main()
