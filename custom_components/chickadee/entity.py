"""Base entity for Chickadee integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChickadeeCoordinator


class ChickadeeEntity(CoordinatorEntity[ChickadeeCoordinator]):
    """Base class for Chickadee entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ChickadeeCoordinator, device_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        data = self.coordinator.data or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=data.get("deviceName", "Chickadee"),
            manufacturer="Chickadee",
            model=data.get("deviceModel", "Tablet"),
            sw_version=data.get("appVersionName"),
            configuration_url=f"http://{self.coordinator.host}:{self.coordinator.port}",
        )
