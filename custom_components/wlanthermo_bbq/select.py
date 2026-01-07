
"""Select platform for WLANThermo BBQ adjustable values."""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

CHANNEL_SELECT_FIELDS = [
    {
        "key": "typ",
        "name": "Probe Type",
        "icon": "mdi:thermometer",
        # TODO: Populate options from device/settings
        "options": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    },
    {
        "key": "alarm",
        "name": "Alarm Mode",
        "icon": "mdi:alarm",
        "options": [0, 1, 2, 3],
    },
]

PITMASTER_SELECT_FIELDS = [
    {
        "key": "typ",
        "name": "Pitmaster State",
        "icon": "mdi:state-machine",
        "options": ["off", "manual", "auto"],
    },
    {
        "key": "pid",
        "name": "PID Profile",
        "icon": "mdi:chart-bell-curve",
        # TODO: Populate options from device/settings
        "options": [0, 1, 2, 3, 4, 5],
    },
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    # Channel selects
    for channel in coordinator.data.channels:
        for field in CHANNEL_SELECT_FIELDS:
            entities.append(WlanthermoChannelSelect(coordinator, channel, field))
    # Pitmaster selects
    for pitmaster in coordinator.data.pitmasters:
        for field in PITMASTER_SELECT_FIELDS:
            entities.append(WlanthermoPitmasterSelect(coordinator, pitmaster, field))
    async_add_entities(entities)


class WlanthermoChannelSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, channel, field):
        super().__init__(coordinator)
        self._channel = channel
        self._field = field
        self._attr_name = f"Channel {channel.number} {field['name']}"
        self._attr_unique_id = f"channel_{channel.number}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_options = field["options"]

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def current_option(self):
        return getattr(self._channel, self._field["key"], None)

    async def async_select_option(self, option):
        # TODO: Implement API call to set value
        pass


class WlanthermoPitmasterSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, pitmaster, field):
        super().__init__(coordinator)
        self._pitmaster = pitmaster
        self._field = field
        self._attr_name = f"Pitmaster {pitmaster.id} {field['name']}"
        self._attr_unique_id = f"pitmaster_{pitmaster.id}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_options = field["options"]

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def current_option(self):
        return getattr(self._pitmaster, self._field["key"], None)

    async def async_select_option(self, option):
        # TODO: Implement API call to set value
        pass
