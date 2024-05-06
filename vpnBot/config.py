import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get('DEBUG') == 'True'

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

SERVER_PUBLIC_KEY = os.environ.get('SERVER_PUBLIC_KEY')
SERVER_ENDPOINT = os.environ.get('SERVER_ENDPOINT')

WORK_DIR = Path(__file__).parent

PATH_TO_LOGS = WORK_DIR / 'logs.txt'

if DEBUG:
    PATH_TO_CONFIG = WORK_DIR / "some_dir/server.conf"
    PATH_TO_CLIENTS_FILES = WORK_DIR / 'client_files/'
else:
    PATH_TO_CONFIG = Path("/etc/wireguard/wg0.conf")
    PATH_TO_CLIENTS_FILES = WORK_DIR / 'client_files/'
