# SPDX-License-Identifier: AGPL-3.0-only
"""Central Music Assistant token store for Chickadee.

Stores the MA JWT token centrally in HA so that multiple tablets
can share it without each needing to go through the MA login flow.

Storage: homeassistant.helpers.storage.Store -> .storage/chickadee.music_token
HTTP endpoints:
  GET  /api/chickadee/music/token  — retrieve stored token + MA URL
  POST /api/chickadee/music/token  — save token + MA URL (from first device to login)
"""
from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "chickadee.music_token"
STORAGE_VERSION = 1


class MusicTokenStore:
    """Stores the MA JWT token centrally."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict = {}

    async def async_load(self) -> None:
        data = await self._store.async_load()
        self._data = data or {}

    def get_token(self) -> dict:
        """Return {token, ma_url} or empty dict. Returns token even without ma_url."""
        token = self._data.get("token", "")
        if not token:
            return {}
        return {"token": token, "ma_url": self._data.get("ma_url", "")}

    async def async_save_token(self, token: str, ma_url: str) -> None:
        """Store the MA JWT token and URL."""
        self._data = {"token": token, "ma_url": ma_url}
        await self._store.async_save(self._data)
        _LOGGER.info("Saved MA token centrally (url=%s)", ma_url)


# ── HTTP Views ───────────────────────────────────────────────────


class ChickadeeMusicTokenView(HomeAssistantView):
    """Get or save the central MA token."""

    url = "/api/chickadee/music/token"
    name = "api:chickadee:music:token"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        hass = request.app["hass"]
        store: MusicTokenStore | None = hass.data.get("chickadee", {}).get("music_token_store")
        if store is None:
            return web.json_response({})
        return web.json_response(store.get_token())

    async def delete(self, request: web.Request) -> web.Response:
        hass = request.app["hass"]
        store: MusicTokenStore | None = hass.data.get("chickadee", {}).get("music_token_store")
        if store is None:
            return web.json_response({"error": "Store not initialized"}, status=500)
        store._data = {}
        await store._store.async_save({})
        _LOGGER.info("Cleared central MA token")
        return web.json_response({"cleared": True})

    async def post(self, request: web.Request) -> web.Response:
        hass = request.app["hass"]
        store: MusicTokenStore | None = hass.data.get("chickadee", {}).get("music_token_store")
        if store is None:
            return web.json_response({"error": "Store not initialized"}, status=500)
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        token = body.get("token", "")
        ma_url = body.get("ma_url", "")
        if not token or not ma_url:
            return web.json_response({"error": "token and ma_url required"}, status=400)

        await store.async_save_token(token, ma_url)
        return web.json_response({"saved": True})


def register_music_token_views(hass: HomeAssistant) -> None:
    """Register music token HTTP views."""
    hass.http.register_view(ChickadeeMusicTokenView())
    _LOGGER.info("Registered Chickadee music token views")
