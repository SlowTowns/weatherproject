"""Motor de alertas. Reglas por umbral con persistencia mínima para evitar falsos positivos.

Una condición debe sostenerse en horas consecutivas del pronóstico; un solo dato aislado
no genera alerta. Las funciones son puras: reciben un Forecast y devuelven alertas.
"""

from datetime import timedelta

from app.schemas import Alert, Forecast, HourlyPoint

WINDOW_HOURS = 24

HEAT_THRESHOLD = 40.0  # sensación térmica °C
HEAT_HIGH = 45.0
HEAT_MIN_HOURS = 2

STORM_CODES = range(95, 100)  # tormenta eléctrica (WMO)
STORM_PROBABILITY = 70.0
STORM_GUSTS = 60.0  # km/h
STORM_MIN_HOURS = 2

COLD_DROP = 8.0  # °C
COLD_WINDOW_HOURS = 12
COLD_MIN_HOURS = 2


def _upcoming(forecast: Forecast) -> list[HourlyPoint]:
    """Horas del pronóstico desde la hora actual, hasta WINDOW_HOURS adelante."""
    start = forecast.current.time.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=WINDOW_HOURS)
    return [p for p in forecast.hourly if start <= p.time < end]


def _longest_run(flags: list[bool]) -> tuple[int, int]:
    """Devuelve (inicio, longitud) de la racha más larga de True."""
    best_start, best_len, run_start, run_len = 0, 0, 0, 0
    for i, flag in enumerate(flags):
        if flag:
            if run_len == 0:
                run_start = i
            run_len += 1
            if run_len > best_len:
                best_start, best_len = run_start, run_len
        else:
            run_len = 0
    return best_start, best_len


def _heat(points: list[HourlyPoint]) -> Alert | None:
    values = [p.apparent_temperature if p.apparent_temperature is not None else p.temperature for p in points]
    flags = [v is not None and v >= HEAT_THRESHOLD for v in values]
    start, length = _longest_run(flags)
    if length < HEAT_MIN_HOURS:
        return None
    peak = max(v for v in values[start : start + length] if v is not None)
    high = peak >= HEAT_HIGH
    return Alert(
        type="calor_extremo",
        severity="alta" if high else "moderada",
        title="Calor extremo",
        message=(
            f"Sensación térmica de hasta {peak:.0f} °C durante {length} horas. "
            "Hidrátate y evita la exposición prolongada al sol."
        ),
        starts_at=points[start].time,
        hours=length,
    )


def _storm(points: list[HourlyPoint]) -> Alert | None:
    flags = []
    for p in points:
        by_code = p.weather_code in STORM_CODES
        by_conditions = (
            p.precipitation_probability is not None
            and p.precipitation_probability >= STORM_PROBABILITY
            and p.wind_gusts is not None
            and p.wind_gusts >= STORM_GUSTS
        )
        flags.append(by_code or by_conditions)
    start, length = _longest_run(flags)
    if length < STORM_MIN_HOURS:
        return None
    window = points[start : start + length]
    thunder = any(p.weather_code in STORM_CODES for p in window)
    return Alert(
        type="tormenta",
        severity="alta" if thunder else "moderada",
        title="Tormenta",
        message=(
            f"Condiciones de tormenta durante {length} horas"
            + (" con actividad eléctrica." if thunder else " con lluvia y ráfagas fuertes.")
            + " Evita zonas inundables y no transites por arroyos."
        ),
        starts_at=window[0].time,
        hours=length,
    )


def _cold_front(points: list[HourlyPoint]) -> Alert | None:
    temps = [p.temperature for p in points]
    for i, base in enumerate(temps):
        if base is None:
            continue
        last = min(i + COLD_WINDOW_HOURS, len(temps) - 1)
        run_start, run_len = None, 0
        for j in range(i + 1, last + 1):
            t = temps[j]
            if t is not None and base - t >= COLD_DROP:
                run_start = j if run_len == 0 else run_start
                run_len += 1
                if run_len >= COLD_MIN_HOURS:
                    return Alert(
                        type="frente_frio",
                        severity="moderada",
                        title="Descenso brusco de temperatura",
                        message=(
                            f"La temperatura bajará al menos {COLD_DROP:.0f} °C "
                            f"(de {base:.0f} °C a {t:.0f} °C) en menos de {COLD_WINDOW_HOURS} horas. "
                            "Posible frente frío; abrígate."
                        ),
                        starts_at=points[run_start].time,
                        hours=run_len,
                    )
            else:
                run_len = 0
    return None


def evaluate_alerts(forecast: Forecast) -> list[Alert]:
    points = _upcoming(forecast)
    rules = (_heat, _storm, _cold_front)
    return [alert for rule in rules if (alert := rule(points)) is not None]
