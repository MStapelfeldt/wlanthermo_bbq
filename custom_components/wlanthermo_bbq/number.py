
"""Number platform for WLANThermo BBQ adjustable values."""

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

CHANNEL_NUMBER_FIELDS = [
    {
        "key": "min",
        "name": "Min Temperature",
        "icon": "mdi:thermometer-low",
        "min": -30.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
    {
        "key": "max",
        "name": "Max Temperature",
        "icon": "mdi:thermometer-high",
        "min": -30.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
]

PITMASTER_NUMBER_FIELDS = [
    {
        "key": "value",
        "name": "Pitmaster Value",
        "icon": "mdi:fan",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
    },
    {
        "key": "set",
        "name": "Set Temperature",
        "icon": "mdi:target",
        "min": 0.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    # Channel numbers
    for channel in coordinator.data.channels:
        for field in CHANNEL_NUMBER_FIELDS:
            entities.append(WlanthermoChannelNumber(coordinator, channel, field))
    # Pitmaster numbers
    for pitmaster in coordinator.data.pitmasters:
        for field in PITMASTER_NUMBER_FIELDS:
            entities.append(WlanthermoPitmasterNumber(coordinator, pitmaster, field))
    async_add_entities(entities)


class WlanthermoChannelNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, channel, field):
        super().__init__(coordinator)
        self._channel = channel
        self._field = field
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_{field['key']}"
        self.entity_id = f"number.{safe_device_name}_channel_{channel.number}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def native_value(self):
        return getattr(self._channel, self._field["key"], None)

    async def async_set_native_value(self, value):
        # TODO: Implement API call to set value
        pass


class WlanthermoPitmasterNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, pitmaster, field):
        super().__init__(coordinator)
        self._pitmaster = pitmaster
        self._field = field
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Pitmaster {pitmaster.id} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self.entity_id = f"number.{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def native_value(self):
        return getattr(self._pitmaster, self._field["key"], None)

    async def async_set_native_value(self, value):
        # TODO: Implement API call to set value
        pass
