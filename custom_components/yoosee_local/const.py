"""Constants for the Yoosee Local integration."""
from homeassistant.const import Platform

DOMAIN = "yoosee_local"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"

DEFAULT_PORT = 554
DEFAULT_TIMEOUT = 2.0

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.SIREN,
]

DIRECTIONS = {
    "up": "UP",
    "down": "DWON",  # Firmware typo required for Anyka AK3918
    "left": "LEFT",
    "right": "RIGHT",
}

SOUND_OPTIONS = [
    "alarm",
    "DoorBell",
    "Beep",
    "du",
    "QRCodeScanSucc_DingDong",
    "clear",
    "set_ok",
    "set_fail",
]

DEFAULT_SOUND = "alarm"
