
"""
Sensor platform for WLANThermo BBQ.
Provides system, channel, pitmaster, and temperature sensors.
"""

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.core import callback
from .const import DOMAIN
from datetime import timedelta
from .data import WlanthermoData
import logging


_LOGGER = logging.getLogger(__name__)

class WlanthermoChannelTemperatureSensor(CoordinatorEntity, Entity):
    """
    Temperature sensor for a WLANThermo channel.
    Entity ID: sensor.{devicename}_channel_{number}_temperatur
    """
    def __init__(self, coordinator, channel, field=None):
        super().__init__(coordinator)
        self._channel = channel
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} Temperatur"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_temperatur"
        self.entity_id = f"sensor.{safe_device_name}_channel_{channel.number}_temperatur"

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """Return the current temperature value."""
        return self._channel.temp

    @property
    def extra_state_attributes(self):
        """Return extra attributes for the temperature sensor."""
        return {
            "number": self._channel.number,
            "name": self._channel.name,
            "typ": self._channel.typ,
            "min": self._channel.min,
            "max": self._channel.max,
            "alarm": self._channel.alarm,
            "color": self._channel.color,
            "fixed": self._channel.fixed,
            "connected": self._channel.connected,
        }

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
    # Defensive: Only proceed if coordinator.data is not None
    if coordinator.data is None:
        _LOGGER.warning("WLANThermo BBQ: coordinator.data is None. Entities will be unavailable until data is fetched.")
        # Continue setup so HA can retry and entities can recover
    num_channels = len(coordinator.data.channels)
    num_pitmasters = len(coordinator.data.pitmasters)
    _LOGGER.debug(f"WLANThermo BBQ: Found {num_channels} channels and {num_pitmasters} pitmasters.")
    # Sanitize device_name for entity_id
    import re
    safe_device_name = re.sub(r'[^a-zA-Z0-9_]', '_', device_name.lower())
    # Add temperature sensors for each channel
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelTemperatureSensor(coordinator, channel))
    # Add system sensors if available
    if hasattr(coordinator.data, 'system') and coordinator.data.system:
        entities.append(WlanthermoSystemSensor(coordinator, safe_device_name))
        sys = coordinator.data.system
        entities.append(WlanthermoSystemTimeSensor(coordinator, sys, safe_device_name))
        entities.append(WlanthermoSystemUnitSensor(coordinator, sys, safe_device_name))
        entities.append(WlanthermoSystemSocSensor(coordinator, sys, safe_device_name))
        entities.append(WlanthermoSystemChargeSensor(coordinator, sys, safe_device_name))
        entities.append(WlanthermoSystemRssiSensor(coordinator, sys, safe_device_name))
        entities.append(WlanthermoSystemOnlineSensor(coordinator, sys, safe_device_name))

    # Add device info sensors from /settings
    settings = getattr(hass.data[DOMAIN][entry_id]["api"], "settings", None)
    if settings:
        if hasattr(settings, "device"):
            entities.append(WlanthermoDeviceInfoSensor(settings.device, safe_device_name))
        if hasattr(settings, "system"):
            entities.append(WlanthermoSystemInfoSensor(settings.system, safe_device_name))
        if hasattr(settings, "iot"):
            entities.append(WlanthermoIotInfoSensor(settings.iot, safe_device_name))

    # Add all entities to Home Assistant
    async_add_entities(entities)

# Individual /data system sensors
class WlanthermoSystemTimeSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System Time"
        self._attr_unique_id = f"{device_name}_system_time"
        self.entity_id = f"sensor.{device_name}_system_time"
    @property
    def state(self):
        return getattr(self._sys, 'time', None)

class WlanthermoSystemUnitSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System Unit"
        self._attr_unique_id = f"{device_name}_system_unit"
        self.entity_id = f"sensor.{device_name}_system_unit"
    @property
    def state(self):
        return getattr(self._sys, 'unit', None)

class WlanthermoSystemSocSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System SOC"
        self._attr_unique_id = f"{device_name}_system_soc"
        self.entity_id = f"sensor.{device_name}_system_soc"
    @property
    def state(self):
        return getattr(self._sys, 'soc', None)

class WlanthermoSystemChargeSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System Charge"
        self._attr_unique_id = f"{device_name}_system_charge"
        self.entity_id = f"sensor.{device_name}_system_charge"
    @property
    def state(self):
        return getattr(self._sys, 'charge', None)

class WlanthermoSystemRssiSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System RSSI"
        self._attr_unique_id = f"{device_name}_system_rssi"
        self.entity_id = f"sensor.{device_name}_system_rssi"
    @property
    def state(self):
        return getattr(self._sys, 'rssi', None)

class WlanthermoSystemOnlineSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_name = f"{device_name} System Online"
        self._attr_unique_id = f"{device_name}_system_online"
        self.entity_id = f"sensor.{device_name}_system_online"
    @property
    def state(self):
        return getattr(self._sys, 'online', None)

# Device Info Sensor
class WlanthermoDeviceInfoSensor(Entity):
    def __init__(self, device, device_name):
        self._device = device
        self._attr_name = f"{device_name} Device Info"
        self._attr_unique_id = f"{device_name}_device_info"
        self.entity_id = f"sensor.{device_name}_device_info"

    @property
    def state(self):
        return getattr(self._device, "device", None)

    @property
    def extra_state_attributes(self):
        return {
            "serial": getattr(self._device, "serial", None),
            "cpu": getattr(self._device, "cpu", None),
            "flash_size": getattr(self._device, "flash_size", None),
            "hw_version": getattr(self._device, "hw_version", None),
            "sw_version": getattr(self._device, "sw_version", None),
            "api_version": getattr(self._device, "api_version", None),
            "language": getattr(self._device, "language", None),
        }

# System Info Sensor
class WlanthermoSystemInfoSensor(Entity):
    def __init__(self, system, device_name):
        self._system = system
        self._attr_name = f"{device_name} System Info"
        self._attr_unique_id = f"{device_name}_system_info"
        self.entity_id = f"sensor.{device_name}_system_info"

    @property
    def state(self):
        return getattr(self._system, "unit", None)

    @property
    def extra_state_attributes(self):
        return {
            "ap": getattr(self._system, "ap", None),
            "host": getattr(self._system, "host", None),
            "language": getattr(self._system, "language", None),
            "getupdate": getattr(self._system, "getupdate", None),
            "autoupd": getattr(self._system, "autoupd", None),
        }

# IOT Info Sensor (Cloud URL)
class WlanthermoIotInfoSensor(Entity):
    def __init__(self, iot, device_name):
        self._iot = iot
        self._attr_name = f"{device_name} Cloud URL"
        self._attr_unique_id = f"{device_name}_cloud_url"
        self.entity_id = f"sensor.{device_name}_cloud_url"

    @property
    def state(self):
        return getattr(self._iot, "CLurl", None)

    @property
    def extra_state_attributes(self):
        return {
            "cloud_url": getattr(self._iot, "CLurl", None),
        }

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
