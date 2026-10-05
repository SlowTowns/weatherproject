# Checklist OWASP ASVS 5.0.0 — API weatherproject

Generado por `scripts/asvs_checklist.py` desde el CSV oficial (`asvs/`). Alcance: niveles 1 y 2 (253 requisitos). Evaluación local del 2026-10-05. Hallazgos `H#` en `INFORME.md`.

Estados: **Cumple**; **Parcial**; **No cumple**; **Despliegue** (no evaluable en local: TLS, proxy, almacenamiento de logs); **N/A** (la funcionalidad no existe en la app).

## Resumen

| Capítulo | Cumple | Parcial | No cumple | Despliegue | N/A | Total |
|---|---|---|---|---|---|---|
| V1 Encoding and Sanitization | 9 | 0 | 0 | 0 | 18 | 27 |
| V2 Validation and Business Logic | 2 | 1 | 3 | 0 | 5 | 11 |
| V3 Web Frontend Security | 6 | 4 | 1 | 0 | 8 | 19 |
| V4 API and Web Service | 2 | 0 | 0 | 1 | 7 | 10 |
| V5 File Handling | 1 | 0 | 0 | 0 | 8 | 9 |
| V6 Authentication | 0 | 0 | 0 | 0 | 35 | 35 |
| V7 Session Management | 0 | 0 | 0 | 0 | 18 | 18 |
| V8 Authorization | 0 | 0 | 0 | 0 | 7 | 7 |
| V9 Self-contained Tokens | 0 | 0 | 0 | 0 | 7 | 7 |
| V10 OAuth and OIDC | 0 | 0 | 0 | 0 | 29 | 29 |
| V11 Cryptography | 1 | 0 | 0 | 0 | 13 | 14 |
| V12 Secure Communication | 1 | 1 | 0 | 4 | 3 | 9 |
| V13 Configuration | 5 | 1 | 1 | 1 | 5 | 13 |
| V14 Data Protection | 3 | 1 | 0 | 0 | 5 | 9 |
| V15 Secure Coding and Architecture | 4 | 3 | 3 | 0 | 3 | 13 |
| V16 Security Logging and Error Handling | 6 | 2 | 4 | 2 | 2 | 16 |
| V17 WebRTC | 0 | 0 | 0 | 0 | 7 | 7 |
| **Total** | **40** | **13** | **12** | **8** | **180** | **253** |

Aplicables (sin N/A): 73. Cumplen 40, parciales 13, no cumplen 12, pendientes de despliegue 8.

