import os
import telebot
from pymongo import MongoClient

# ==========================
#   TOKEN
# ==========================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("❌ BOT_TOKEN environment variable topilmadi!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ==========================
#   APP_URL (Render URL)
# ==========================
APP_URL = os.environ.get("APP_URL")
if not APP_URL:
    raise Exception("❌ APP_URL environment variable topilmadi!")


# ==========================
#   MONGO DB
# ==========================
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise Exception("❌ MONGO_URI environment variable topilmadi!")

client = MongoClient(MONGO_URI)
db = client["anime_bot"]


# ==========================
#   ADMINS (Environment orqali)
# ==========================
ADMINS_ENV = os.environ.get("ADMINS", "")

# Masalan: "12345,67890"
if ADMINS_ENV.strip():
    ADMINS = [int(x) for x in ADMINS_ENV.split(",") if x.strip().isdigit()]
else:
    ADMINS = []

print("ADMINS:", ADMINS)


# ==========================
#   VIP TEKSHIRISH
# ==========================
def is_vip(user_id: int) -> bool:
    return db.vip_users.find_one({"user_id": user_id}) is not None


# ==========================
#   ADMIN TEKSHIRISH
# ==========================
def is_admin(user_id):
    return str(user_id) in [str(x) for x in ADMINS]
