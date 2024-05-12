import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from wireguard_tools.wireguard_config import WireguardConfig


WORK_DIR = Path(__file__).parent.parent

load_dotenv(WORK_DIR / "setup_utils/.env")

DEBUG = os.environ.get('DEBUG') == 'True'

DATABASE_URL = os.environ.get("DATABASE_URL")

PATH_TO_CLIENTS_FILES = WORK_DIR / 'vpnBot/client_files/'

if DEBUG:
    BOT_TOKEN = os.environ.get("DEBUG_BOT_TOKEN")
    BOT_TG_URL = os.environ.get('DEBUG_BOT_URL')
    _WG0_CONFIG_PATH = WORK_DIR / "wg_files/wg0.conf"
else:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    BOT_TG_URL = os.environ.get('BOT_URL')
    _WG0_CONFIG_PATH = Path("/etc/wireguard/wg0.conf")

_wg0_config = WireguardConfig()
_wg0_config.set_config(
    interface='wg0',
    public_key=os.environ.get('WG0_SERVER_PUBLIC_KEY'),
    endpoint=os.environ.get('WG0_SERVER_ENDPOINT'),
    config_path=_WG0_CONFIG_PATH,
    debug=DEBUG,
)

WIREGUARD_CONFIG_MAP: Dict[str, WireguardConfig] = {
    'wg0': _wg0_config
}
