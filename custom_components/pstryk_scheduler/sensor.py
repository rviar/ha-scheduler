"""Sensor platform for Pstryk Energy Scheduler."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_HOURLY_PRICES,
    ATTR_SCHEDULE,
    ATTR_CURRENT_PRICE,
    ATTR_NEXT_PRICE,
    ATTR_AVERAGE_PRICE,
    ATTR_MIN_PRICE,
    ATTR_MAX_PRICE,
)
from .coordinator import PstrykDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pstryk sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        PstrykCurrentPriceSensor(coordinator),
        PstrykNextPriceSensor(coordinator),
        PstrykAveragePriceSensor(coordinator),
        PstrykMinPriceSensor(coordinator),
        PstrykMaxPriceSensor(coordinator),
        PstrykCurrentModeSensor(coordinator),
        PstrykPriceDataSensor(coordinator),
        PstrykScheduleSensor(coordinator),
    ]

    async_add_entities(sensors)


class PstrykSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Pstryk sensors."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator, sensor_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "pstryk_energy_scheduler")},
            "name": "Pstryk Energy Scheduler",
            "manufacturer": "Pstryk",
            "model": "Energy Scheduler",
        }


class PstrykCurrentPriceSensor(PstrykSensorBase):
    """Sensor for current electricity price."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "current_price")
        self._attr_unique_id = f"{DOMAIN}_current_price"
        self._attr_name = "Current Price"
        self._attr_native_unit_of_measurement = "€/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_CURRENT_PRICE)


class PstrykNextPriceSensor(PstrykSensorBase):
    """Sensor for next hour electricity price."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "next_price")
        self._attr_unique_id = f"{DOMAIN}_next_price"
        self._attr_name = "Next Hour Price"
        self._attr_native_unit_of_measurement = "€/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_NEXT_PRICE)


class PstrykAveragePriceSensor(PstrykSensorBase):
    """Sensor for average electricity price."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "average_price")
        self._attr_unique_id = f"{DOMAIN}_average_price"
        self._attr_name = "Average Price"
        self._attr_native_unit_of_measurement = "€/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_AVERAGE_PRICE)


class PstrykMinPriceSensor(PstrykSensorBase):
    """Sensor for minimum electricity price."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "min_price")
        self._attr_unique_id = f"{DOMAIN}_min_price"
        self._attr_name = "Minimum Price"
        self._attr_native_unit_of_measurement = "€/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_MIN_PRICE)


class PstrykMaxPriceSensor(PstrykSensorBase):
    """Sensor for maximum electricity price."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "max_price")
        self._attr_unique_id = f"{DOMAIN}_max_price"
        self._attr_name = "Maximum Price"
        self._attr_native_unit_of_measurement = "€/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_MAX_PRICE)


class PstrykCurrentModeSensor(PstrykSensorBase):
    """Sensor for current operating mode."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "current_mode")
        self._attr_unique_id = f"{DOMAIN}_current_mode"
        self._attr_name = "Current Mode"
        self._attr_icon = "mdi:power-settings"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.data.get("current_mode", "Default")


class PstrykPriceDataSensor(PstrykSensorBase):
    """Sensor containing all hourly price data."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "price_data")
        self._attr_unique_id = f"{DOMAIN}_price_data"
        self._attr_name = "Price Data"
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return "Available"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        prices = self.coordinator.data.get("prices", {})
        return {
            ATTR_HOURLY_PRICES: prices,
            "last_update": self.coordinator.data.get("last_update"),
        }


class PstrykScheduleSensor(PstrykSensorBase):
    """Sensor containing schedule data."""

    def __init__(self, coordinator: PstrykDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "schedule")
        self._attr_unique_id = f"{DOMAIN}_schedule"
        self._attr_name = "Schedule"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        schedule = self.coordinator.data.get("schedule", {})
        return f"{len(schedule)} hours scheduled"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_SCHEDULE: self.coordinator.data.get("schedule", {}),
        }
