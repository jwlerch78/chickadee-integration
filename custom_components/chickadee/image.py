# SPDX-License-Identifier: AGPL-3.0-only
"""Screenshot image entity for Chickadee integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import aiohttp

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_DEVICE_ID, API_GET_SCREENSHOT
from .coordinator import ChickadeeCoordinator
from .entity import ChickadeeEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chickadee screenshot image entity."""
    coordinator: ChickadeeCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_id = entry.data[CONF_DEVICE_ID]

    async_add_entities([ChickadeeScreenshot(coordinator, device_id)])


class ChickadeeScreenshot(ChickadeeEntity, ImageEntity):
    """Image entity that shows what's currently displayed on the Chickadee tablet."""

    _attr_translation_key = "screenshot"

    def __init__(self, coordinator: ChickadeeCoordinator, device_id: str) -> None:
        """Initialize the screenshot entity."""
        ChickadeeEntity.__init__(self, coordinator, device_id)
        ImageEntity.__init__(self, coordinator.hass)
        self._attr_unique_id = f"{device_id}_screenshot"
        self._attr_name = "Screenshot"
        self._cached_image: bytes | None = None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_image(self) -> bytes | None:
        """Return a screenshot from the device."""
        try:
            # Reuse HA's shared session (don't spin up a per-call session/connector).
            session = async_get_clientsession(self.coordinator.hass)
            url = f"{self.coordinator.base_url}/?cmd={API_GET_SCREENSHOT}"
            if self.coordinator.password:
                url += f"&password={self.coordinator.password}"

            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "image" in content_type:
                        self._cached_image = await response.read()
                        self._attr_image_last_updated = datetime.now()
                        return self._cached_image

                _LOGGER.debug("Screenshot request failed: status=%s", response.status)
                return self._cached_image
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.debug("Error getting screenshot: %s", err)
            return self._cached_image
