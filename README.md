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
Fases 0 a 2 completadas (preparación, datos y API con alertas). Consulta `PLAN.md`.

## Backend
Desde la raíz del proyecto:
- Pruebas: `.\.venv\Scripts\python.exe -m pytest backend`
- Servidor: `cd backend` y `..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`
- Endpoints: `/api/clima`, `/api/pronostico`, `/api/aire`, `/api/alertas`
