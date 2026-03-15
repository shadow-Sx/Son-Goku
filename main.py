import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID
from database import db
from flask import Flask
import threading

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ============================
# /start — Ongoing Animelar
# ============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    if not animelist:
        return bot.send_message(msg.chat.id, "Hozircha ongoing animelar mavjud emas.")

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
        kb.add(InlineKeyboardButton("🛠 Boshqarish", callback_data="admin_panel"))

    bot.send_message(msg.chat.id, text, reply_markup=kb)


# ============================
# Callbacklar
# ============================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    if data == "admin_panel":
        from admin_panel import admin_panel
        return bot.send_message(call.message.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

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
