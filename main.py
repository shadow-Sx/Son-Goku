import os
import threading
import pytz
from datetime import datetime, timedelta
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup
from database import db

# ==========================
#   TOKEN VA BOT
# ==========================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7797502113
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==========================
#   DATABASE
# ==========================
users = db["users"]

# ==========================
#   FLASK
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ==========================
#   /start
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)

    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "joined": datetime.now(pytz.timezone("Asia/Tashkent"))
        })

    text = "👋 Salom!\nBu test versiya. Statistika ishlayapti."

    if is_admin:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("📊 Statistika")
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        bot.send_message(message.chat.id, text)

# ==========================
#   📊 STATISTIKA
# ==========================
def get_stats():
    tz = pytz.timezone("Asia/Tashkent")
    now = datetime.now(tz)

    total = users.count_documents({})
    today = users.count_documents({
        "joined": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
    })

    return (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total}</b>\n"
        f"📅 Bugun qo‘shilganlar: <b>{today}</b>\n"
        f"⏱ Sana va vaqt: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID)
def show_stats(message):
    bot.send_message(message.chat.id, get_stats())

# ==========================
#   POLLING + FLASK
# ==========================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=False).start()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
