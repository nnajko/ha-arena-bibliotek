"""Button: fetch loans now instead of waiting for the 6-hour update."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ArenaConfigEntry, async_renew
from .coordinator import ArenaCoordinator
from .sensor import device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ArenaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ArenaRefreshButton(entry.runtime_data, entry), ArenaRenewAllButton(entry.runtime_data, entry)])


class ArenaRefreshButton(CoordinatorEntity[ArenaCoordinator], ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: ArenaCoordinator, entry: ArenaConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_refresh"
        self._attr_device_info = device_info(entry)

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()


class ArenaRenewAllButton(CoordinatorEntity[ArenaCoordinator], ButtonEntity):
    """Renew every loan that can be renewed (result as event arena_bibliotek_renewed)."""

    _attr_has_entity_name = True
    _attr_translation_key = "renew_all"
    _attr_icon = "mdi:book-refresh"

    def __init__(self, coordinator: ArenaCoordinator, entry: ArenaConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_renew_all"
        self._attr_device_info = device_info(entry)

    async def async_press(self) -> None:
        await async_renew(self.hass, self._entry, lambda loan: True)
