from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app, get_service
from app.schemas import AirQuality, CurrentWeather, DailyPoint, DataUnavailable, Forecast, HourlyPoint

START = datetime(2026, 7, 10, 12, 0)


def make_forecast(stale=False) -> Forecast:
    hourly = [
        HourlyPoint(time=START + timedelta(hours=i), temperature=30.0, apparent_temperature=42.0)
        for i in range(-2, 60)
    ]
    return Forecast(
        fetched_at=datetime.now(timezone.utc),
        stale=stale,
        current=CurrentWeather(time=START, temperature=31.0, humidity=40),
        hourly=hourly,
        daily=[DailyPoint(date="2026-07-10", temperature_max=35.0, temperature_min=24.0)],
    )


class FakeService:
    def __init__(self, forecast=None, air=None, error=None):
        self.forecast, self.air, self.error = forecast, air, error

    async def get_forecast(self):
        if self.error:
            raise self.error
        return self.forecast

    async def get_air_quality(self):
        if self.error:
            raise self.error
        return self.air


def client_with(service) -> TestClient:
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def teardown_function():
    app.dependency_overrides.clear()


def test_clima():
    response = client_with(FakeService(make_forecast())).get("/api/clima")
    assert response.status_code == 200
    body = response.json()
    assert body["current"]["temperature"] == 31.0
    assert body["stale"] is False


def test_pronostico_starts_at_current_hour_and_is_limited():
    body = client_with(FakeService(make_forecast())).get("/api/pronostico").json()
    assert body["hourly"][0]["time"] == START.isoformat()
    assert len(body["hourly"]) == 48
    assert body["daily"][0]["temperature_max"] == 35.0


def test_aire_includes_category():
    air = AirQuality(fetched_at=datetime.now(timezone.utc), time=START, us_aqi=80)
    body = client_with(FakeService(air=air)).get("/api/aire").json()
    assert body["category"] == "Moderada"


def test_alertas_detects_heat():
    body = client_with(FakeService(make_forecast())).get("/api/alertas").json()
    assert [a["type"] for a in body["alerts"]] == ["calor_extremo"]


def test_stale_flag_is_exposed():
    body = client_with(FakeService(make_forecast(stale=True))).get("/api/clima").json()
    assert body["stale"] is True


def test_data_unavailable_returns_generic_503():
    response = client_with(FakeService(error=DataUnavailable("httpx 500 interno"))).get("/api/clima")
    assert response.status_code == 503
    assert "interno" not in response.text
    assert "httpx" not in response.text


def test_security_headers_are_set():
    response = client_with(FakeService(make_forecast())).get("/api/clima")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "https://tile.openstreetmap.org" in csp


def test_unexpected_error_returns_generic_500_without_details():
    response = client_with(FakeService(error=RuntimeError("clave secreta xyz"))).get("/api/alertas")
    assert response.status_code == 500
    assert "xyz" not in response.text
    assert "detail" in response.json()
