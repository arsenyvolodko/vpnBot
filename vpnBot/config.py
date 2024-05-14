import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from wireguard_tools.wireguard_config import WireguardConfig


WORK_DIR = Path(__file__).parent.parent

load_dotenv(WORK_DIR / ".env")

DEBUG = os.environ.get('DEBUG') == 'True'

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_TG_URL = os.environ.get("BOT_URL")

DATABASE_URL = os.environ.get("DATABASE_URL")

PATH_TO_CLIENTS_FILES = WORK_DIR / 'vpnBot/tmp_client_files/'
SYNC_CONFIG_FILE_PATH = WORK_DIR / 'wireguard_tools/sync_config.sh'

WG_CONFIGS_PATH = Path(os.environ.get('WG_CONFIGS_PATH'))
_WG0_CONFIG_PATH = WG_CONFIGS_PATH / "wg0.conf"

_wg0_config = WireguardConfig()
_wg0_config.set_config(
    interface='wg0',
    private_key=os.environ.get('WG0_SERVER_PRIVATE_KEY'),
    endpoint=os.environ.get('WG0_SERVER_ENDPOINT'),
    config_path=_WG0_CONFIG_PATH,
    sync_config_file_path=SYNC_CONFIG_FILE_PATH,
    debug=DEBUG,
)

WIREGUARD_CONFIG_MAP: Dict[str, WireguardConfig] = {
    'wg0': _wg0_config
}
