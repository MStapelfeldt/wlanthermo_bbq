
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
    # Load translations for alarm modes
    import json
    import os
    import aiofiles
    lang = hass.config.language if hasattr(hass.config, 'language') else 'en'
    translations_path = os.path.join(os.path.dirname(__file__), 'translations', f'{lang}.json')
    if not os.path.exists(translations_path):
        translations_path = os.path.join(os.path.dirname(__file__), 'translations', 'en.json')
    async with aiofiles.open(translations_path, encoding='utf-8') as f:
        translations = json.loads(await f.read())
    alarm_labels_dict = translations.get("alarm", {})
    # Map alarm mode values to translated labels
    alarm_mode_map = {
        0: alarm_labels_dict.get("off", "Off"),
        1: alarm_labels_dict.get("push", "Push"),
        2: alarm_labels_dict.get("buzzer", "Buzzer"),
        3: alarm_labels_dict.get("push_buzzer", "Push + Buzzer"),
    }
    alarm_labels = [alarm_mode_map[i] for i in range(4)]

    # Get sensor types from settings (include all types)
    settings = getattr(hass.data[DOMAIN][config_entry.entry_id]["api"], 'settings', None)
    sensor_types = []
    if settings and hasattr(settings, 'sensors'):
        sensor_types = [s.name for s in settings.sensors]
    if not sensor_types:
        sensor_types = ["Typ 0", "Typ 1", "Typ 2"]
    # Channel selects
    for channel in coordinator.data.channels:
        # Alarm mode select
        entities.append(WlanthermoChannelSelect(coordinator, channel, {
            "key": "alarm",
            "name": "Alarm Mode",
            "icon": "mdi:alarm",
            "options": alarm_labels,
            "alarm_mode_map": alarm_mode_map,
        }))
        # Probe type select
        entities.append(WlanthermoChannelSelect(coordinator, channel, {
            "key": "typ",
            "name": "Probe Type",
            "icon": "mdi:thermometer",
            "options": sensor_types,
        }))
    # Get PID profiles from settings
    pid_profiles = []
    pid_profile_names = []
    if settings and hasattr(settings, 'pid'):
        pid_profiles = settings.pid
        pid_profile_names = [p.name for p in pid_profiles]
    if not pid_profile_names:
        pid_profile_names = ["Profile 0", "Profile 1", "Profile 2"]
    for pitmaster in coordinator.data.pitmasters:
        for field in PITMASTER_SELECT_FIELDS:
            if field["key"] == "pid":
                # Use profile names for PID select
                field = field.copy()
                field["options"] = pid_profile_names
                entities.append(WlanthermoPitmasterSelect(coordinator, pitmaster, field, pid_profiles=pid_profiles))
            else:
                entities.append(WlanthermoPitmasterSelect(coordinator, pitmaster, field))
    async_add_entities(entities)


class WlanthermoChannelSelect(CoordinatorEntity, SelectEntity):
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
        self.entity_id = f"select.{safe_device_name}_channel_{channel.number}_{field['key']}"
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
        # For alarm, return the translated label
        if self._field["key"] == "alarm":
            alarm_value = getattr(self._channel, "alarm", None)
            alarm_mode_map = self._field.get("alarm_mode_map")
            if alarm_mode_map and alarm_value in alarm_mode_map:
                return alarm_mode_map[alarm_value]
            return None
        # For probe type, return the name from options if possible
        if self._field["key"] == "typ":
            typ_value = getattr(self._channel, "typ", None)
            if self._attr_options and 0 <= typ_value < len(self._attr_options):
                return self._attr_options[typ_value]
            return None
        return getattr(self._channel, self._field["key"], None)

    async def async_select_option(self, option):
        # TODO: Implement API call to set value
        pass


class WlanthermoPitmasterSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, pitmaster, field, pid_profiles=None):
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
        self.entity_id = f"select.{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_options = field["options"]
        self._pid_profiles = pid_profiles if pid_profiles is not None else []

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def current_option(self):
        if self._field["key"] == "pid" and self._pid_profiles:
            # Find profile name by id
            pid_id = getattr(self._pitmaster, "pid", None)
            for p in self._pid_profiles:
                if hasattr(p, "id") and p.id == pid_id:
                    return p.name
            return None
        return getattr(self._pitmaster, self._field["key"], None)

    async def async_select_option(self, option):
        # TODO: Implement API call to set value
        if self._field["key"] == "pid" and self._pid_profiles:
            # Find profile id by name
            for p in self._pid_profiles:
                if hasattr(p, "name") and p.name == option:
                    # Set pitmaster.pid to p.id (API call needed)
                    # Example: await self.coordinator.api.set_pitmaster_pid(self._pitmaster.id, p.id)
                    return
        pass
