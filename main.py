import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

from config import BOT_TOKEN, ADMIN_ID
from database import db
from admin_panel import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)


# ============================
# Admin uchun bitta tugma (ReplyKeyboard)
# ============================
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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
# /start — Ongoing Animelar
# ============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    text = "🎥 *Hozirgi Ongoing Animelar:*\n\n"
    i = 1

    for anime in animelist:
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)
        text += f"{i}. {name} ({current}/{total})\n"
        i += 1

    # Inline raqam tugmalari
    kb = InlineKeyboardMarkup()
    for n in range(1, i):
        kb.add(InlineKeyboardButton(str(n), callback_data=f"anime_{n}"))

    # ADMIN uchun boshqaruv tugmasi (ReplyKeyboard)
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
# Inline tugmalar callbacklari
# ============================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    # Anime tanlash
    if data.startswith("anime_"):
        index = int(data.split("_")[1]) - 1
        animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

        if index < 0 or index >= len(animelist):
            return bot.answer_callback_query(call.id, "Xato raqam!")

        anime = animelist[index]
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)

        bot.send_message(
            call.message.chat.id,
            f"🎬 *{name}*\n\nEpizodlar: {current}/{total}",
            parse_mode="Markdown"
        )

        return bot.answer_callback_query(call.id)

    bot.answer_callback_query(call.id, "Bu bo‘lim hali qo‘shilmagan.")


# ============================
# Pollingni alohida thread’da ishga tushiramiz
# ============================
def start_bot():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
