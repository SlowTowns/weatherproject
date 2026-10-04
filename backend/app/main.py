"""API del clima de Monterrey."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.alerts import evaluate_alerts
from app.schemas import (
    AirQuality,
    Alert,
    CurrentWeather,
    DailyPoint,
    DataUnavailable,
    HourlyPoint,
)
from app.services.openmeteo import WeatherService

log = logging.getLogger(__name__)

GENERIC_ERROR = "El servicio del clima no está disponible por el momento. Intenta de nuevo en unos minutos."
HOURLY_LIMIT = 48

# Frontend compilado (npm run build). Si existe, este mismo servidor lo sirve en producción.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    # OpenStreetMap pide el encabezado Referer para servir sus mosaicos.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "img-src 'self' data: https://tile.openstreetmap.org; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    ),
}


class CurrentResponse(BaseModel):
    fetched_at: datetime
    stale: bool
    current: CurrentWeather


class ForecastResponse(BaseModel):
    fetched_at: datetime
    stale: bool
    hourly: list[HourlyPoint]
    daily: list[DailyPoint]


class AlertsResponse(BaseModel):
    fetched_at: datetime
    stale: bool
    alerts: list[Alert]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = WeatherService()
    yield


app = FastAPI(title="Clima Monterrey", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


def get_service(request: Request) -> WeatherService:
    return request.app.state.service


@app.exception_handler(DataUnavailable)
async def data_unavailable_handler(request: Request, exc: DataUnavailable):
    log.error("Datos no disponibles en %s: %s", request.url.path, exc)
    return JSONResponse(status_code=503, content={"detail": GENERIC_ERROR})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    # El detalle queda en el log del servidor; el usuario final solo ve un mensaje genérico.
    log.exception("Error inesperado en %s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": GENERIC_ERROR})


@app.get("/api/clima", response_model=CurrentResponse)
async def clima(service: WeatherService = Depends(get_service)):
    forecast = await service.get_forecast()
    return CurrentResponse(fetched_at=forecast.fetched_at, stale=forecast.stale, current=forecast.current)


@app.get("/api/pronostico", response_model=ForecastResponse)
async def pronostico(service: WeatherService = Depends(get_service)):
    forecast = await service.get_forecast()
    start = forecast.current.time.replace(minute=0, second=0, microsecond=0)
    upcoming = [p for p in forecast.hourly if p.time >= start][:HOURLY_LIMIT]
    return ForecastResponse(
        fetched_at=forecast.fetched_at,
        stale=forecast.stale,
        hourly=upcoming,
        daily=forecast.daily,
    )


@app.get("/api/aire", response_model=AirQuality)
async def aire(service: WeatherService = Depends(get_service)):
    return await service.get_air_quality()


@app.get("/api/alertas", response_model=AlertsResponse)
async def alertas(service: WeatherService = Depends(get_service)):
    forecast = await service.get_forecast()
    return AlertsResponse(
        fetched_at=forecast.fetched_at,
        stale=forecast.stale,
        alerts=evaluate_alerts(forecast),
    )


# Se monta al final para que las rutas /api tengan prioridad.
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
