import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
import threading
from datetime import datetime, timedelta

from config import BOT_TOKEN, ADMIN_ID
from database import db
from admin_panel import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# ============================
# Admin uchun ReplyKeyboard
# ============================
def admin_main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛠 Boshqarish"))
    return kb


# ============================
# Flask — Render Web Service porti
# ============================
@app.route('/')
def home():
    return "Bot is running!"


# ============================
# Admin state va data
# ============================
admin_state = {}
admin_data = {}


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

    text = (
        "📊 *Statistika*\n\n"
        f"🕒 Vaqt: *{time_str}* (O‘zbekiston)\n\n"
        f"👥 Jami foydalanuvchilar: *{total_users}*\n"
        f"🆕 Bugun qo‘shilganlar: *{today_users}*\n"
        f"⏱ Oxirgi 24 soat: *{last24_users}*\n"
        f"💎 VIP foydalanuvchilar: *{vip_users}*\n\n"
        f"🎥 Ongoing animelar: *{ongoing}*\n"
        f"✅ Tugallangan animelar: *{completed}*"
    )

    return text


# ============================
# /start — Ongoing Animelar
# ============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):

    # Foydalanuvchini bazaga qo‘shish
    db.users.update_one(
        {"user_id": msg.from_user.id},
        {"$setOnInsert": {"user_id": msg.from_user.id, "joined": msg.date}},
        upsert=True
    )

    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    text = "🎥 *Hozirgi Ongoing Animelar:*\n\n"
    i = 1

    for anime in animelist:
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)
        text += f"{i}. {name} ({current}/{total})\n"
        i += 1

    kb = InlineKeyboardMarkup()
    for n in range(1, i):
        kb.add(InlineKeyboardButton(str(n), callback_data=f"anime_{n}"))

    if msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id, text, reply_markup=admin_main_menu())
    else:
        bot.send_message(msg.chat.id, text, reply_markup=kb)


# ============================
# 🛠 Boshqarish tugmasi
# ============================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish")
def open_admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return bot.send_message(msg.chat.id, "⛔ Siz admin emassiz.")

    bot.send_message(msg.chat.id, "🌸 Admin panel", reply_markup=admin_panel())


# ============================
# Callbacklar
# ============================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    # Admin panel
    if data == "admin_panel":
        return bot.send_message(call.message.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

    # Statistika
    if data == "stats":
        bot.send_message(call.message.chat.id, get_stats())
        return bot.answer_callback_query(call.id)

    # Xabar yuborish menyusi
    if data == "send_msg":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("Forword", callback_data="send_forward"),
            InlineKeyboardButton("Oddiy", callback_data="send_simple")
        )
        bot.send_message(call.message.chat.id, "Qaysi turda xabar yubormoqchisiz?", reply_markup=kb)
        return bot.answer_callback_query(call.id)

    # FORWARD rejimi
    if data == "send_forward":
        admin_state[call.from_user.id] = "await_forward_msg"
        bot.send_message(call.message.chat.id, "Forward qilinadigan xabarni yuboring.")
        return bot.answer_callback_query(call.id)

    if data == "forward_confirm":
        msg = admin_data.get(call.from_user.id)
        users = db.users.find({})

        for u in users:
            try:
                bot.forward_message(u["user_id"], msg.chat.id, msg.message_id)
            except:
                pass

        bot.send_message(call.message.chat.id, "Xabar yuborildi!")
        admin_state.pop(call.from_user.id, None)
        admin_data.pop(call.from_user.id, None)
        return bot.answer_callback_query(call.id)

    if data == "forward_cancel":
        admin_state.pop(call.from_user.id, None)
        admin_data.pop(call.from_user.id, None)
        bot.send_message(call.message.chat.id, "Bekor qilindi.")
        return bot.answer_callback_query(call.id)

    # ODDIY rejimi
    if data == "send_simple":
        admin_state[call.from_user.id] = "await_simple_text"
        bot.send_message(call.message.chat.id, "Xabar yuboring.")
        return bot.answer_callback_query(call.id)

    if data == "simple_btn_yes":
        admin_state[call.from_user.id] = "await_btn_name"
        bot.send_message(call.message.chat.id, "Tugma nomini kiriting.")
        return bot.answer_callback_query(call.id)

    if data == "simple_btn_no":
        text = admin_data[call.from_user.id]["text"]
        users = db.users.find({})

        for u in users:
            try:
                bot.send_message(u["user_id"], text)
            except:
                pass

        bot.send_message(call.message.chat.id, "Xabar yuborildi!")
        admin_state.pop(call.from_user.id, None)
        admin_data.pop(call.from_user.id, None)
        return bot.answer_callback_query(call.id)


# ============================
# FORWARD xabarni qabul qilish
# ============================
@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_forward_msg")
def get_forward_msg(msg):
    admin_data[msg.from_user.id] = msg
    admin_state[msg.from_user.id] = "confirm_forward"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("Tasdiqlash", callback_data="forward_confirm"),
        InlineKeyboardButton("Bekor qilish", callback_data="forward_cancel")
    )

    bot.send_message(msg.chat.id, "Yuborishni xohlaysizmi?", reply_markup=kb)


# ============================
# ODDIY matnni qabul qilish
# ============================
@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_simple_text")
def get_simple_text(msg):
    admin_data[msg.from_user.id] = {"text": msg.text}
    admin_state[msg.from_user.id] = "simple_add_button"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("Ha", callback_data="simple_btn_yes"),
        InlineKeyboardButton("O‘tkazib yuborish", callback_data="simple_btn_no")
    )

    bot.send_message(msg.chat.id, "Tugma qo‘shishni xohlaysizmi?", reply_markup=kb)


# ============================
# Tugma nomi
# ============================
@bot.message_handler(func=lambda m: admin_state.get(m.from_user.id) == "await_btn_name")
def get_btn_name(msg):
    admin_data[msg.from_user.id]["btn_name"] = msg.text
    admin_state[msg.from_user.id] = "await_btn_url"
    bot.send_message(msg.chat.id, "URL (havola) kiriting.")


# ============================
# Tugma URL va yuborish
# ============================
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

    bot.send_message(msg.chat.id, "Xabar yuborildi!")

    admin_state.pop(msg.from_user.id, None)
    admin_data.pop(msg.from_user.id, None)


# ============================
# Pollingni alohida thread’da ishga tushiramiz
# ============================
def start_bot():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
