"""Configuración del backend. Monterrey, Nuevo León."""

LATITUDE = 25.6866
LONGITUDE = -100.3161
TIMEZONE = "America/Monterrey"

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CACHE_TTL_SECONDS = 600
HTTP_TIMEOUT_SECONDS = 10.0
HTTP_RETRIES = 3
HTTP_BACKOFF_SECONDS = 0.5
FORECAST_DAYS = 7
