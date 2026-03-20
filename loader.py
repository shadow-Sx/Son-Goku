import os
from telebot import TeleBot
from pymongo import MongoClient

# ==========================
#   ENVIRONMENT
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Render URL: https://your-app.onrender.com
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "anime_bot")

# Bir nechta admin ID
# Masalan: "123456789,987654321"
ADMINS_ENV = os.getenv("ADMINS", "")
if ADMINS_ENV.strip():
    ADMINS = [int(x) for x in ADMINS_ENV.split(",") if x.strip().isdigit()]
else:
    ADMINS = []  # agar env bo'lmasa, keyin qo'lda to'ldirasan

# ==========================
#   TELEGRAM BOT
# ==========================

bot = TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==========================
#   DATABASE
# ==========================

mongo_client = MongoClient(MONGO_URL)
db = mongo_client[DB_NAME]


# ==========================
#   HELPERS
# ==========================

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def is_vip(user_id: int) -> bool:
    """
    VIP foydalanuvchini tekshirish.
    db.vip_users kolleksiyasida saqlanadi deb faraz qilamiz:
    { "user_id": 123456789 }
    """
    return db.vip_users.find_one({"user_id": user_id}) is not None
