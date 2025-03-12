import os
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).parent

load_dotenv(API_DIR / ".env")

API_KEY = os.environ.get("API_KEY")
