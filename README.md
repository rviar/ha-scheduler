# Pstryk Energy Scheduler for Home Assistant

A custom Home Assistant integration that connects to the Pstryk API to retrieve hourly electricity prices and provides an interactive interface for scheduling energy management based on tariffs.

## Features

- **Automatic Data Updates**: Fetches electricity prices from Pstryk API every 15 minutes
- **Interactive Dashboard**: Beautiful chart visualization with hourly price display
- **Flexible Scheduling**: Click on any hour to set operating modes
- **Multiple Operating Modes**:
  - Default
  - Buy
  - Sell
  - Sell (All)
  - Sell (PV Only)
  - Buy (Charge car)
  - Buy (Charge car and charge battery)
- **Persistent Storage**: Schedule data is stored and persists across restarts
- **Automated Actions**: Automatically execute scripts based on scheduled modes
- **Real-time Statistics**: Current, next, average, min, and max price sensors

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/rviar/ha-scheduler`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Pstryk Energy Scheduler" in the integration list
9. Click "Install"
10. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pstryk_scheduler` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

### 1. Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Pstryk Energy Scheduler"**
4. Enter your Pstryk API key
5. Click **"Submit"**

### 2. Add Custom Card

The integration includes a custom Lovelace card for visualization.

#### Add Resource

1. Go to **Settings** → **Dashboards** → **Resources**
2. Click **"Add Resource"**
3. Enter URL: `/local/custom_components/pstryk_scheduler/www/pstryk-scheduler-card.js`
4. Select Resource type: **"JavaScript Module"**
5. Click **"Create"**

Alternatively, add to your `configuration.yaml`:

```yaml
lovelace:
  mode: yaml
  resources:
    - url: /local/custom_components/pstryk_scheduler/www/pstryk-scheduler-card.js
      type: module
```

### 3. Add Card to Dashboard

Add this to your Lovelace dashboard:

```yaml
type: custom:pstryk-scheduler-card
entity: sensor.pstryk_scheduler_price_data
schedule_entity: sensor.pstryk_scheduler_schedule
title: "Pstryk Energy Scheduler"
```

### 4. Set Up Automations

Add the example automations from `examples/automations.yaml` to your Home Assistant configuration. These automations will execute the appropriate scripts when each hour begins based on your schedule.

See the [examples/automations.yaml](examples/automations.yaml) file for complete automation examples.

## Usage

### Interactive Chart

1. The main card displays a bar chart with hourly electricity prices
2. Bars are color-coded:
   - **Green**: Low prices (below 80% of average)
   - **Yellow**: Medium prices (80-120% of average)
   - **Red**: High prices (above 120% of average)
3. **Blue border**: Hour has a scheduled mode
4. **Purple border**: Current hour

### Setting Modes

1. Click on any hour bar in the chart
2. A modal dialog will appear
3. Select the desired operating mode from the dropdown
4. Click **"Save"** to confirm
5. Click **"Clear Schedule"** to remove the mode
6. Click **"Cancel"** to close without changes

### Sensors

The integration provides the following sensors:

- `sensor.pstryk_scheduler_current_price` - Current hour electricity price
- `sensor.pstryk_scheduler_next_price` - Next hour electricity price
- `sensor.pstryk_scheduler_average_price` - Average price across all hours
- `sensor.pstryk_scheduler_min_price` - Minimum price
- `sensor.pstryk_scheduler_max_price` - Maximum price
- `sensor.pstryk_scheduler_current_mode` - Currently active operating mode
- `sensor.pstryk_scheduler_price_data` - All hourly prices (with attributes)
- `sensor.pstryk_scheduler_schedule` - Complete schedule (with attributes)

### Services

#### `pstryk_scheduler.set_schedule`

Set operating mode for a specific hour.

```yaml
service: pstryk_scheduler.set_schedule
data:
  hour: "2024-01-15T14:00:00"
  mode: "Buy"
```

#### `pstryk_scheduler.clear_schedule`

Clear operating mode for a specific hour.

```yaml
service: pstryk_scheduler.clear_schedule
data:
  hour: "2024-01-15T14:00:00"
```

## Customization

### Custom Scripts

Edit the scripts in your `automations.yaml` to define what happens in each mode:

```yaml
script:
  pstryk_mode_buy:
    alias: "Pstryk Mode: Buy"
    sequence:
      # Add your custom actions
      - service: switch.turn_on
        target:
          entity_id: switch.grid_import
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charging
```

### API Configuration

The integration uses the following Pstryk API endpoint:

- Base URL: `https://api.pstryk.com/v1`
- Endpoint: `/prices`

To get your API key, visit the [Pstryk website](https://pstryk.com) and register for an account.

## Troubleshooting

### Integration Not Loading

1. Check Home Assistant logs for errors
2. Verify your API key is correct
3. Ensure you have an active internet connection
4. Restart Home Assistant

### Custom Card Not Showing

1. Clear browser cache
2. Verify the resource is added correctly
3. Check browser console for JavaScript errors
4. Ensure the card configuration is correct

### Data Not Updating

1. Check the `sensor.pstryk_scheduler_price_data` sensor attributes
2. Verify API connectivity in Home Assistant logs
3. Check if your API key is still valid
4. The integration updates every 15 minutes

### Automations Not Working

1. Verify the automation is enabled
2. Check that scripts are defined correctly
3. Test scripts manually from Developer Tools
4. Review automation traces for errors

## Development

### Project Structure

```
custom_components/pstryk_scheduler/
├── __init__.py           # Integration setup and services
├── api.py               # Pstryk API client
├── config_flow.py       # Configuration flow (UI setup)
├── const.py             # Constants and configuration
├── coordinator.py       # Data update coordinator
├── manifest.json        # Integration manifest
├── sensor.py            # Sensor entities
├── services.yaml        # Service definitions
├── strings.json         # Translations
└── www/
    └── pstryk-scheduler-card.js  # Custom Lovelace card
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Integration created for Home Assistant
- Uses the Pstryk API for electricity price data
- Custom Lovelace card built with vanilla JavaScript

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/rviar/ha-scheduler/issues) page
2. Create a new issue with:
   - Home Assistant version
   - Integration version
   - Detailed description of the problem
   - Relevant logs

## Changelog

### Version 1.0.0

- Initial release
- Pstryk API integration
- Interactive price chart
- Mode scheduling
- Automated script execution
- 8 operating modes
- Persistent storage
- Real-time price sensors

---

**Disclaimer**: This is a third-party integration and is not officially affiliated with Pstryk or Home Assistant.
