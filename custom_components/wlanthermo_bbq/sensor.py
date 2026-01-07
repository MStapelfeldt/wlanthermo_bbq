"""Sensor platform for WLANThermo BBQ."""


from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.core import callback
from .const import DOMAIN
from datetime import timedelta
from .data import WlanthermoData
import logging

_LOGGER = logging.getLogger(__name__)


class WlanthermoSystemSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device_name):
        super().__init__(coordinator)
        self._device_name = device_name
        self._attr_name = f"{device_name} System"
        self._attr_unique_id = f"{device_name}_system"
        self.entity_id = f"sensor.{device_name}_system"

    @property
    def state(self):
        # Use time as the main state, or another relevant value
        return getattr(self.coordinator.data.system, 'time', None)

    @property
    def extra_state_attributes(self):
        sys = self.coordinator.data.system
        return {
            "time": getattr(sys, 'time', None),
            "unit": getattr(sys, 'unit', None),
            "soc": getattr(sys, 'soc', None),
            "charge": getattr(sys, 'charge', None),
            "rssi": getattr(sys, 'rssi', None),
            "online": getattr(sys, 'online', None),
        }


class BBQCoordinator(DataUpdateCoordinator):
    def __init__(self, *args, device_info=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_info = device_info


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_id = config_entry.entry_id
    api = hass.data[DOMAIN][entry_id]["api"]
    scan_interval = timedelta(seconds=hass.data[DOMAIN][entry_id]["scan_interval"])
    _LOGGER.debug(f"WLANThermo BBQ integration added. Data request URL: {api._base_url}/data")

    # Fetch device info for device registry
    device_name = config_entry.data.get("device_name", "WLANThermo BBQ")
    host = config_entry.data.get("host")
    port = config_entry.data.get("port", 80)
    path_prefix = config_entry.data.get("path_prefix", "/")
    # Try to fetch /settings for device info
    device_info = {}
    try:
        settings = await api.get_settings()
        if settings and "device" in settings:
            dev = settings["device"]
            device_info = {
                "identifiers": {(DOMAIN, dev.get("serial", host))},
                "name": device_name,
                "manufacturer": "WLANThermo",
                "model": dev.get("device", "unknown"),
                "sw_version": dev.get("sw_version", "unknown"),
            }
        else:
            device_info = {
                "identifiers": {(DOMAIN, host)},
                "name": device_name,
                "manufacturer": "WLANThermo",
                "model": config_entry.data.get("model", "unknown"),
                "sw_version": "unknown",
            }
    except Exception:
        device_info = {
            "identifiers": {(DOMAIN, host)},
            "name": device_name,
            "manufacturer": "WLANThermo",
            "model": config_entry.data.get("model", "unknown"),
            "sw_version": "unknown",
        }

    async def async_update_data():
        _LOGGER.debug(f"WLANThermo BBQ scan_interval data fetch. Request URL: {api._base_url}/data")
        raw = await api.get_data()
        if not raw:
            raise Exception("Failed to fetch /data from device")
        return WlanthermoData(raw)

    coordinator = BBQCoordinator(
        hass,
        _LOGGER,
        name="WLANThermo BBQ Data",
        update_method=async_update_data,
        update_interval=scan_interval,
        device_info=device_info,
    )
    await coordinator.async_refresh()

    # Store coordinator for other platforms (number, select, text)
    hass.data[DOMAIN][entry_id]["coordinator"] = coordinator

    entities = []
    num_channels = len(coordinator.data.channels)
    num_pitmasters = len(coordinator.data.pitmasters)
    _LOGGER.debug(f"WLANThermo BBQ: Found {num_channels} channels and {num_pitmasters} pitmasters.")
    # Sanitize device_name for entity_id
    import re
    safe_device_name = re.sub(r'[^a-zA-Z0-9_]', '_', device_name.lower())
    # Add system sensor if available
    if hasattr(coordinator.data, 'system') and coordinator.data.system:
        entities.append(WlanthermoSystemSensor(coordinator, safe_device_name))
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelSensor(coordinator, channel, safe_device_name))
    for idx, pitmaster in enumerate(coordinator.data.pitmasters, start=1):
        entities.append(WlanthermoPitmasterSensor(coordinator, pitmaster, safe_device_name, idx))
    if not entities:
        _LOGGER.warning(f"WLANThermo BBQ: No entities created. Check /data endpoint response. Requested URL: {api._base_url}/data")
    async_add_entities(entities)

class WlanthermoChannelSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, channel, device_name):
        super().__init__(coordinator)
        self._channel = channel
        self._device_name = device_name
        self._attr_name = f"{device_name} Channel {channel.number}: {channel.name}"
        self._attr_unique_id = f"{device_name}_channel_{channel.number}"
        self.entity_id = f"sensor.{device_name}_channel_{channel.number}"

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def state(self):
        return self._channel.temp

    @property
    def extra_state_attributes(self):
        return {
            "number": self._channel.number,
            "name": self._channel.name,
            "typ": self._channel.typ,
            "temp": self._channel.temp,
            "min": self._channel.min,
            "max": self._channel.max,
            "alarm": self._channel.alarm,
            "color": self._channel.color,
            "fixed": self._channel.fixed,
            "connected": self._channel.connected,
        }

class WlanthermoPitmasterSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, pitmaster, device_name, idx):
        super().__init__(coordinator)
        self._pitmaster = pitmaster
        self._device_name = device_name
        self._attr_name = f"{device_name} Pitmaster {idx}"
        self._attr_unique_id = f"{device_name}_pitmaster_{idx}"
        self.entity_id = f"sensor.{device_name}_pitmaster_{idx}"

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def state(self):
        return self._pitmaster.value

    @property
    def extra_state_attributes(self):
        return {
            "id": self._pitmaster.id,
            "channel": self._pitmaster.channel,
            "pid": self._pitmaster.pid,
            "value": self._pitmaster.value,
            "set": self._pitmaster.set,
            "typ": self._pitmaster.typ,
            "set_color": self._pitmaster.set_color,
            "value_color": self._pitmaster.value_color,
        }
