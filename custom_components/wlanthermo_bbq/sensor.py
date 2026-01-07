"""Sensor platform for WLANThermo BBQ."""


from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.core import callback
from .const import DOMAIN
from datetime import timedelta
from .data import WlanthermoData
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_id = config_entry.entry_id
    api = hass.data[DOMAIN][entry_id]["api"]
    scan_interval = timedelta(seconds=hass.data[DOMAIN][entry_id]["scan_interval"])
    # Debug log the request URL after adding integration
    _LOGGER.debug(f"WLANThermo BBQ integration added. Data request URL: {api._base_url}/data")

    async def async_update_data():
        # Debug log the request URL at each scan_interval
        _LOGGER.debug(f"WLANThermo BBQ scan_interval data fetch. Request URL: {api._base_url}/data")
        raw = await api.get_data()
        if not raw:
            raise Exception("Failed to fetch /data from device")
        return WlanthermoData(raw)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="WLANThermo BBQ Data",
        update_method=async_update_data,
        update_interval=scan_interval,
    )
    await coordinator.async_refresh()

    entities = []
    # Create sensor entities for each channel
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelSensor(coordinator, channel))
    # Create sensor entities for each pitmaster
    for pitmaster in coordinator.data.pitmasters:
        entities.append(WlanthermoPitmasterSensor(coordinator, pitmaster))

    async_add_entities(entities)

class WlanthermoChannelSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, channel):
        super().__init__(coordinator)
        self._channel = channel
        self._attr_name = f"Channel {channel.number}: {channel.name}"
        self._attr_unique_id = f"wlanthermo_channel_{channel.number}"

    @property
    def state(self):
        return self._channel.temp

    @property
    def extra_state_attributes(self):
        return {
            "min": self._channel.min,
            "max": self._channel.max,
            "alarm": self._channel.alarm,
            "color": self._channel.color,
            "fixed": self._channel.fixed,
            "connected": self._channel.connected,
        }

class WlanthermoPitmasterSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, pitmaster):
        super().__init__(coordinator)
        self._pitmaster = pitmaster
        self._attr_name = f"Pitmaster {pitmaster.id}"
        self._attr_unique_id = f"wlanthermo_pitmaster_{pitmaster.id}"

    @property
    def state(self):
        return self._pitmaster.value

    @property
    def extra_state_attributes(self):
        return {
            "channel": self._pitmaster.channel,
            "pid": self._pitmaster.pid,
            "set": self._pitmaster.set,
            "typ": self._pitmaster.typ,
            "set_color": self._pitmaster.set_color,
            "value_color": self._pitmaster.value_color,
        }
