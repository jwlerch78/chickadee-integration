# SPDX-License-Identifier: AGPL-3.0-only
"""Device name endpoint for Chickadee.

Returns HA device registry names for all Chickadee devices so Android tablets
can look up their friendly name (e.g., "Mio 15\" Chickadee") instead of using
Build.MODEL (e.g., "rk3576_u").

HTTP endpoint:
  GET /api/chickadee/device/names — list all Chickadee devices with name + model
  GET /api/chickadee/device/area?device_id=<StableDeviceId> — the device's HA area name (room awareness)
"""
from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, device_registry as dr

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ChickadeeDeviceNamesView(HomeAssistantView):
    """Return friendly names for all Chickadee devices from the HA device registry."""

    url = "/api/chickadee/device/names"
    name = "api:chickadee:device:names"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        device_registry = dr.async_get(hass)

        devices = []
        for device in device_registry.devices.values():
            chickadee_ids = [
                id_tuple[1] for id_tuple in device.identifiers
                if id_tuple[0] == DOMAIN
            ]
            if not chickadee_ids:
                continue
            devices.append({
                "device_id": device.id,
                "name": device.name_by_user or device.name or "",
                "model": device.model or "",
                "android_id": chickadee_ids[0],
            })

        return web.json_response({"devices": devices})


def register_device_name_views(hass: HomeAssistant) -> None:
    """Register device name HTTP views."""
    hass.http.register_view(ChickadeeDeviceNamesView())
    hass.http.register_view(ChickadeeDeviceAreaView())
    _LOGGER.info("Registered Chickadee device name views")


class ChickadeeDeviceAreaView(HomeAssistantView):
    """Return the HA area NAME of a Chickadee device (room awareness, 20260715).

    The tablet is registered as an HA device identified by (DOMAIN, StableDeviceId); its area is
    assigned in HA. The voice brain uses this as device_area so "turn off the lights" resolves to
    the tablet's room. Keyed by the SAME StableDeviceId the tablet sends as endpoint_id.
    """

    url = "/api/chickadee/device/area"
    name = "api:chickadee:device:area"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        device_id = request.query.get("device_id", "").strip()
        if not device_id:
            return web.json_response({"error": "device_id required"}, status=400)

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
        if device is None:
            # Unknown device (not yet registered) → no area. Not an error; the brain falls back to
            # "ask which room" when device_area is absent.
            return web.json_response({"device_id": device_id, "area": None})

        area = None
        if device.area_id:
            area_entry = ar.async_get(hass).async_get_area(device.area_id)
            area = area_entry.name if area_entry is not None else None
        return web.json_response({"device_id": device_id, "area": area})
