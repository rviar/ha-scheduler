# Pstryk Energy Scheduler

Intelligent energy management for Home Assistant based on hourly electricity prices from Pstryk API.

## Features

### Smart Price Monitoring
- Automatic price updates every 15 minutes
- Real-time current, next hour, and statistical price data
- Visual price trends with color-coded bars

### Interactive Scheduling
- Click any hour to set operating mode
- Beautiful interactive chart interface
- 7 different operating modes
- Persistent schedule storage

### Automated Control
- Execute scripts based on scheduled modes
- Automatic mode switching at hour boundaries
- Customizable actions for each mode

### Operating Modes

1. **Default** - Normal operation
2. **Buy** - Purchase energy from grid
3. **Sell** - Sell energy to grid
4. **Sell (All)** - Sell all available energy including battery
5. **Sell (PV Only)** - Sell only solar energy
6. **Buy (Charge car)** - Purchase energy and charge EV
7. **Buy (Charge car and charge battery)** - Purchase energy for both EV and home battery

## Quick Start

1. Install via HACS
2. Add integration with your Pstryk API key
3. Add custom card resource
4. Configure automations
5. Start scheduling!

## Sensors Created

- Current Price
- Next Hour Price
- Average Price
- Minimum Price
- Maximum Price
- Current Mode
- Price Data (all hours)
- Schedule Data

## Services

- `pstryk_scheduler.set_schedule` - Set mode for a specific hour
- `pstryk_scheduler.clear_schedule` - Clear scheduled mode

## Requirements

- Home Assistant 2023.1.0 or newer
- Valid Pstryk API key
- Internet connection for API access

## Support

For issues, questions, or feature requests, please visit:
[GitHub Repository](https://github.com/rviar/ha-scheduler)

---

**Note**: This is an unofficial integration and is not affiliated with Pstryk.
