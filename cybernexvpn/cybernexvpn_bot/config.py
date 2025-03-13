import os
from pathlib import Path

from dotenv import load_dotenv

BOT_DIR = Path(__file__).parent
BASE_DIR = BOT_DIR.parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_DB_TTL = 60 * 10

ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID"))
BOT_URL = os.environ.get("BOT_URL", "https://t.me/CyberNexVpnBot")

START_BALANCE = 100
INVITATION_BONUS = 50
FILLING_UP_VALUES = [100, 200, 300, 500, 700, 1000]
