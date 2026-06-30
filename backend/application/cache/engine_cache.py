import time

from backend.sdk.engine import Engine


class EngineCache:
    """In-memory cache for SDK Engine instances."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self._cache: dict[str, dict] = {}
        self.default_ttl = default_ttl_seconds

    def _generate_key(self, organization_id: str, version: str) -> str:
        return f"{organization_id}:{version}"

    def get(self, organization_id: str, version: str) -> Engine | None:
        key = self._generate_key(organization_id, version)
        entry = self._cache.get(key)

        if entry:
            # Check TTL
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            return entry["engine"]
        return None

    def set(self, organization_id: str, version: str, engine: Engine, ttl_seconds: int | None = None) -> None:
        key = self._generate_key(organization_id, version)
        expires_at = time.time() + (ttl_seconds or self.default_ttl)
        self._cache[key] = {"engine": engine, "expires_at": expires_at}

    def invalidate(self, organization_id: str, version: str | None = None) -> None:
        if version:
            key = self._generate_key(organization_id, version)
            self._cache.pop(key, None)
        else:
            # Invalidate all versions for this org
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{organization_id}:")]
            for k in keys_to_delete:
                del self._cache[k]
