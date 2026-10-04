"""Caché en memoria con TTL y acceso al último dato válido (aunque haya expirado)."""

import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: float, clock=time.monotonic):
        self._ttl = ttl_seconds
        self._clock = clock
        self._items: dict[str, tuple[float, Any]] = {}

    def set(self, key: str, value: Any) -> None:
        self._items[key] = (self._clock(), value)

    def get(self, key: str) -> Any | None:
        """Devuelve el valor solo si sigue vigente."""
        entry = self._items.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if self._clock() - stored_at > self._ttl:
            return None
        return value

    def get_stale(self, key: str) -> Any | None:
        """Devuelve el último valor guardado, aunque haya expirado."""
        entry = self._items.get(key)
        return entry[1] if entry else None
