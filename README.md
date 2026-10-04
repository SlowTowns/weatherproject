# Clima Monterrey

Página web del clima del municipio de Monterrey, Nuevo León, con estética pixel art inspirada en Blasphemous y Celeste, y temas de color por estación.

## Stack
- Backend: Python, FastAPI, httpx, Pydantic
- Frontend: Vite + React
- Datos: Open-Meteo (sin API key)

## Estructura
- `backend/`: API en Python
- `frontend/`: aplicación web
- `PLAN.md`: plan por fases
- `CLAUDE.md`: objetivo y lineamientos del proyecto

## Estado
Fases 0 a 3 completadas (preparación, datos, API con alertas y base del frontend). Consulta `PLAN.md`.

## Frontend
Con el backend corriendo, desde `frontend/`: `npm run dev` y abrir http://localhost:5173.
Para forzar un tema: `?tema=verano`, `?tema=otono`, `?tema=invierno` o `?tema=primavera`.

## Backend
Desde la raíz del proyecto:
- Pruebas: `.\.venv\Scripts\python.exe -m pytest backend`
- Servidor: `cd backend` y `..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`
- Endpoints: `/api/clima`, `/api/pronostico`, `/api/aire`, `/api/alertas`
