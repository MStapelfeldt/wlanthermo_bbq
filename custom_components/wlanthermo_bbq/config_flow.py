"""Config flow for WLANThermo BBQ integration."""

from homeassistant import config_entries
from .const import DOMAIN


import voluptuous as vol
from homeassistant.const import CONF_HOST, CONF_PORT

CONF_PATH_PREFIX = "path_prefix"
CONF_MODEL = "model"



import aiohttp
from .api import WlanthermoBBQApi
from .data import SettingsData

class WlanthermoBBQConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    class WlanthermoBBQOptionsFlow(config_entries.OptionsFlow):
        def __init__(self, config_entry):
            self.config_entry = config_entry

        async def async_step_init(self, user_input=None):
            errors = {}
            if user_input is not None:
                # All fields required
                if not user_input.get(CONF_HOST):
                    errors[CONF_HOST] = "required"
                if not user_input.get(CONF_PORT):
                    errors[CONF_PORT] = "required"
                if not user_input.get("scan_interval"):
                    errors["scan_interval"] = "required"
                if not errors:
                    return self.async_create_entry(title="Options", data=user_input)

            data_schema = vol.Schema({
                vol.Required(CONF_HOST, default=self.config_entry.data.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=self.config_entry.data.get(CONF_PORT, 80)): int,
                vol.Required("scan_interval", default=10): int,
            })

            return self.async_show_form(
                step_id="init",
                data_schema=data_schema,
                errors=errors,
            )
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # All fields are required
            if not user_input.get(CONF_HOST):
                errors[CONF_HOST] = "required"
            if not user_input.get(CONF_PORT):
                errors[CONF_PORT] = "required"
            if not user_input.get(CONF_PATH_PREFIX):
                errors[CONF_PATH_PREFIX] = "required"
            if not user_input.get(CONF_MODEL):
                errors[CONF_MODEL] = "required"
            if not errors:
                # Save user_input temporarily in context
                self.context["user_input"] = user_input
                return await self.async_step_device_info()

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=80): int,
            vol.Required(CONF_PATH_PREFIX, default="/"): str,
            vol.Required(CONF_MODEL, default="select"): vol.In([m[0] for m in MODELS]),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=None,
        )

    async def async_step_device_info(self, user_input=None):
        # Get user_input from context
        user_input = self.context.get("user_input")
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        path_prefix = user_input[CONF_PATH_PREFIX]
        # Fetch /settings
        async with aiohttp.ClientSession() as session:
            api = WlanthermoBBQApi(host, port, path_prefix)
            api.set_session(session)
            settings_json = await api.get_settings()
        if not settings_json:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST, default=host): str,
                    vol.Required(CONF_PORT, default=port): int,
                    vol.Required(CONF_PATH_PREFIX, default=path_prefix): str,
                    vol.Required(CONF_MODEL, default=user_input[CONF_MODEL]): vol.In([m[0] for m in MODELS]),
                }),
                errors={"base": "cannot_connect"},
            )
        settings = SettingsData.from_json(settings_json)
        device = settings.device
        # Show info to user before creating entry
        description = (
            f"Geräte-Info:\n"
            f"Gerät: {device.device}\n"
            f"Seriennummer: {device.serial}\n"
            f"CPU: {device.cpu}\n"
            f"HW-Version: {device.hw_version}\n"
            f"SW-Version: {device.sw_version}"
        )
        if user_input is not None and user_input.get("confirm"):
            return self.async_create_entry(title=host, data=user_input)
        # Confirm step
        return self.async_show_form(
            step_id="device_info",
            data_schema=vol.Schema({vol.Required("confirm", default=True): bool}),
            description=description,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return WlanthermoBBQOptionsFlow(config_entry)
