"""Constants for the Axiell Arena library integration."""

from datetime import timedelta

DOMAIN = "arena_bibliotek"

CONF_BASE_URL = "base_url"
DEFAULT_BASE_URL = "https://bibliotek.varberg.se"

UPDATE_INTERVAL = timedelta(hours=6)
