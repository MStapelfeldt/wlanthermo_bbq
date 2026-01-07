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



async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][entry_id]["coordinator"]
    device_name = config_entry.data.get("device_name", "WLANThermo BBQ")
    api = hass.data[DOMAIN][entry_id]["api"]
    _LOGGER.debug(f"WLANThermo BBQ integration added. Data request URL: {api._base_url}/data")

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
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

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
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

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
