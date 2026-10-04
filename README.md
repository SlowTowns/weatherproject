# Clima Monterrey

Página web del clima del municipio de Monterrey, Nuevo León, con estética pixel art inspirada en Blasphemous y Celeste, temas de color por estación y un oso como mascota.

## Funciones
- Clima actual: temperatura, sensación térmica, humedad, viento y lluvia.
- Línea del tiempo de 24 horas (temperatura y probabilidad de lluvia).
- Pronóstico de 7 días con rango de temperatura.
- Mapa de la ciudad con la temperatura actual.
- Calidad del aire (ICA de EE. UU.).
- Alertas de calor extremo, tormenta y frente frío.
- Tema por estación según la fecha real en Monterrey; el Cerro de la Silla al fondo.

## Stack
- **Backend:** Python, FastAPI, httpx, Pydantic (`backend/`).
- **Frontend:** Vite + React, Leaflet (`frontend/`).
- **Datos:** [Open-Meteo](https://open-meteo.com/) (clima y calidad del aire) y [OpenStreetMap](https://www.openstreetmap.org/copyright) (mapa). Ninguno requiere API key.

## Requisitos
- Python con el entorno virtual `.venv` en la raíz.
- Node.js y npm.

Instalación de dependencias (solo la primera vez):
```
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd frontend; npm install
```

## Desarrollo
Dos terminales:
1. Backend: `cd backend` y `..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload` (http://127.0.0.1:8000, documentación en `/docs`).
2. Frontend: `cd frontend` y `npm run dev` (http://localhost:5173). Vite reenvía `/api` al backend.

En desarrollo se puede previsualizar un tema con `?tema=primavera|verano|otono|invierno` o con los botones del pie de página.

## Producción
```
cd frontend; npm run build
cd ..\backend; ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
FastAPI sirve la API y el frontend compilado (`frontend/dist`) desde el mismo servidor, con cabeceras de seguridad (CSP, `nosniff`, `X-Frame-Options`). El tema depende solo de la fecha real.

## Verificación
- Pruebas del backend: `.\.venv\Scripts\python.exe -m pytest backend`
- Vulnerabilidades Python: `.\.venv\Scripts\python.exe -m pip_audit -r backend\requirements.txt`
- Frontend: `npm run lint`, `npm run build` y `npm audit` (desde `frontend/`)

## API
| Endpoint | Contenido |
|---|---|
| `/api/clima` | Condiciones actuales |
| `/api/pronostico` | 48 horas desde la hora actual y 7 días |
| `/api/aire` | Calidad del aire con categoría |
| `/api/alertas` | Alertas calculadas a partir del pronóstico |

Si la API externa falla, se devuelve el último dato válido marcado como `stale`. Si no hay datos, la respuesta es un 503 con un mensaje genérico; el detalle técnico queda solo en el log del servidor.

## Calidad de los datos
- Valores fuera de rango físico (p. ej. 999 °C) se descartan.
- Las alertas requieren que la condición se mantenga varias horas seguidas:
  - **Calor extremo:** sensación ≥ 40 °C durante ≥ 2 h (severidad alta desde 45 °C).
  - **Tormenta:** tormenta eléctrica, o lluvia ≥ 70 % con ráfagas ≥ 60 km/h, durante ≥ 2 h.
  - **Frente frío:** descenso ≥ 8 °C en menos de 12 h, sostenido ≥ 2 h.

## Atribución
Datos del clima: Open-Meteo (CC BY 4.0). Mapa: © colaboradores de OpenStreetMap.
