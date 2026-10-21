"""Config flow: library address + card number (or personal ID number) + PIN."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import ArenaAuthError, ArenaClient, ArenaError
from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

PIN_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def _normalise_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


async def _validate(base_url: str, username: str, pin: str) -> dict[str, str]:
    """Return form errors ({} if the login works)."""
    try:
        await ArenaClient(base_url, username, pin).fetch()
    except ArenaAuthError:
        return {"base": "invalid_auth"}
    except ArenaError:
        return {"base": "cannot_connect"}
    return {}


class ArenaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle setup and re-authentication."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = _normalise_url(user_input[CONF_BASE_URL])
            username = user_input[CONF_USERNAME].strip()
            await self.async_set_unique_id(f"{urlparse(base_url).netloc}_{username}")
            self._abort_if_unique_id_configured()
            errors = await _validate(base_url, username, user_input[CONF_PASSWORD])
            if not errors:
                host = urlparse(base_url).netloc.removeprefix("bibliotek.")
                return self.async_create_entry(
                    title=f"Bibliotek {host.split('.')[0].capitalize()} (…{username[-4:]})",
                    data={CONF_BASE_URL: base_url, CONF_USERNAME: username, CONF_PASSWORD: user_input[CONF_PASSWORD]},
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): PIN_SELECTOR,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = await _validate(entry.data[CONF_BASE_URL], entry.data[CONF_USERNAME], user_input[CONF_PASSWORD])
            if not errors:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): PIN_SELECTOR}),
            errors=errors,
        )
