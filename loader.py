import os
from pymongo import MongoClient
import telebot

# ==========================
#   CONFIG
# ==========================

# .env yoki config.py dan moslab olasan
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "anime_bot")
APP_URL = os.getenv("APP_URL")  # masalan: https://son-goku-4c47.onrender.com

# Adminlar ro‘yxati (string ko‘rinishida saqlash qulay)
# Masalan: "7797502113,7026418050"
ADMINS_RAW = os.getenv("ADMINS", "")
ADMINS = [x.strip() for x in ADMINS_RAW.split(",") if x.strip()]

# VIP foydalanuvchilar (ixtiyoriy)
VIP_RAW = os.getenv("VIP_USERS", "")
VIP_USERS = [x.strip() for x in VIP_RAW.split(",") if x.strip()]


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
    return str(user_id) in VIP_USERS
