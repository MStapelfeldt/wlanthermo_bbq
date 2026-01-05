# Device models
MODELS = [
	("select", "Select"),
	("link_v1", "Link V1"),
	("nano_v3", "Nano-V3"),
	("mini_v2", "Mini-V2"),
	("mini_v3", "Mini-V3"),
]
"""Constants for the WLANThermo BBQ integration."""


DOMAIN = "wlanthermo_bbq"
CONF_PATH_PREFIX = "path_prefix"
CONF_MODEL = "model"

# Alarm modes
ALARM_OFF = 0
ALARM_PUSH = 1
ALARM_BUZZER = 2
ALARM_PUSH_BUZZER = 3

ALARM_MODES = {
	ALARM_OFF: "off",
	ALARM_PUSH: "push",
	ALARM_BUZZER: "buzzer",
	ALARM_PUSH_BUZZER: "push_buzzer",
}
