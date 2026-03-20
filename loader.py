import os
import time
from pymongo import MongoClient
import telebot

# ==========================
#   CONFIG
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "anime_bot")
APP_URL = os.getenv("APP_URL")  # masalan: https://son-goku-4c47.onrender.com

ADMINS_RAW = os.getenv("ADMINS", "")
ADMINS = [x.strip() for x in ADMINS_RAW.split(",") if x.strip()]

# ==========================
#   BOT VA DB
# ==========================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


# ==========================
#   FOYDALANUVCHI TEKSHIRUV FUNKSIYALARI
# ==========================

def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMINS


def is_vip(user_id: int) -> bool:
    vip = db.vip_users.find_one({"user_id": user_id})
    if not vip:
        return False
    return vip.get("expires_at", 0) > int(time.time())


def check_vip_expiration(user_id: int):
    vip = db.vip_users.find_one({"user_id": user_id})
    if not vip:
        return

    now = int(time.time())
    left = vip["expires_at"] - now

    # 10 kun = 864000 sekund
    if 0 < left < 864000 and not vip.get("warned_10_days"):
        try:
            bot.send_message(
                user_id,
                "⚠️ Sizning VIP holatingiz tugashiga 10 kun qoldi."
            )
        except:
            pass

        db.vip_users.update_one(
            {"user_id": user_id},
            {"$set": {"warned_10_days": True}}
        )
