
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, CONF_PATH_PREFIX, CONF_MODEL
from .api import WlanthermoBBQApi

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
	host = entry.options.get("host", entry.data.get("host"))
	port = entry.options.get("port", entry.data.get("port", 80))
	path_prefix = entry.data.get("path_prefix", "/")
	scan_interval = entry.options.get("scan_interval", 10)
	model = entry.data.get("model", "select")

	session = aiohttp_client.async_get_clientsession(hass)
	api = WlanthermoBBQApi(host, port, path_prefix)
	api.set_session(session)

	hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
		"api": api,
		"scan_interval": scan_interval,
		"model": model,
	}

	# Forward setup to platforms (e.g., sensor)
	hass.async_create_task(
		hass.config_entries.async_forward_entry_setup(entry, "sensor")
	)
	return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
	await hass.config_entries.async_forward_entry_unload(entry, "sensor")
	hass.data[DOMAIN].pop(entry.entry_id)
	return True
