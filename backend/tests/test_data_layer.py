import asyncio

import httpx
import pytest

from app.cache import TTLCache
from app.schemas import DataUnavailable, clean
from app.services.openmeteo import WeatherService, parse_air_quality, parse_forecast

RAW_FORECAST = {
    "current": {
        "time": "2026-10-04T12:00",
        "temperature_2m": 31.5,
        "relative_humidity_2m": 45,
        "apparent_temperature": 33.0,
        "precipitation": 0.0,
        "weather_code": 1,
        "pressure_msl": 1012.3,
        "wind_speed_10m": 12.0,
        "wind_direction_10m": 90,
        "wind_gusts_10m": 25.0,
        "is_day": 1,
    },
    "hourly": {
        "time": ["2026-10-04T12:00", "2026-10-04T13:00"],
        "temperature_2m": [31.5, 999],
        "apparent_temperature": [33.0, 34.0],
        "precipitation_probability": [10, 20],
        "precipitation": [0.0, 0.0],
        "weather_code": [1, 2],
        "wind_gusts_10m": [25.0, 30.0],
    },
    "daily": {
        "time": ["2026-10-04"],
        "weather_code": [1],
        "temperature_2m_max": [34.0],
        "temperature_2m_min": [22.0],
        "precipitation_sum": [0.0],
        "precipitation_probability_max": [20],
        "uv_index_max": [8.1],
        "sunrise": ["2026-10-04T07:10"],
        "sunset": ["2026-10-04T18:55"],
    },
}

RAW_AIR = {"current": {"time": "2026-10-04T12:00", "us_aqi": 80, "pm2_5": 20.0, "pm10": 40.0}}


def service(handler, cache=None):
    return WeatherService(transport=httpx.MockTransport(handler), cache=cache, backoff=0)


def test_clean_discards_out_of_range_and_non_numeric():
    assert clean(30, "temperature") == 30.0
    assert clean(999, "temperature") is None
    assert clean(-50, "temperature") is None
    assert clean("30", "temperature") is None
    assert clean(True, "humidity") is None
    assert clean(None, "humidity") is None


def test_parse_forecast_discards_outliers():
    forecast = parse_forecast(RAW_FORECAST)
    assert forecast.current.temperature == 31.5
    assert forecast.current.is_day is True
    assert forecast.hourly[0].temperature == 31.5
    assert forecast.hourly[1].temperature is None  # 999 °C descartado
    assert forecast.daily[0].temperature_max == 34.0


def test_parse_forecast_rejects_invalid_current_temperature():
    raw = {**RAW_FORECAST, "current": {**RAW_FORECAST["current"], "temperature_2m": 200}}
    with pytest.raises(DataUnavailable):
        parse_forecast(raw)


def test_parse_forecast_rejects_malformed_response():
    with pytest.raises(DataUnavailable):
        parse_forecast({"nope": 1})


def test_parse_air_quality_requires_some_valid_value():
    assert parse_air_quality(RAW_AIR).us_aqi == 80
    with pytest.raises(DataUnavailable):
        parse_air_quality({"current": {"time": "2026-10-04T12:00", "us_aqi": 9999}})


def test_service_retries_then_succeeds():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, json=RAW_FORECAST)

    result = asyncio.run(service(handler).get_forecast())
    assert calls["n"] == 3
    assert result.stale is False


def test_service_uses_cache_within_ttl():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(200, json=RAW_FORECAST)

    svc = service(handler)

    async def run():
        await svc.get_forecast()
        await svc.get_forecast()

    asyncio.run(run())
    assert calls["n"] == 1


def test_service_falls_back_to_stale_data_when_api_fails():
    now = {"t": 0.0}
    cache = TTLCache(ttl_seconds=10, clock=lambda: now["t"])
    state = {"fail": False}

    def handler(request):
        if state["fail"]:
            return httpx.Response(500)
        return httpx.Response(200, json=RAW_FORECAST)

    svc = service(handler, cache)

    async def run():
        first = await svc.get_forecast()
        now["t"] = 100.0  # caché expirada
        state["fail"] = True
        return first, await svc.get_forecast()

    first, second = asyncio.run(run())
    assert first.stale is False
    assert second.stale is True
    assert second.current.temperature == 31.5


def test_service_raises_generic_error_without_cache():
    svc = service(lambda request: httpx.Response(500))
    with pytest.raises(DataUnavailable) as info:
        asyncio.run(svc.get_forecast())
    assert "500" not in str(info.value)


def test_service_does_not_retry_client_errors():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(400, json={"reason": "bad"})

    with pytest.raises(DataUnavailable):
        asyncio.run(service(handler).get_air_quality())
    assert calls["n"] == 1
