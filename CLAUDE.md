# Proyecto: Página web del clima de Monterrey, Nuevo León

## Objetivo

Crear una página web enfocada en mostrar el clima del municipio de Monterrey, Nuevo León, México. La página debe ofrecer información meteorológica clara, actualizada y fácil de consultar para los habitantes y visitantes de la ciudad.

## Alcance

- Condiciones actuales: temperatura, sensación térmica, humedad, viento, presión y descripción del clima.
- Pronóstico por horas y de varios días (temperaturas máxima/mínima, probabilidad de lluvia).
- Alertas o avisos relevantes para la región (calor extremo, tormentas, frentes fríos, huracanes).
- Calidad del aire.
- Enfoque exclusivo en Monterrey (coordenadas aprox. 25.6866° N, 100.3161° W; zona horaria America/Monterrey).

## Lineamientos

- Idioma: español (México). Unidades: °C, km/h, mm.
- Diseño responsivo (móvil primero), limpio y accesible.
- Datos de Open-Meteo (clima y calidad del aire) y mapa de OpenStreetMap: gratuitos y sin API key. No usar servicios de paga.
- Estilo pixel art (Blasphemous / Celeste) con temas por estación; en producción el tema depende solo de la fecha real.
- Contraste de texto ≥ 4.5:1 en los cuatro temas.
- Antes de instalar librerías o dependencias, avisar al usuario. Revisar vulnerabilidades (`npm audit`, `pip-audit`).
- Manejar errores de red/API con mensajes claros al usuario encargado del backend, mostrar errores que no revelen información al usuario final.
- No exponer claves de API en el código del cliente si la API las requiere.

## Stack tecnológico

- Backend: Python + FastAPI + httpx + Pydantic (`backend/`), pruebas con pytest.
- Frontend: Vite + React + Leaflet (`frontend/`).
- En producción FastAPI sirve la API y `frontend/dist`.
- Repositorio: https://github.com/SlowTowns/weatherproject

## Estado

Fases 0 a 5 completadas (ver `PLAN.md` y `README.md`).
