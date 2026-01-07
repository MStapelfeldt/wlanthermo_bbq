
"""Text platform for WLANThermo BBQ adjustable channel name."""

from homeassistant.components.text import TextEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelNameText(coordinator, channel))
    async_add_entities(entities)


class WlanthermoChannelNameText(CoordinatorEntity, TextEntity):
    def __init__(self, coordinator, channel):
        super().__init__(coordinator)
        self._channel = channel
        self._attr_name = f"Channel {channel.number} Name"
        self._attr_unique_id = f"channel_{channel.number}_name"
        self._attr_icon = "mdi:rename-box"
        self._attr_max_length = 10

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def native_value(self):
        return self._channel.name

    async def async_set_value(self, value: str):
        # TODO: Implement API call to set channel name
        pass
