"""Esquemas de datos y validación de rangos plausibles.

Un valor fuera de rango físico se descarta (None) en lugar de mostrarse al usuario.
"""

from datetime import datetime

from pydantic import BaseModel

# Rangos plausibles para Monterrey (con margen amplio).
RANGES = {
    "temperature": (-10.0, 55.0),
    "humidity": (0.0, 100.0),
    "pressure": (900.0, 1100.0),
    "wind": (0.0, 250.0),
    "wind_direction": (0.0, 360.0),
    "precipitation": (0.0, 500.0),
    "probability": (0.0, 100.0),
    "uv": (0.0, 16.0),
    "aqi": (0.0, 500.0),
    "concentration": (0.0, 2000.0),
}


def clean(value, kind: str) -> float | None:
    """Devuelve el valor si es numérico y está en rango; si no, None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    low, high = RANGES[kind]
    return float(value) if low <= value <= high else None


class DataUnavailable(Exception):
    """No hay datos válidos disponibles (ni frescos ni en caché)."""


class CurrentWeather(BaseModel):
    time: datetime
    temperature: float
    apparent_temperature: float | None = None
    humidity: float | None = None
    precipitation: float | None = None
    pressure: float | None = None
    wind_speed: float | None = None
    wind_gusts: float | None = None
    wind_direction: float | None = None
    weather_code: int | None = None
    is_day: bool | None = None


class HourlyPoint(BaseModel):
    time: datetime
    temperature: float | None = None
    apparent_temperature: float | None = None
    precipitation_probability: float | None = None
    precipitation: float | None = None
    wind_gusts: float | None = None
    weather_code: int | None = None


class DailyPoint(BaseModel):
    date: str
    weather_code: int | None = None
    temperature_max: float | None = None
    temperature_min: float | None = None
    precipitation_sum: float | None = None
    precipitation_probability_max: float | None = None
    uv_index_max: float | None = None
    sunrise: datetime | None = None
    sunset: datetime | None = None


class Forecast(BaseModel):
    fetched_at: datetime
    stale: bool = False
    current: CurrentWeather
    hourly: list[HourlyPoint]
    daily: list[DailyPoint]


class AirQuality(BaseModel):
    fetched_at: datetime
    stale: bool = False
    time: datetime
    us_aqi: float | None = None
    pm2_5: float | None = None
    pm10: float | None = None
    ozone: float | None = None
    nitrogen_dioxide: float | None = None
