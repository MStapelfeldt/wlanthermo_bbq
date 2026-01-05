
# WLANThermo BBQ – Home Assistant Custom Integration

![Version](https://img.shields.io/badge/version-0.0.1-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024%2B-blue)
![Support](https://img.shields.io/badge/support-No%20support%20provided-lightgrey)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

**Version:** 0.0.1  
**Code Owner:** @MStapelfeldt  
**License:** MIT

> **Attribution & Disclaimer**
> This is a community integration for WLANThermo BBQ.  
> **No support** is provided by the author. Forks, contributions, and bugfixes are welcome.  
> **No warranty/liability** — use at your own risk.

## Overview
This integration connects Home Assistant to a WLANThermo BBQ (ESP32/Nano/Next). It reads sensor and pitmaster data and exposes them as entities.

## Features
- Automatic discovery and setup via Home Assistant UI
- Temperature sensors for all channels (by name & number)
- Pitmaster sensors (e.g., duty cycle)
- System info: RSSI, battery status, charging
- Configurable scan intervals
- Support for multiple WLANThermo models
- Offline-tolerant startup (entities become available when the device is online)

## API Reference
- Official HTTP API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Use lowercase routes (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`)
- For pitmaster writes: send complete nested PM objects in an array

## Manual Installation
1. Extract this repository
2. Copy `custom_components/wlanthermo_bbq` into `<HA config>/custom_components/`
3. Restart Home Assistant

## Setup
1. Open Home Assistant
2. Go to Settings → Devices & Services → **Add Integration** → **WLANThermo BBQ**
3. Enter host, port, and (if needed) path prefix

## Entities (Examples)
- **Pitmaster**: duty cycle, channel, PID status, setpoint
- **Channels**: temperature, alarm, sensor type, min/max
- **System**: RSSI, battery status, charging

## Configuration
The integration uses a configuration dialog (config flow). No manual YAML entries are required.

## Development & Contributions
Pull requests, bug reports, and feature requests are welcome!
