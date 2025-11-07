"""Pstryk Energy Scheduler Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_API_KEY
from .api import PstrykApiClient
from .coordinator import PstrykDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Pstryk Energy Scheduler component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pstryk Energy Scheduler from a config entry."""
    api_key = entry.data.get(CONF_API_KEY)

    session = async_get_clientsession(hass)
    api_client = PstrykApiClient(api_key, session)

    # Create data update coordinator
    coordinator = PstrykDataUpdateCoordinator(
        hass,
        api_client,
        update_interval=timedelta(minutes=15),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant, coordinator: PstrykDataUpdateCoordinator) -> None:
    """Set up services for the Pstryk integration."""

    async def handle_set_schedule(call: ServiceCall) -> None:
        """Handle the set_schedule service call."""
        hour = call.data.get("hour")
        mode = call.data.get("mode")

        await coordinator.async_set_schedule(hour, mode)
        _LOGGER.info(f"Schedule set for hour {hour} with mode {mode}")

    async def handle_clear_schedule(call: ServiceCall) -> None:
        """Handle the clear_schedule service call."""
        hour = call.data.get("hour")

        await coordinator.async_clear_schedule(hour)
        _LOGGER.info(f"Schedule cleared for hour {hour}")

    # Register services
    hass.services.async_register(DOMAIN, "set_schedule", handle_set_schedule)
    hass.services.async_register(DOMAIN, "clear_schedule", handle_clear_schedule)
