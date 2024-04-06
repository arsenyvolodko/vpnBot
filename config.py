import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')
DEBUG = bool(os.environ.get('DEBUG'))

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

SERVER_PUBLIC_KEY = os.environ.get('SERVER_PUBLIC_KEY')
SERVER_ENDPOINT = os.environ.get('SERVER_ENDPOINT')

# BASE_PATH = '/home/vpnBot/'

WORK_DIR = Path(__file__).parent

PATH_TO_SYNC = WORK_DIR / 'utils/sync_iter.sh'

if DEBUG:
    PATH_TO_CONFIG = WORK_DIR / "some_dir/server.conf"
    PATH_TO_LOGS = WORK_DIR / 'logs.txt'
    PATH_TO_CLIENTS_FILES = WORK_DIR / 'client_files/'
else:
    PATH_TO_CONFIG = "/etc/wireguard/wg0.conf"
    PATH_TO_LOGS = WORK_DIR / 'logs.txt'
    PATH_TO_CLIENTS_FILES = WORK_DIR / 'client_files/'
