"""Data update coordinator for Pstryk Energy Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PstrykApiClient
from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION, MODE_DEFAULT

_LOGGER = logging.getLogger(__name__)


class PstrykDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Pstryk data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: PstrykApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api_client = api_client
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._schedule: dict[str, str] = {}
        self._prices: dict[str, float] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Fetch prices from API
            data = await self.api_client.async_get_prices()
            self._prices = self.api_client.parse_prices(data)

            # Load schedule from storage
            await self._async_load_schedule()

            # Get current hour schedule
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            current_hour_str = current_hour.strftime("%Y-%m-%dT%H:00:00")
            current_mode = self._schedule.get(current_hour_str, MODE_DEFAULT)

            # Calculate statistics
            price_values = list(self._prices.values())
            avg_price = sum(price_values) / len(price_values) if price_values else 0
            min_price = min(price_values) if price_values else 0
            max_price = max(price_values) if price_values else 0

            # Get current and next price
            current_price = self._prices.get(current_hour_str)
            next_hour_str = (current_hour + timedelta(hours=1)).strftime("%Y-%m-%dT%H:00:00")
            next_price = self._prices.get(next_hour_str)

            return {
                "prices": self._prices,
                "schedule": self._schedule,
                "current_mode": current_mode,
                "current_price": current_price,
                "next_price": next_price,
                "average_price": avg_price,
                "min_price": min_price,
                "max_price": max_price,
                "last_update": datetime.now().isoformat(),
            }

        except Exception as err:
            _LOGGER.error(f"Error updating data: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def async_set_schedule(self, hour: str, mode: str) -> None:
        """Set schedule for a specific hour."""
        self._schedule[hour] = mode
        await self._async_save_schedule()
        await self.async_request_refresh()

    async def async_clear_schedule(self, hour: str) -> None:
        """Clear schedule for a specific hour."""
        if hour in self._schedule:
            del self._schedule[hour]
            await self._async_save_schedule()
            await self.async_request_refresh()

    async def async_get_schedule(self) -> dict[str, str]:
        """Get the current schedule."""
        return self._schedule.copy()

    async def async_get_mode_for_hour(self, hour: str) -> str:
        """Get the mode for a specific hour."""
        return self._schedule.get(hour, MODE_DEFAULT)

    async def _async_load_schedule(self) -> None:
        """Load schedule from storage."""
        data = await self._store.async_load()
        if data:
            self._schedule = data.get("schedule", {})
            _LOGGER.debug(f"Loaded schedule: {self._schedule}")

    async def _async_save_schedule(self) -> None:
        """Save schedule to storage."""
        await self._store.async_save({"schedule": self._schedule})
        _LOGGER.debug(f"Saved schedule: {self._schedule}")
