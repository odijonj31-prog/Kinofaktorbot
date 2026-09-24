import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

_admin_ids_raw = os.getenv("SUPER_ADMIN_ID", "0")
SUPER_ADMIN_IDS = set(int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip())
SUPER_ADMIN_ID = next(iter(SUPER_ADMIN_IDS), 0)

DATABASE_URL = os.getenv("DATABASE_URL")

# AI tavsiya funksiyasi uchun (ixtiyoriy — bo'lmasa shu funksiya o'chiq turadi)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida topilmadi!")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL .env faylida topilmadi!")
