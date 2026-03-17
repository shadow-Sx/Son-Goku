import os
import telebot
from pymongo import MongoClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7797502113"))

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

mongo = MongoClient(MONGO_URI)
db = mongo["anime_bot"]

# ⭐ VIP tekshirish funksiyasi
def is_vip(user_id):
    return db.vip_users.find_one({"user_id": user_id}) is not None
