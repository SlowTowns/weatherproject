"""Mide amplificacion hacia upstream con cache vacio (upstream SIMULADO, sin red)."""
import asyncio, sys
import httpx
sys.path.insert(0, "/home/weatherproject/backend")
from app.services.openmeteo import WeatherService

calls = 0
async def handler(request):
    global calls
    calls += 1
    await asyncio.sleep(0.2)
    return httpx.Response(503)  # fuerza reintentos para medir el peor caso

async def main(n=100):
    svc = WeatherService(transport=httpx.MockTransport(handler), backoff=0.01)
    res = await asyncio.gather(*[svc.get_forecast() for _ in range(n)], return_exceptions=True)
    print(f"{n} solicitudes concurrentes, cache vacio -> {calls} llamadas upstream "
          f"({calls/n:.1f} por solicitud); errores: {sum(isinstance(r, Exception) for r in res)}")
asyncio.run(main())
