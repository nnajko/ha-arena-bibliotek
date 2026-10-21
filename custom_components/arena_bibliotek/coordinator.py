"""Data update coordinator: one login + overview fetch per refresh."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AccountData, ArenaAuthError, ArenaClient, ArenaError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ArenaCoordinator(DataUpdateCoordinator[AccountData]):
    """Fetches loans, reservations and fees."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: ArenaClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {entry.title}",
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = client

    async def _async_update_data(self) -> AccountData:
        try:
            return await self.client.fetch()
        except ArenaAuthError as err:
            raise ConfigEntryAuthFailed("Inloggningen nekades – kontrollera kortnummer och PIN") from err
        except ArenaError as err:
            raise UpdateFailed(str(err)) from err
