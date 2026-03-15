import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
from datetime import datetime, timedelta

from config import BOT_TOKEN, ADMIN_ID
from database import db
from admin_menu import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

admin_state = {}
admin_data = {}

# ============================
# Flask Web Service
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
# ✉ Xabar yuborish
# ============================
@bot.message_handler(func=lambda m: m.text == "✉ Xabar yuborish")
def send_msg_menu(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Forword"), KeyboardButton("Oddiy"))
    kb.add(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(msg.chat.id, "Qaysi turda xabar yubormoqchisiz?", reply_markup=kb)

# ============================
# ⬅️ Orqaga
# ============================
@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def back_to_admin(msg):
    bot.send_message(msg.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

# ============================
# FORWARD rejimi
# ============================
@bot.message_handler(func=lambda m: m.text == "Forword")
def forward_mode(msg):
    admin_state[msg.from_user.id] = "await_forward_msg"
    bot.send_message(msg.chat.id, "Forward qilinadigan xabarni yuboring.")

@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_forward_msg")
def get_forward_msg(msg):
    admin_data[msg.from_user.id] = msg
    admin_state[msg.from_user.id] = "confirm_forward"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Tasdiqlash"), KeyboardButton("Bekor qilish"))

    bot.send_message(msg.chat.id, "Yuborishni xohlaysizmi?", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "Tasdiqlash")
def forward_confirm(msg):
    if admin_state.get(msg.from_user.id) != "confirm_forward":
        return

    fwd = admin_data[msg.from_user.id]
    users = db.users.find({})

    for u in users:
        try:
            bot.forward_message(u["user_id"], fwd.chat.id, fwd.message_id)
        except:
            pass

    bot.send_message(msg.chat.id, "Xabar yuborildi!", reply_markup=admin_panel())
    admin_state.pop(msg.from_user.id, None)
    admin_data.pop(msg.from_user.id, None)

@bot.message_handler(func=lambda m: m.text == "Bekor qilish")
def forward_cancel(msg):
    admin_state.pop(msg.from_user.id, None)
    admin_data.pop(msg.from_user.id, None)
    bot.send_message(msg.chat.id, "Bekor qilindi.", reply_markup=admin_panel())

# ============================
# ODDIY rejimi
# ============================
@bot.message_handler(func=lambda m: m.text == "Oddiy")
def simple_mode(msg):
    admin_state[msg.from_user.id] = "await_simple_text"
    bot.send_message(msg.chat.id, "Xabar yuboring.")

@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_simple_text")
def get_simple_text(msg):
    admin_data[msg.from_user.id] = {"text": msg.text}
    admin_state[msg.from_user.id] = "simple_add_button"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Ha"), KeyboardButton("O‘tkazib yuborish"))

    bot.send_message(msg.chat.id, "Tugma qo‘shishni xohlaysizmi?", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "Ha")
def ask_btn_name(msg):
    if admin_state.get(msg.from_user.id) != "simple_add_button":
        return

    admin_state[msg.from_user.id] = "await_btn_name"
    bot.send_message(msg.chat.id, "Tugma nomini kiriting.")

@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_btn_name")
def get_btn_name(msg):
    admin_data[msg.from_user.id]["btn_name"] = msg.text
    admin_state[msg.from_user.id] = "await_btn_url"
    bot.send_message(msg.chat.id, "URL (havola) kiriting.")

@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_btn_url")
def get_btn_url(msg):
    data = admin_data[msg.from_user.id]
    text = data["text"]
    btn_name = data["btn_name"]
    url = msg.text

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(btn_name, url=url))

    users = db.users.find({})
    for u in users:
        try:
            bot.send_message(u["user_id"], text, reply_markup=kb)
        except:
            pass

    bot.send_message(msg.chat.id, "Xabar yuborildi!", reply_markup=admin_panel())

    admin_state.pop(msg.from_user.id, None)
    admin_data.pop(msg.from_user.id, None)

@bot.message_handler(func=lambda m: m.text == "O‘tkazib yuborish")
def send_without_button(msg):
    if admin_state.get(msg.from_user.id) != "simple_add_button":
        return

    text = admin_data[msg.from_user.id]["text"]
    users = db.users.find({})

    for u in users:
        try:
            bot.send_message(u["user_id"], text)
        except:
            pass

    bot.send_message(msg.chat.id, "Xabar yuborildi!", reply_markup=admin_panel())

    admin_state.pop(msg.from_user.id, None)
    admin_data.pop(msg.from_user.id, None)

# ============================
# Pollingni threadda ishga tushiramiz
# ============================
def start_polling():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=start_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
