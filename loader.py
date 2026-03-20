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
#   ADMINS (string sifatida)
# ==========================
ADMINS_ENV = os.environ.get("ADMINS", "").strip()

if ADMINS_ENV:
    # "7797592113, 7206418056" → ["7797592113", "7206418056"]
    ADMINS = [x.strip() for x in ADMINS_ENV.split(",") if x.strip()]
else:
    ADMINS = []

print("ADMINS LOADED:", ADMINS)


# ==========================
#   VIP TEKSHIRISH
# ==========================
def is_vip(user_id):
    return db.vip_users.find_one({"user_id": user_id}) is not None


# ==========================
#   ADMIN TEKSHIRISH (string solishtirish)
# ==========================
def is_admin(user_id):
    return str(user_id) in ADMINS