## V1 Encoding and Sanitization

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V1.1.1 | L2 | Verify that input is decoded or unescaped into a canonical form only once, it is only decoded when encoded data in that form is expected, and that this is do… | N/A | No hay entrada de usuario que decodificar; la API no recibe parámetros ni cuerpo. |  |
| V1.1.2 | L2 | Verify that the application performs output encoding and escaping either as a final step before being used by the interpreter for which it is intended or by … | Cumple | FastAPI/Pydantic serializan JSON al final; React escapa al renderizar. |  |
| V1.2.1 | L1 | Verify that output encoding for an HTTP response, HTML document, or XML document is relevant for the context required, such as encoding the relevant characte… | Cumple | JSON con Content-Type correcto; React escapa texto. El único HTML construido (`L.divIcon` en `MapCard.jsx:13`) recibe `Number(...).toLocaleString()`, que solo produce dígitos. |  |
| V1.2.2 | L1 | Verify that when dynamically building URLs, untrusted data is encoded according to its context (e.g., URL encoding or base64url encoding for query or path pa… | Cumple | URLs salientes constantes (`config.py`) con params codificados por httpx; en el cliente, `URLSearchParams` (`themes.js:41`). |  |
| V1.2.3 | L1 | Verify that output encoding or escaping is used when dynamically building JavaScript content (including JSON), to avoid changing the message or document stru… | Cumple | JSON generado por el serializador de FastAPI/Pydantic, nunca por concatenación. |  |
| V1.2.4 | L1 | Verify that data selection or database queries (e.g., SQL, HQL, NoSQL, Cypher) use parameterized queries, ORMs, entity frameworks, or are otherwise protected… | N/A | No hay base de datos. |  |
| V1.2.5 | L1 | Verify that the application protects against OS command injection and that operating system calls use parameterized OS queries or use contextual command line… | N/A | No hay llamadas al sistema operativo (bandit sin B602/B603/B605). |  |
| V1.2.6 | L2 | Verify that the application protects against LDAP injection vulnerabilities, or that specific security controls to prevent LDAP injection have been implemented. | N/A | No usa LDAP. |  |
| V1.2.7 | L2 | Verify that the application is protected against XPath injection attacks by using query parameterization or precompiled queries. | N/A | No usa XPath. |  |
| V1.2.8 | L2 | Verify that LaTeX processors are configured securely (such as not using the "--shell-escape" flag) and an allowlist of commands is used to prevent LaTeX inje… | N/A | No usa LaTeX. |  |
| V1.2.9 | L2 | Verify that the application escapes special characters in regular expressions (typically using a backslash) to prevent them from being misinterpreted as meta… | N/A | No construye expresiones regulares con datos externos. |  |
| V1.3.1 | L1 | Verify that all untrusted HTML input from WYSIWYG editors or similar is sanitized using a well-known and secure HTML sanitization library or framework feature. | N/A | No acepta HTML de usuario. |  |
| V1.3.2 | L1 | Verify that the application avoids the use of eval() or other dynamic code execution features such as Spring Expression Language (SpEL). Where there is no al… | Cumple | Sin `eval`/`new Function` en `frontend/src` (grep) ni en backend (bandit). |  |
| V1.3.3 | L2 | Verify that data being passed to a potentially dangerous context is sanitized beforehand to enforce safety measures, such as only allowing characters which a… | Cumple | Único contexto peligroso: HTML de `divIcon`, alimentado con un número formateado. |  |
| V1.3.4 | L2 | Verify that user-supplied Scalable Vector Graphics (SVG) scriptable content is validated or sanitized to contain only tags and attributes (such as draw graph… | N/A | Los SVG son recursos propios del build; no hay SVG de usuario. |  |
| V1.3.5 | L2 | Verify that the application sanitizes or disables user-supplied scriptable or expression template language content, such as Markdown, CSS or XSL stylesheets,… | N/A | No procesa Markdown, plantillas ni CSS de usuario. |  |
| V1.3.6 | L2 | Verify that the application protects against Server-side Request Forgery (SSRF) attacks, by validating untrusted data against an allowlist of protocols, doma… | Cumple | Sin SSRF: destinos y parámetros salientes son constantes (`config.py:6-7`); ninguna entrada llega a la URL. |  |
| V1.3.7 | L2 | Verify that the application protects against template injection attacks by not allowing templates to be built based on untrusted input. Where there is no alt… | N/A | No usa plantillas del servidor. |  |
| V1.3.8 | L2 | Verify that the application appropriately sanitizes untrusted input before use in Java Naming and Directory Interface (JNDI) queries and that JNDI is configu… | N/A | No usa JNDI. |  |
| V1.3.9 | L2 | Verify that the application sanitizes content before it is sent to memcache to prevent injection attacks. | N/A | Caché en memoria con claves constantes (`forecast`, `air_quality`); no usa memcache. |  |
| V1.3.10 | L2 | Verify that format strings which might resolve in an unexpected or malicious way when used are sanitized before being processed. | Cumple | Los logs usan formato `%s` con argumentos; no hay format strings con datos externos. |  |
| V1.3.11 | L2 | Verify that the application sanitizes user input before passing to mail systems to protect against SMTP or IMAP injection. | N/A | No envía correo. |  |
| V1.4.1 | L2 | Verify that the application uses memory-safe string, safer memory copy and pointer arithmetic to detect or prevent stack, buffer, or heap overflows. | N/A | Python y JavaScript gestionan la memoria; no hay código nativo propio. |  |
| V1.4.2 | L2 | Verify that sign, range, and input validation techniques are used to prevent integer overflows. | N/A | Python y JavaScript gestionan la memoria; no hay código nativo propio. |  |
| V1.4.3 | L2 | Verify that dynamically allocated memory and resources are released, and that references or pointers to freed memory are removed or set to null to prevent da… | N/A | Python y JavaScript gestionan la memoria; no hay código nativo propio. |  |
| V1.5.1 | L1 | Verify that the application configures XML parsers to use a restrictive configuration and that unsafe features such as resolving external entities are disabl… | N/A | No procesa XML. |  |
| V1.5.2 | L2 | Verify that deserialization of untrusted data enforces safe input handling, such as using an allowlist of object types or restricting client-defined object t… | Cumple | Solo deserializa JSON de Open-Meteo hacia modelos Pydantic tipados; sin pickle/yaml. |  |

## V2 Validation and Business Logic

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V2.1.1 | L1 | Verify that the application's documentation defines input validation rules for how to check the validity of data items against an expected structure. This co… | Parcial | Las reglas existen en código (`RANGES`/`clean()` en `schemas.py:11-32`) pero no están documentadas. | H10 |
| V2.1.2 | L2 | Verify that the application's documentation defines how to validate the logical and contextual consistency of combined data items, such as checking that subu… | N/A | No hay combinaciones de datos de usuario que validar. |  |
| V2.1.3 | L2 | Verify that expectations for business logic limits and validations are documented, including both per-user and globally across the application. | No cumple | No hay límites documentados de uso (por cliente ni globales). | H1, H10 |
| V2.2.1 | L1 | Verify that input is validated to enforce business or functional expectations for that input. This should either use positive validation against an allow lis… | Cumple | Sin entrada de usuario; los datos upstream se validan contra rangos y se descartan si no cumplen. |  |
| V2.2.2 | L1 | Verify that the application is designed to enforce input validation at a trusted service layer. While client-side validation improves usability and should be… | Cumple | La validación ocurre en el backend (`openmeteo.py:38-148`). |  |
| V2.2.3 | L2 | Verify that the application ensures that combinations of related data items are reasonable according to the pre-defined rules. | N/A | No hay datos relacionados de entrada. |  |
| V2.3.1 | L1 | Verify that the application will only process business logic flows for the same user in the expected sequential step order and without skipping steps. | N/A | No hay flujos de varios pasos. |  |
| V2.3.2 | L2 | Verify that business logic limits are implemented per the application's documentation to avoid business logic flaws being exploited. | No cumple | Sin límites implementados (ni de tasa ni de concurrencia hacia upstream). | H1 |
| V2.3.3 | L2 | Verify that transactions are being used at the business logic level such that either a business logic operation succeeds in its entirety or it is rolled back… | N/A | No hay transacciones. |  |
| V2.3.4 | L2 | Verify that business logic level locking mechanisms are used to ensure that limited quantity resources (such as theater seats or delivery slots) cannot be do… | N/A | No hay recursos de cantidad limitada. |  |
| V2.4.1 | L2 | Verify that anti-automation controls are in place to protect against excessive calls to application functions that could lead to data exfiltration, garbage-d… | No cumple | Sin anti-automatización ni rate limit; 100 solicitudes concurrentes producen 300 llamadas upstream (`reports/cache_stampede.txt`). | H1 |

## V3 Web Frontend Security

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V3.2.1 | L1 | Verify that security controls are in place to prevent browsers from rendering content or functionality in HTTP responses in an incorrect context (e.g., when … | Parcial | nosniff, CSP y Content-Type correctos en 200/404/503; las respuestas 500 salen sin cabeceras de seguridad (`reports/live_errors.txt`). | H9 |
| V3.2.2 | L1 | Verify that content intended to be displayed as text, rather than rendered as HTML, is handled using safe rendering functions (such as createTextNode or text… | Cumple | React inserta texto con nodos de texto; sin `dangerouslySetInnerHTML`/`innerHTML` (grep). |  |
| V3.3.1 | L1 | Verify that cookies have the 'Secure' attribute set, and if the '\__Host-' prefix is not used for the cookie name, the '__Secure-' prefix must be used for th… | N/A | La app no emite cookies (verificado con curl en todas las respuestas). |  |
| V3.3.2 | L2 | Verify that each cookie's 'SameSite' attribute value is set according to the purpose of the cookie, to limit exposure to user interface redress attacks and b… | N/A | La app no emite cookies (verificado con curl en todas las respuestas). |  |
| V3.3.3 | L2 | Verify that cookies have the '__Host-' prefix for the cookie name unless they are explicitly designed to be shared with other hosts. | N/A | La app no emite cookies (verificado con curl en todas las respuestas). |  |
| V3.3.4 | L2 | Verify that if the value of a cookie is not meant to be accessible to client-side scripts (such as a session token), the cookie must have the 'HttpOnly' attr… | N/A | La app no emite cookies (verificado con curl en todas las respuestas). |  |
| V3.4.1 | L1 | Verify that a Strict-Transport-Security header field is included on all responses to enforce an HTTP Strict Transport Security (HSTS) policy. A maximum age o… | No cumple | No se envía Strict-Transport-Security (nuclei). Aplica al servir por HTTPS. | H3, H7 |
| V3.4.2 | L1 | Verify that the Cross-Origin Resource Sharing (CORS) Access-Control-Allow-Origin header field is a fixed value by the application, or if the Origin HTTP requ… | Cumple | `Access-Control-Allow-Origin` solo para `localhost:5173`/`127.0.0.1:5173`; orígenes ajenos y `null` no lo reciben (`reports/manual_tests.txt`). |  |
| V3.4.3 | L2 | Verify that HTTP responses include a Content-Security-Policy response header field which defines directives to ensure the browser only loads and executes tru… | Parcial | CSP restrictiva (`default-src 'self'`, `frame-ancestors 'none'`), pero `style-src 'unsafe-inline'` y ausente en respuestas 500. | H4, H9 |
| V3.4.4 | L2 | Verify that all HTTP responses contain an 'X-Content-Type-Options: nosniff' header field. This instructs browsers not to use content sniffing and MIME type g… | Parcial | nosniff en todas las respuestas salvo las 500. | H9 |
| V3.4.5 | L2 | Verify that the application sets a referrer policy to prevent leakage of technically sensitive data to third-party services via the 'Referer' HTTP request he… | Cumple | `Referrer-Policy: strict-origin-when-cross-origin` (OSM recibe solo el origen). |  |
| V3.4.6 | L2 | Verify that the web application uses the frame-ancestors directive of the Content-Security-Policy header field for every HTTP response to ensure that it cann… | Parcial | `frame-ancestors 'none'` + `X-Frame-Options: DENY`, salvo en respuestas 500. | H9 |
| V3.5.1 | L1 | Verify that, if the application does not rely on the CORS preflight mechanism to prevent disallowed cross-origin requests to use sensitive functionality, the… | N/A | No hay funcionalidad sensible; todo es lectura pública. |  |
| V3.5.2 | L1 | Verify that, if the application relies on the CORS preflight mechanism to prevent disallowed cross-origin use of sensitive functionality, it is not possible … | N/A | No hay funcionalidad sensible. |  |
| V3.5.3 | L1 | Verify that HTTP requests to sensitive functionality use appropriate HTTP methods such as POST, PUT, PATCH, or DELETE, and not methods defined by the HTTP sp… | N/A | No hay operaciones sensibles; los métodos no-GET devuelven 405 (`reports/manual_tests.txt`). |  |
| V3.5.4 | L2 | Verify that separate applications are hosted on different hostnames to leverage the restrictions provided by same-origin policy, including how documents or s… | Cumple | Una sola aplicación en un solo origen (FastAPI sirve API y frontend). |  |
| V3.5.5 | L2 | Verify that messages received by the postMessage interface are discarded if the origin of the message is not trusted, or if the syntax of the message is inva… | N/A | No usa `postMessage` (grep). |  |
| V3.7.1 | L2 | Verify that the application only uses client-side technologies which are still supported and considered secure. Examples of technologies which do not meet th… | Cumple | React 19, Leaflet 1.9 y Vite 8 vigentes; sin tecnologías obsoletas (`npm audit` limpio). |  |
| V3.7.2 | L2 | Verify that the application will only automatically redirect the user to a different hostname or domain (which is not controlled by the application) where th… | Cumple | La app no redirige a otros dominios; los enlaces externos son constantes (Open-Meteo, OSM). |  |

## V4 API and Web Service

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V4.1.1 | L1 | Verify that every HTTP response with a message body contains a Content-Type header field that matches the actual content of the response, including the chars… | Cumple | JSON `application/json`, HTML y JS con `charset=utf-8`. |  |
| V4.1.2 | L2 | Verify that only user-facing endpoints (intended for manual web-browser access) automatically redirect from HTTP to HTTPS, while other services or endpoints … | Despliegue | Sin HTTPS en local; definir la redirección HTTP→HTTPS solo para la UI en el proxy. | H7 |
| V4.1.3 | L2 | Verify that any HTTP header field used by the application and set by an intermediary layer, such as a load balancer, a web proxy, or a backend-for-frontend s… | N/A | No hay intermediarios hoy. Nota: uvicorn confía en `X-Forwarded-*` solo desde 127.0.0.1 por defecto. |  |
| V4.2.1 | L2 | Verify that all application components (including load balancers, firewalls, and application servers) determine boundaries of incoming HTTP messages using th… | Cumple | Un solo componente HTTP (uvicorn con h11/httptools); revalidar si se añade un proxy. |  |
| V4.3.1 | L2 | Verify that a query allowlist, depth limiting, amount limiting, or query cost analysis is used to prevent GraphQL or data layer expression Denial of Service … | N/A | No usa GraphQL. |  |
| V4.3.2 | L2 | Verify that GraphQL introspection queries are disabled in the production environment unless the GraphQL API is meant to be used by other parties. | N/A | No usa GraphQL. |  |
| V4.4.1 | L1 | Verify that WebSocket over TLS (WSS) is used for all WebSocket connections. | N/A | No usa WebSocket. |  |
| V4.4.2 | L2 | Verify that, during the initial HTTP WebSocket handshake, the Origin header field is checked against a list of origins allowed for the application. | N/A | No usa WebSocket. |  |
| V4.4.3 | L2 | Verify that, if the application's standard session management cannot be used, dedicated tokens are being used for this, which comply with the relevant Sessio… | N/A | No usa WebSocket. |  |
| V4.4.4 | L2 | Verify that dedicated WebSocket session management tokens are initially obtained or validated through the previously authenticated HTTPS session when transit… | N/A | No usa WebSocket. |  |

## V5 File Handling

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V5.1.1 | L2 | Verify that the documentation defines the permitted file types, expected file extensions, and maximum size (including unpacked size) for each upload feature.… | N/A | No hay subida ni descarga de archivos de usuario. |  |
| V5.2.1 | L1 | Verify that the application will only accept files of a size which it can process without causing a loss of performance or a denial of service attack. | N/A | No hay subida de archivos. |  |
| V5.2.2 | L1 | Verify that when the application accepts a file, either on its own or within an archive such as a zip file, it checks if the file extension matches an expect… | N/A | No hay subida de archivos. |  |
| V5.2.3 | L2 | Verify that the application checks compressed files (e.g., zip, gz, docx, odt) against maximum allowed uncompressed size and against maximum number of files … | N/A | No hay subida de archivos. |  |
| V5.3.1 | L1 | Verify that files uploaded or generated by untrusted input and stored in a public folder, are not executed as server-side program code when accessed directly… | N/A | No se almacenan archivos subidos; `dist` solo contiene el build estático. |  |
| V5.3.2 | L1 | Verify that when the application creates file paths for file operations, instead of user-submitted filenames, it uses internally generated or trusted data, o… | Cumple | `StaticFiles` resuelve rutas dentro de `dist` y no sigue symlinks; traversal y `%2e%2e`/`%00` devuelven 404 (`reports/manual_tests.txt`). |  |
| V5.4.1 | L2 | Verify that the application validates or ignores user-submitted filenames, including in a JSON, JSONP, or URL parameter and specifies a filename in the Conte… | N/A | No hay descarga de archivos con nombre controlado por el usuario. |  |
| V5.4.2 | L2 | Verify that file names served (e.g., in HTTP response header fields or email attachments) are encoded or sanitized (e.g., following RFC 6266) to preserve doc… | N/A | No hay descarga de archivos con nombre controlado por el usuario. |  |
| V5.4.3 | L2 | Verify that files obtained from untrusted sources are scanned by antivirus scanners to prevent serving of known malicious content. | N/A | No hay descarga de archivos con nombre controlado por el usuario. |  |

## V6 Authentication

**N/A** (35 requisitos): La app no tiene usuarios, autenticación, sesiones, tokens ni cookies: API pública de solo lectura.

## V7 Session Management

**N/A** (18 requisitos): La app no tiene usuarios, autenticación, sesiones, tokens ni cookies: API pública de solo lectura.

## V8 Authorization

**N/A** (7 requisitos): Sin autorización: todos los recursos son públicos por diseño (datos del clima abiertos).

## V9 Self-contained Tokens

**N/A** (7 requisitos): La app no tiene usuarios, autenticación, sesiones, tokens ni cookies: API pública de solo lectura.

## V10 OAuth and OIDC

**N/A** (29 requisitos): No usa OAuth ni OIDC.

## V11 Cryptography

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V11.1.1 | L2 | Verify that there is a documented policy for management of cryptographic keys and a cryptographic key lifecycle that follows a key management standard such a… | N/A | La app no gestiona claves ni cripto propia; TLS lo aporta httpx/ssl de la biblioteca estándar. |  |
| V11.1.2 | L2 | Verify that a cryptographic inventory is performed, maintained, regularly updated, and includes all cryptographic keys, algorithms, and certificates used by … | N/A | La app no gestiona claves ni cripto propia; TLS lo aporta httpx/ssl de la biblioteca estándar. |  |
| V11.2.1 | L2 | Verify that industry-validated implementations (including libraries and hardware-accelerated implementations) are used for cryptographic operations. | Cumple | TLS saliente vía httpx sobre el módulo `ssl` estándar (OpenSSL). |  |
| V11.2.2 | L2 | Verify that the application is designed with crypto agility such that random number, authenticated encryption, MAC, or hashing algorithms, key lengths, round… | N/A | No hay algoritmos criptográficos propios que rotar. |  |
| V11.2.3 | L2 | Verify that all cryptographic primitives utilize a minimum of 128-bits of security based on the algorithm, key size, and configuration. For example, a 256-bi… | N/A | No hay primitivas criptográficas propias. |  |
| V11.3.1 | L1 | Verify that insecure block modes (e.g., ECB) and weak padding schemes (e.g., PKCS#1 v1.5) are not used. | N/A | No cifra datos. |  |
| V11.3.2 | L1 | Verify that only approved ciphers and modes such as AES with GCM are used. | N/A | No cifra datos. |  |
| V11.3.3 | L2 | Verify that encrypted data is protected against unauthorized modification preferably by using an approved authenticated encryption method or by combining an … | N/A | No cifra datos. |  |
| V11.4.1 | L1 | Verify that only approved hash functions are used for general cryptographic use cases, including digital signatures, HMAC, KDF, and random bit generation. Di… | N/A | No usa hashes criptográficos ni contraseñas. |  |
| V11.4.2 | L2 | Verify that passwords are stored using an approved, computationally intensive, key derivation function (also known as a "password hashing function"), with pa… | N/A | No usa hashes criptográficos ni contraseñas. |  |
| V11.4.3 | L2 | Verify that hash functions used in digital signatures, as part of data authentication or data integrity are collision resistant and have appropriate bit-leng… | N/A | No usa hashes criptográficos ni contraseñas. |  |
| V11.4.4 | L2 | Verify that the application uses approved key derivation functions with key stretching parameters when deriving secret keys from passwords. The parameters in… | N/A | No usa hashes criptográficos ni contraseñas. |  |
| V11.5.1 | L2 | Verify that all random numbers and strings which are intended to be non-guessable must be generated using a cryptographically secure pseudo-random number gen… | N/A | No genera valores aleatorios con fines de seguridad. |  |
| V11.6.1 | L2 | Verify that only approved cryptographic algorithms and modes of operation are used for key generation and seeding, and digital signature generation and verif… | N/A | No usa criptografía de clave pública propia. |  |

## V12 Secure Communication

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V12.1.1 | L1 | Verify that only the latest recommended versions of the TLS protocol are enabled, such as TLS 1.2 and TLS 1.3. The latest version of the TLS protocol must be… | Despliegue | En local se sirve HTTP; versiones de TLS a definir en el proxy. Saliente: httpx negocia TLS 1.2+. | H7 |
| V12.1.2 | L2 | Verify that only recommended cipher suites are enabled, with the strongest cipher suites set as preferred. L3 applications must only support cipher suites wh… | Despliegue | Suites de cifrado a definir en el proxy. | H7 |
| V12.1.3 | L2 | Verify that the application validates that mTLS client certificates are trusted before using the certificate identity for authentication or authorization. | N/A | No usa mTLS. |  |
| V12.2.1 | L1 | Verify that TLS is used for all connectivity between a client and external facing, HTTP-based services, and does not fall back to insecure or unencrypted com… | Despliegue | Saliente a Open-Meteo siempre HTTPS (`config.py:6-7`); entrante sin TLS en local. | H7 |
| V12.2.2 | L1 | Verify that external facing services use publicly trusted TLS certificates. | Despliegue | Certificado público a configurar en el despliegue. | H7 |
| V12.3.1 | L2 | Verify that an encrypted protocol such as TLS is used for all inbound and outbound connections to and from the application, including monitoring systems, man… | Parcial | Conexiones salientes cifradas; la entrante no (README sugiere `--host 0.0.0.0` sin TLS). | H7 |
| V12.3.2 | L2 | Verify that TLS clients validate certificates received before communicating with a TLS server. | Cumple | httpx valida certificados por defecto (`verify=True`, no se desactiva). |  |
| V12.3.3 | L2 | Verify that TLS or another appropriate transport encryption mechanism used for all connectivity between internal, HTTP-based services within the application,… | N/A | No hay servicios internos. |  |
| V12.3.4 | L2 | Verify that TLS connections between internal services use trusted certificates. Where internally generated or self-signed certificates are used, the consumin… | N/A | No hay servicios internos. |  |

## V13 Configuration

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V13.1.1 | L2 | Verify that all communication needs for the application are documented. This must include external services which the application relies upon and cases where… | Parcial | CLAUDE.md/README mencionan Open-Meteo y OSM, sin una sección formal de comunicaciones. | H10 |
| V13.2.1 | L2 | Verify that communications between backend application components that don't support the application's standard user session mechanism, including APIs, middl… | N/A | No hay otros componentes backend. |  |
| V13.2.2 | L2 | Verify that communications between backend application components, including local or operating system services, APIs, middleware, and data layers, are perfo… | N/A | No hay otros componentes backend. |  |
| V13.2.3 | L2 | Verify that if a credential has to be used for service authentication, the credential being used by the consumer is not a default credential (e.g., root/root… | N/A | No hay credenciales de servicio. |  |
| V13.2.4 | L2 | Verify that an allowlist is used to define the external resources or systems with which the application is permitted to communicate (e.g., for outbound reque… | Cumple | Allowlist en código (`config.py`) y en el navegador (CSP `connect-src 'self'`, `img-src` solo OSM). |  |
| V13.2.5 | L2 | Verify that the web or application server is configured with an allowlist of resources or systems to which the server can send requests or load data or files… | Despliegue | Sin restricción de salida a nivel de servidor/red; definir en el despliegue. |  |
| V13.3.1 | L2 | Verify that a secrets management solution, such as a key vault, is used to securely create, store, control access to, and destroy backend secrets. These coul… | N/A | No hay secretos: Open-Meteo y OSM no requieren API key (grep de claves sin resultados). |  |
| V13.3.2 | L2 | Verify that access to secret assets adheres to the principle of least privilege. | N/A | No hay secretos: Open-Meteo y OSM no requieren API key (grep de claves sin resultados). |  |
| V13.4.1 | L1 | Verify that the application is deployed either without any source control metadata, including the .git or .svn folders, or in a way that these folders are in… | Cumple | `/.git/config` y `/.env` devuelven 404; solo se sirve `frontend/dist` (`reports/manual_tests.txt`). |  |
| V13.4.2 | L2 | Verify that debug modes are disabled for all components in production environments to prevent exposure of debugging features and information leakage. | Cumple | FastAPI sin `debug`; sin `--reload` en el comando de producción. |  |
| V13.4.3 | L2 | Verify that web servers do not expose directory listings to clients unless explicitly intended. | Cumple | `/assets/` y directorios sin `index.html` devuelven 404 (sin listado). |  |
| V13.4.4 | L2 | Verify that using the HTTP TRACE method is not supported in production environments, to avoid potential information leakage. | Cumple | TRACE devuelve 405 en `/api/*` y en `/` (`reports/manual_tests.txt`). |  |
| V13.4.5 | L2 | Verify that documentation (such as for internal APIs) and monitoring endpoints are not exposed unless explicitly intended. | No cumple | `/docs`, `/redoc` y `/openapi.json` públicos en producción (nuclei). | H2 |

## V14 Data Protection

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V14.1.1 | L2 | Verify that all sensitive data created and processed by the application has been identified and classified into protection levels. This includes data that is… | Parcial | No se procesan datos sensibles (solo clima público), pero no está documentado. | H10 |
| V14.1.2 | L2 | Verify that all sensitive data protection levels have a documented set of protection requirements. This must include (but not be limited to) requirements rel… | N/A | No hay niveles de protección que definir sin datos sensibles. |  |
| V14.2.1 | L1 | Verify that sensitive data is only sent to the server in the HTTP message body or header fields, and that the URL and query string do not contain sensitive i… | Cumple | No hay datos sensibles; las URLs no llevan información privada. |  |
| V14.2.2 | L2 | Verify that the application prevents sensitive data from being cached in server components, such as load balancers and application caches, or ensures that th… | N/A | La caché del servidor solo guarda datos públicos del clima. |  |
| V14.2.3 | L2 | Verify that defined sensitive data is not sent to untrusted parties (e.g., user trackers) to prevent unwanted collection of data outside of the application's… | Cumple | Sin rastreadores; terceros: OSM (mosaicos) recibe IP y origen, inherente al mapa y documentado en la atribución. |  |
| V14.2.4 | L2 | Verify that controls around sensitive data related to encryption, integrity verification, retention, how the data is to be logged, access controls around sen… | N/A | No hay datos sensibles. |  |
| V14.3.1 | L1 | Verify that authenticated data is cleared from client storage, such as the browser DOM, after the client or session is terminated. The 'Clear-Site-Data' HTTP… | N/A | No hay datos autenticados en el cliente. |  |
| V14.3.2 | L2 | Verify that the application sets sufficient anti-caching HTTP response header fields (i.e., Cache-Control: no-store) so that sensitive data is not cached in … | N/A | Datos públicos; aun así falta `Cache-Control` explícito. | H3 |
| V14.3.3 | L2 | Verify that data stored in browser storage (such as localStorage, sessionStorage, IndexedDB, or cookies) does not contain sensitive data, with the exception … | Cumple | No usa localStorage/sessionStorage/IndexedDB/cookies (grep). |  |

## V15 Secure Coding and Architecture

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V15.1.1 | L1 | Verify that application documentation defines risk based remediation time frames for 3rd party component versions with vulnerabilities and for updating libra… | No cumple | No hay plazos documentados para remediar dependencias vulnerables. | H10 |
| V15.1.2 | L2 | Verify that an inventory catalog, such as software bill of materials (SBOM), is maintained of all third-party libraries in use, including verifying that comp… | Parcial | Dependencias fijadas (`requirements.txt`, `package-lock.json`), sin SBOM formal. | H10 |
| V15.1.3 | L2 | Verify that the application documentation identifies functionality which is time-consuming or resource-demanding. This must include how to prevent a loss of … | No cumple | No se documenta que las llamadas a Open-Meteo son la operación costosa ni cómo protegerla. | H1, H10 |
| V15.2.1 | L1 | Verify that the application only contains components which have not breached the documented update and remediation time frames. | Parcial | `pip-audit` y `npm audit` sin vulnerabilidades, pero sin plazos documentados contra los que medir. | H10 |
| V15.2.2 | L2 | Verify that the application has implemented defenses against loss of availability due to functionality which is time-consuming or resource-demanding, based o… | No cumple | Sin single-flight ni límite de tasa; tampoco límite de tamaño de respuesta upstream. | H1, H8 |
| V15.2.3 | L2 | Verify that the production environment only includes functionality that is required for the application to function, and does not expose extraneous functiona… | Parcial | Producción expone la documentación interactiva de la API. | H2 |
| V15.3.1 | L1 | Verify that the application only returns the required subset of fields from a data object. For example, it should not return an entire data object, as some i… | Cumple | Cada endpoint usa `response_model` con solo los campos necesarios. |  |
| V15.3.2 | L2 | Verify that where the application backend makes calls to external URLs, it is configured to not follow redirects unless it is intended functionality. | Cumple | httpx no sigue redirecciones por defecto y no se activa `follow_redirects`. |  |
| V15.3.3 | L2 | Verify that the application has countermeasures to protect against mass assignment attacks by limiting allowed fields per controller and action, e.g., it is … | N/A | No hay escrituras ni enlace de cuerpo a modelos. |  |
| V15.3.4 | L2 | Verify that all proxying and middleware components transfer the user's original IP address correctly using trusted data fields that cannot be manipulated by … | N/A | La app no usa la IP del cliente. |  |
| V15.3.5 | L2 | Verify that the application explicitly ensures that variables are of the correct type and performs strict equality and comparator operations. This is to avoi… | Cumple | Tipos estrictos con Pydantic; conversiones explícitas en `openmeteo.py` (`_code`, `_dt`). |  |
| V15.3.6 | L2 | Verify that JavaScript code is written in a way that prevents prototype pollution, for example, by using Set() or Map() instead of object literals. | Cumple | Sin fusiones de objetos con claves externas (`Object.assign`, spread de respuestas: grep sin resultados). |  |
| V15.3.7 | L2 | Verify that the application has defenses against HTTP parameter pollution attacks, particularly if the application framework makes no distinction about the s… | N/A | La API no lee parámetros. |  |

## V16 Security Logging and Error Handling

| ID | Nivel | Requisito | Estado | Evidencia | Hallazgo |
|---|---|---|---|---|---|
| V16.1.1 | L2 | Verify that an inventory exists documenting the logging performed at each layer of the application's technology stack, what events are being logged, log form… | No cumple | No hay inventario de logs. | H10, H11 |
| V16.2.1 | L2 | Verify that each log entry includes necessary metadata (such as when, where, who, what) that would allow for a detailed investigation of the timeline when an… | No cumple | Con `uvicorn app.main:app` los logs de la app salen sin fecha, nivel ni origen (logging sin configurar). | H11 |
| V16.2.2 | L2 | Verify that time sources for all logging components are synchronized, and that timestamps in security event metadata use UTC or include an explicit time zone… | No cumple | Sin marca de tiempo en los logs de la app. | H11 |
| V16.2.3 | L2 | Verify that the application only stores or broadcasts logs to the files and services that are documented in the log inventory. | Parcial | Solo se escribe a stderr; no hay destino documentado. | H11 |
| V16.2.4 | L2 | Verify that logs can be read and correlated by the log processor that is in use, preferably by using a common logging format. | No cumple | Formato libre sin estructura. | H11 |
| V16.2.5 | L2 | Verify that when logging sensitive data, the application enforces logging based on the data's protection level. For example, it may not be allowed to log cer… | Cumple | No se registran datos sensibles; solo ruta y tipo de error. |  |
| V16.3.1 | L2 | Verify that all authentication operations are logged, including successful and unsuccessful attempts. Additional metadata, such as the type of authentication… | N/A | No hay autenticación. |  |
| V16.3.2 | L2 | Verify that failed authorization attempts are logged. For L3, this must include logging all authorization decisions, including logging when sensitive data is… | N/A | No hay autorización. |  |
| V16.3.3 | L2 | Verify that the application logs the security events that are defined in the documentation and also logs attempts to bypass the security controls, such as in… | Parcial | No hay eventos de seguridad definidos; 404/405 solo quedan en el access log de uvicorn. | H10 |
| V16.3.4 | L2 | Verify that the application logs unexpected errors and security control failures such as backend TLS failures. | Cumple | Fallos upstream (incluidos errores TLS/transporte) y errores inesperados se registran con detalle (`reports/live_errors.txt`). |  |
| V16.4.1 | L2 | Verify that all logging components appropriately encode data to prevent log injection. | Cumple | Las rutas registradas son las de endpoints ya resueltos (constantes); uvicorn codifica la ruta en el access log. |  |
| V16.4.2 | L2 | Verify that logs are protected from unauthorized access and cannot be modified. | Despliegue | Depende de dónde se guarde stderr en el despliegue. | H11 |
| V16.4.3 | L2 | Verify that logs are securely transmitted to a logically separate system for analysis, detection, alerting, and escalation. The aim is to ensure that if the … | Despliegue | No hay envío a un sistema separado. | H11 |
| V16.5.1 | L2 | Verify that a generic message is returned to the consumer when an unexpected or security-sensitive error occurs, ensuring no exposure of sensitive internal s… | Cumple | Prueba en vivo: 503 (upstream caído o JSON malformado) y 500 (excepción) devuelven solo el mensaje genérico; el detalle queda en el log (`reports/live_errors.txt`). |  |
| V16.5.2 | L2 | Verify that the application continues to operate securely when external resource access fails, for example, by using patterns such as circuit breakers or gra… | Cumple | Degradación controlada: datos en caché marcados `stale=true` si upstream falla; reintentos con backoff. |  |
| V16.5.3 | L2 | Verify that the application fails gracefully and securely, including when an exception occurs, preventing fail-open conditions such as processing a transacti… | Cumple | Ante error se responde 5xx; no hay estados que puedan quedar abiertos. |  |

## V17 WebRTC

**N/A** (7 requisitos): No usa WebRTC.
