import os
from pathlib import Path

from dotenv import load_dotenv

BOT_DIR = Path(__file__).parent.parent
BASE_DIR = BOT_DIR.parent

print(BASE_DIR)
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

REDIS_BROKER = os.environ.get("REDIS_BROKER", "redis://redis:6379/0")
REDIS_BACKEND = os.environ.get("REDIS_BACKEND", "redis://redis:6379/0")

ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID"))
BOT_URL = os.environ.get("BOT_URL", "https://t.me/CyberNexVpnBot")

START_BALANCE = 100
INVITATION_BONUS = 50
FILLING_UP_VALUES = [100, 200, 300, 500, 700, 1000]
