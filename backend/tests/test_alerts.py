from datetime import datetime, timedelta, timezone

from app.alerts import evaluate_alerts
from app.schemas import CurrentWeather, Forecast, HourlyPoint

START = datetime(2026, 7, 10, 12, 0)


def make_forecast(**series) -> Forecast:
    """series: listas por campo, una entrada por hora a partir de START."""
    n = max(len(v) for v in series.values())
    hourly = []
    for i in range(n):
        fields = {k: v[i] for k, v in series.items() if i < len(v)}
        hourly.append(HourlyPoint(time=START + timedelta(hours=i), **fields))
    return Forecast(
        fetched_at=datetime.now(timezone.utc),
        current=CurrentWeather(time=START, temperature=30.0),
        hourly=hourly,
        daily=[],
    )


def types(forecast):
    return [a.type for a in evaluate_alerts(forecast)]


def test_no_alerts_on_mild_weather():
    assert types(make_forecast(temperature=[28] * 24, apparent_temperature=[30] * 24)) == []


def test_single_hot_hour_is_not_an_alert():
    forecast = make_forecast(apparent_temperature=[38, 41, 38, 38])
    assert types(forecast) == []


def test_sustained_heat_triggers_alert():
    alerts = evaluate_alerts(make_forecast(apparent_temperature=[38, 41, 42, 39]))
    assert [a.type for a in alerts] == ["calor_extremo"]
    assert alerts[0].hours == 2
    assert alerts[0].severity == "moderada"
    assert alerts[0].starts_at == START + timedelta(hours=1)


def test_very_high_heat_is_high_severity():
    alerts = evaluate_alerts(make_forecast(apparent_temperature=[46, 47, 46]))
    assert alerts[0].severity == "alta"


def test_heat_falls_back_to_temperature_when_apparent_missing():
    assert types(make_forecast(temperature=[41, 41, 41])) == ["calor_extremo"]


def test_isolated_storm_code_is_not_an_alert():
    assert types(make_forecast(weather_code=[1, 95, 1, 1])) == []


def test_sustained_thunderstorm_is_high_severity():
    alerts = evaluate_alerts(make_forecast(weather_code=[1, 95, 96, 1]))
    assert [a.type for a in alerts] == ["tormenta"]
    assert alerts[0].severity == "alta"


def test_rain_with_strong_gusts_is_moderate_storm():
    forecast = make_forecast(
        precipitation_probability=[80, 80, 20],
        wind_gusts=[70, 65, 10],
    )
    alerts = evaluate_alerts(forecast)
    assert [a.type for a in alerts] == ["tormenta"]
    assert alerts[0].severity == "moderada"


def test_rain_without_gusts_is_not_a_storm():
    forecast = make_forecast(precipitation_probability=[90] * 4, wind_gusts=[20] * 4)
    assert types(forecast) == []


def test_sustained_temperature_drop_triggers_cold_front():
    temps = [30, 29, 27, 24, 21, 20, 20]
    assert types(make_forecast(temperature=temps)) == ["frente_frio"]


def test_brief_dip_is_not_a_cold_front():
    assert types(make_forecast(temperature=[30, 30, 20, 30, 30])) == []


def test_slow_drop_over_more_than_window_is_not_a_cold_front():
    temps = [30 - i for i in range(20)]  # -1 °C por hora, pero 8 °C tarda 8 h: sí es frente
    assert types(make_forecast(temperature=temps)) == ["frente_frio"]
    slow = [30 - (i // 2) for i in range(24)]  # -1 °C cada 2 h: 8 °C tarda 16 h
    assert types(make_forecast(temperature=slow)) == []


def test_missing_values_do_not_crash():
    assert types(make_forecast(temperature=[None, None, 30], weather_code=[None, 1, None])) == []


def test_hours_before_current_time_are_ignored():
    forecast = make_forecast(apparent_temperature=[45, 45, 45, 30, 30])
    forecast.current.time = START + timedelta(hours=3)
    assert types(forecast) == []
