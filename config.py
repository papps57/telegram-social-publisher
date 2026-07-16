import os
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN mancante nel .env")

ALLOWED_USER_IDS = [
    int(x.strip())
    for x in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if x.strip()
]

PAGES = []
for i in range(1, 10):
    name = os.getenv(f"PAGE_{i}_NAME")
    if not name:
        break
    PAGES.append({
        "name": name,
        "id": os.getenv(f"PAGE_{i}_ID"),
        "token": os.getenv(f"PAGE_{i}_TOKEN"),
        "ig_id": os.getenv(f"INSTAGRAM_{i}_ID"),
    })

if not PAGES:
    raise ValueError("Nessuna pagina configurata nel .env")


def token_days_left():
    raw = os.getenv("TOKEN_GENERATED_AT")
    if not raw:
        return None
    try:
        generated = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
        days_passed = (date.today() - generated).days
        return max(0, 60 - days_passed)
    except ValueError:
        return None


FB_API_VERSION = "v22.0"
FB_BASE_URL = f"https://graph.facebook.com/{FB_API_VERSION}"
