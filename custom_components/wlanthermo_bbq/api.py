"""API client for WLANThermo BBQ device."""

import aiohttp
import async_timeout

class WlanthermoBBQApi:
    def __init__(self, host, port=80, path_prefix="/"):
        self._host = host
        self._port = port
        self._path_prefix = path_prefix.rstrip("/")
        self._base_url = f"http://{host}:{port}{self._path_prefix}"
        self._session = None

    def set_session(self, session):
        self._session = session

    async def _get(self, endpoint):
        url = f"{self._base_url}{endpoint}"
        if self._session is None:
            raise RuntimeError("Session not set for WlanthermoBBQApi")
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as err:
            # Optionally log error
            return None

    async def get_data(self):
        return await self._get("/data")

    async def get_settings(self):
        return await self._get("/settings")

    async def get_info(self):
        return await self._get("/info")
