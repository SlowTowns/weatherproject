"""Levanta la API en 127.0.0.1:8001 con un upstream SIMULADO que falla (sin red).

Uso: python run_failing_upstream.py {upstream503|malformed|unexpected}
  upstream503 -> Open-Meteo responde 503 (se espera 503 genérico)
  malformed   -> Open-Meteo responde JSON inválido/incompleto (se espera 503 genérico)
  unexpected  -> el servicio lanza una excepción no prevista (se espera 500 genérico)
"""

import logging
import sys

import httpx
import uvicorn

sys.path.insert(0, "/home/weatherproject/backend")
import app.main as main  # noqa: E402
from app.services.openmeteo import WeatherService  # noqa: E402

SECRET = "DETALLE-INTERNO-NO-DEBE-SALIR"


def upstream503(request):
    return httpx.Response(503, text=f"upstream caido {SECRET}")


def malformed(request):
    return httpx.Response(200, json={"current": {"temperature_2m": SECRET}})


class UnexpectedService:
    async def get_forecast(self):
        raise RuntimeError(f"fallo inesperado {SECRET} /etc/passwd")

    async def get_air_quality(self):
        raise RuntimeError(f"fallo inesperado {SECRET}")


scenario = sys.argv[1]
if scenario == "unexpected":
    main.WeatherService = UnexpectedService
else:
    handler = {"upstream503": upstream503, "malformed": malformed}[scenario]
    main.WeatherService = lambda: WeatherService(transport=httpx.MockTransport(handler), backoff=0.01)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
uvicorn.run(main.app, host="127.0.0.1", port=8001, log_level="info")
