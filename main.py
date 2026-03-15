import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from flask import Flask
import threading

from config import BOT_TOKEN, ADMIN_ID
from database import db
from admin_menu import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

admin_state = {}
admin_data = {}

# ============================
# Flask Web Service (Render uchun majburiy)
# ============================
@app.route('/')
def home():
    return "Bot is running!"

# ============================
# Admin bosh menyu
# ============================
def admin_main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛠 Boshqarish"))
    return kb

# ============================
# Statistika funksiyasi
# ============================
def get_stats():
    total_users = db.users.count_documents({})

    today = datetime.utcnow().date()
    today_users = db.users.count_documents({
        "joined": {"$gte": datetime(today.year, today.month, today.day)}
    })

    last24 = datetime.utcnow() - timedelta(hours=24)
    last24_users = db.users.count_documents({"joined": {"$gte": last24}})

    vip_users = db.users.count_documents({"vip": True})

    ongoing = db.anime.count_documents({"status": {"$ne": "completed"}})
    completed = db.anime.count_documents({"status": "completed"})

    uz_time = datetime.utcnow() + timedelta(hours=5)
    time_str = uz_time.strftime("%Y-%m-%d %H:%M:%S")

    return (
        "📊 *Statistika*\n\n"
        f"🕒 Vaqt: *{time_str}* (O‘zbekiston)\n\n"
        f"👥 Jami foydalanuvchilar: *{total_users}*\n"
        f"🆕 Bugun qo‘shilganlar: *{today_users}*\n"
        f"⏱ Oxirgi 24 soat: *{last24_users}*\n"
        f"💎 VIP foydalanuvchilar: *{vip_users}*\n\n"
        f"🎥 Ongoing animelar: *{ongoing}*\n"
        f"✅ Tugallangan animelar: *{completed}*"
    )

# ============================
# /start
# ============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    db.users.update_one(
        {"user_id": msg.from_user.id},
        {"$setOnInsert": {"user_id": msg.from_user.id, "joined": msg.date}},
        upsert=True
    )

    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    text = "🎥 *Hozirgi Ongoing Animelar:*\n\n"
    for i, anime in enumerate(animelist, start=1):
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)
        text += f"{i}. {name} ({current}/{total})\n"

    if msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id, text, reply_markup=admin_main_menu())
    else:
        bot.send_message(msg.chat.id, text)

# ============================
# 🛠 Boshqarish
# ============================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish")
def open_admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return bot.send_message(msg.chat.id, "⛔ Siz admin emassiz.")
    bot.send_message(msg.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

# ============================
# 📊 Statistika
# ============================
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats_handler(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, get_stats())

# ============================
# ✉️ Xabar Yuborish — menyu
# ============================
@bot.message_handler(func=lambda m: m.text == "✉️ Xabar Yuborish")
def send_msg_menu(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Forword"), KeyboardButton("Oddiy"))
    kb.add(KeyboardButton("◀️ Orqaga"))

    bot.send_message(msg.chat.id, "Qaysi turda xabar yubormoqchisiz?", reply_markup=kb)

# ============================
# ◀️ Orqaga
# ============================
@bot.message_handler(func=lambda m: m.text == "◀️ Orqaga")
def back_to_admin(msg):
    bot.send_message(msg.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

# ============================
# Pollingni threadda ishga tushiramiz
# ============================
def start_polling():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=start_polling, daemon=True).start()
import os
app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

