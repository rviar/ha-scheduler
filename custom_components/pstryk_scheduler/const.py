"""Constants for the Pstryk Energy Scheduler integration."""

DOMAIN = "pstryk_scheduler"

# Configuration
CONF_API_KEY = "api_key"
CONF_REGION = "region"

# Defaults
DEFAULT_SCAN_INTERVAL = 15  # minutes

# API
API_BASE_URL = "https://api.pstryk.com/v1"
API_TIMEOUT = 30

# Modes
MODE_DEFAULT = "Default"
MODE_BUY = "Buy"
MODE_SELL = "Sell"
MODE_SELL_ALL = "Sell (All)"
MODE_SELL_PV_ONLY = "Sell (PV Only)"
MODE_BUY_CHARGE_CAR = "Buy (Charge car)"
MODE_BUY_CHARGE_CAR_AND_BATTERY = "Buy (Charge car and charge battery)"

MODES = [
    MODE_DEFAULT,
    MODE_BUY,
    MODE_SELL,
    MODE_SELL_ALL,
    MODE_SELL_PV_ONLY,
    MODE_BUY_CHARGE_CAR,
    MODE_BUY_CHARGE_CAR_AND_BATTERY,
]

# Attributes
ATTR_HOURLY_PRICES = "hourly_prices"
ATTR_SCHEDULE = "schedule"
ATTR_CURRENT_PRICE = "current_price"
ATTR_NEXT_PRICE = "next_price"
ATTR_AVERAGE_PRICE = "average_price"
ATTR_MIN_PRICE = "min_price"
ATTR_MAX_PRICE = "max_price"

# Services
SERVICE_SET_SCHEDULE = "set_schedule"
SERVICE_CLEAR_SCHEDULE = "clear_schedule"

# Storage
STORAGE_KEY = "pstryk_scheduler_storage"
STORAGE_VERSION = 1
