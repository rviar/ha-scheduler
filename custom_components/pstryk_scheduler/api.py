"""API client for Pstryk Energy."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class PstrykApiClient:
    """Client to interact with Pstryk API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._session = session
        self._base_url = API_BASE_URL

    async def async_get_prices(self) -> dict[str, Any]:
        """Get hourly electricity prices from Pstryk API.

        Returns a dictionary with hourly prices for today and tomorrow.
        Example format:
        {
            "prices": [
                {"hour": "2024-01-01T00:00:00", "price": 0.15},
                {"hour": "2024-01-01T01:00:00", "price": 0.14},
                ...
            ]
        }
        """
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }

            url = f"{self._base_url}/prices"

            async with self._session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as response:
                response.raise_for_status()
                data = await response.json()

                _LOGGER.debug(f"Received price data: {data}")
                return data

        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error fetching prices from Pstryk API: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error fetching prices: {err}")
            raise

    async def async_get_current_price(self) -> float | None:
        """Get the current electricity price."""
        try:
            data = await self.async_get_prices()
            prices = data.get("prices", [])

            now = datetime.now()
            current_hour = now.replace(minute=0, second=0, microsecond=0)

            for price_entry in prices:
                hour_str = price_entry.get("hour")
                price = price_entry.get("price")

                try:
                    hour_dt = datetime.fromisoformat(hour_str.replace("Z", "+00:00"))
                    # Compare without timezone info
                    if hour_dt.replace(tzinfo=None) == current_hour:
                        return float(price)
                except (ValueError, AttributeError) as err:
                    _LOGGER.warning(f"Error parsing hour {hour_str}: {err}")
                    continue

            return None

        except Exception as err:
            _LOGGER.error(f"Error getting current price: {err}")
            return None

    def parse_prices(self, data: dict[str, Any]) -> dict[str, float]:
        """Parse API response into a dictionary of hour -> price."""
        prices_dict = {}

        prices = data.get("prices", [])
        for entry in prices:
            hour_str = entry.get("hour")
            price = entry.get("price")

            try:
                # Parse the hour string and use it as key
                hour_dt = datetime.fromisoformat(hour_str.replace("Z", "+00:00"))
                # Use ISO format as key
                key = hour_dt.strftime("%Y-%m-%dT%H:00:00")
                prices_dict[key] = float(price)
            except (ValueError, AttributeError) as err:
                _LOGGER.warning(f"Error parsing price entry {entry}: {err}")
                continue

        return prices_dict
