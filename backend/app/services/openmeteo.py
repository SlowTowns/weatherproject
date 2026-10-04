"""Cliente de Open-Meteo (clima y calidad del aire) con reintentos, validación y caché."""

import asyncio
import logging
from datetime import datetime, timezone

import httpx

from app import config
from app.cache import TTLCache
from app.schemas import (
    AirQuality,
    CurrentWeather,
    DailyPoint,
    DataUnavailable,
    Forecast,
    HourlyPoint,
    clean,
)

log = logging.getLogger(__name__)

CURRENT_VARS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
    "weather_code,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,is_day"
)
HOURLY_VARS = (
    "temperature_2m,apparent_temperature,precipitation_probability,precipitation,"
    "weather_code,wind_gusts_10m"
)
DAILY_VARS = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
    "precipitation_probability_max,uv_index_max,sunrise,sunset"
)
AIR_VARS = "us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide"


def _code(value) -> int | None:
    """Código WMO válido (0-99) o None."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if 0 <= value <= 99 else None


def _dt(value) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _at(series: dict, key: str, i: int):
    values = series.get(key)
    return values[i] if isinstance(values, list) and i < len(values) else None


def parse_forecast(raw: dict, now: datetime | None = None) -> Forecast:
    """Convierte la respuesta cruda en un Forecast validado. Lanza DataUnavailable si no es usable."""
    try:
        cur = raw["current"]
        temperature = clean(cur.get("temperature_2m"), "temperature")
        current_time = _dt(cur.get("time"))
        if temperature is None or current_time is None:
            raise DataUnavailable("Temperatura o fecha actual inválida")

        current = CurrentWeather(
            time=current_time,
            temperature=temperature,
            apparent_temperature=clean(cur.get("apparent_temperature"), "temperature"),
            humidity=clean(cur.get("relative_humidity_2m"), "humidity"),
            precipitation=clean(cur.get("precipitation"), "precipitation"),
            pressure=clean(cur.get("pressure_msl"), "pressure"),
            wind_speed=clean(cur.get("wind_speed_10m"), "wind"),
            wind_gusts=clean(cur.get("wind_gusts_10m"), "wind"),
            wind_direction=clean(cur.get("wind_direction_10m"), "wind_direction"),
            weather_code=_code(cur.get("weather_code")),
            is_day=bool(cur["is_day"]) if cur.get("is_day") in (0, 1) else None,
        )

        hourly_raw = raw.get("hourly", {})
        hourly = []
        for i, t in enumerate(hourly_raw.get("time", [])):
            when = _dt(t)
            if when is None:
                continue
            hourly.append(
                HourlyPoint(
                    time=when,
                    temperature=clean(_at(hourly_raw, "temperature_2m", i), "temperature"),
                    apparent_temperature=clean(_at(hourly_raw, "apparent_temperature", i), "temperature"),
                    precipitation_probability=clean(
                        _at(hourly_raw, "precipitation_probability", i), "probability"
                    ),
                    precipitation=clean(_at(hourly_raw, "precipitation", i), "precipitation"),
                    wind_gusts=clean(_at(hourly_raw, "wind_gusts_10m", i), "wind"),
                    weather_code=_code(_at(hourly_raw, "weather_code", i)),
                )
            )

        daily_raw = raw.get("daily", {})
        daily = [
            DailyPoint(
                date=str(d),
                weather_code=_code(_at(daily_raw, "weather_code", i)),
                temperature_max=clean(_at(daily_raw, "temperature_2m_max", i), "temperature"),
                temperature_min=clean(_at(daily_raw, "temperature_2m_min", i), "temperature"),
                precipitation_sum=clean(_at(daily_raw, "precipitation_sum", i), "precipitation"),
                precipitation_probability_max=clean(
                    _at(daily_raw, "precipitation_probability_max", i), "probability"
                ),
                uv_index_max=clean(_at(daily_raw, "uv_index_max", i), "uv"),
                sunrise=_dt(_at(daily_raw, "sunrise", i)),
                sunset=_dt(_at(daily_raw, "sunset", i)),
            )
            for i, d in enumerate(daily_raw.get("time", []))
        ]
    except (KeyError, AttributeError, TypeError) as exc:
        raise DataUnavailable(f"Respuesta con formato inesperado: {exc!r}") from exc

    return Forecast(
        fetched_at=now or datetime.now(timezone.utc),
        current=current,
        hourly=hourly,
        daily=daily,
    )


def parse_air_quality(raw: dict, now: datetime | None = None) -> AirQuality:
    try:
        cur = raw["current"]
        when = _dt(cur.get("time"))
        if when is None:
            raise DataUnavailable("Fecha de calidad del aire inválida")
        air = AirQuality(
            fetched_at=now or datetime.now(timezone.utc),
            time=when,
            us_aqi=clean(cur.get("us_aqi"), "aqi"),
            pm2_5=clean(cur.get("pm2_5"), "concentration"),
            pm10=clean(cur.get("pm10"), "concentration"),
            ozone=clean(cur.get("ozone"), "concentration"),
            nitrogen_dioxide=clean(cur.get("nitrogen_dioxide"), "concentration"),
        )
    except (KeyError, AttributeError, TypeError) as exc:
        raise DataUnavailable(f"Respuesta con formato inesperado: {exc!r}") from exc

    if all(v is None for v in (air.us_aqi, air.pm2_5, air.pm10, air.ozone, air.nitrogen_dioxide)):
        raise DataUnavailable("Calidad del aire sin valores válidos")
    return air


class WeatherService:
    def __init__(
        self,
        transport: httpx.AsyncBaseTransport | None = None,
        cache: TTLCache | None = None,
        backoff: float = config.HTTP_BACKOFF_SECONDS,
    ):
        self._transport = transport
        self._cache = cache or TTLCache(config.CACHE_TTL_SECONDS)
        self._backoff = backoff

    async def _get_json(self, url: str, params: dict) -> dict:
        """GET con reintentos ante errores de red y respuestas 5xx."""
        last_exc: Exception | None = None
        async with httpx.AsyncClient(
            timeout=config.HTTP_TIMEOUT_SECONDS, transport=self._transport
        ) as client:
            for attempt in range(config.HTTP_RETRIES):
                try:
                    response = await client.get(url, params=params)
                    if response.status_code >= 500:
                        raise httpx.HTTPStatusError(
                            "Error del servidor", request=response.request, response=response
                        )
                    response.raise_for_status()
                    return response.json()
                except (httpx.TransportError, httpx.HTTPStatusError, ValueError) as exc:
                    last_exc = exc
                    retryable = not (
                        isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500
                    )
                    if not retryable:
                        break
                    if attempt < config.HTTP_RETRIES - 1:
                        await asyncio.sleep(self._backoff * 2**attempt)
        assert last_exc is not None
        raise last_exc

    async def _cached(self, key: str, fetch_and_parse):
        fresh = self._cache.get(key)
        if fresh is not None:
            return fresh
        try:
            value = await fetch_and_parse()
        except (httpx.HTTPError, ValueError, DataUnavailable) as exc:
            # El detalle va solo al log; el cliente final no debe verlo.
            log.error("Fallo al obtener %s: %r", key, exc)
            stale = self._cache.get_stale(key)
            if stale is None:
                raise DataUnavailable("Sin datos disponibles") from exc
            return stale.model_copy(update={"stale": True})
        self._cache.set(key, value)
        return value

    async def get_forecast(self) -> Forecast:
        async def fetch():
            raw = await self._get_json(
                config.FORECAST_URL,
                {
                    "latitude": config.LATITUDE,
                    "longitude": config.LONGITUDE,
                    "timezone": config.TIMEZONE,
                    "forecast_days": config.FORECAST_DAYS,
                    "wind_speed_unit": "kmh",
                    "temperature_unit": "celsius",
                    "precipitation_unit": "mm",
                    "current": CURRENT_VARS,
                    "hourly": HOURLY_VARS,
                    "daily": DAILY_VARS,
                },
            )
            return parse_forecast(raw)

        return await self._cached("forecast", fetch)

    async def get_air_quality(self) -> AirQuality:
        async def fetch():
            raw = await self._get_json(
                config.AIR_QUALITY_URL,
                {
                    "latitude": config.LATITUDE,
                    "longitude": config.LONGITUDE,
                    "timezone": config.TIMEZONE,
                    "current": AIR_VARS,
                },
            )
            return parse_air_quality(raw)

        return await self._cached("air_quality", fetch)
