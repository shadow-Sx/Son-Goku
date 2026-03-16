import os
import threading
import telebot
from flask import Flask
from telebot.types import ReplyKeyboardMarkup
from admin_menu import admin_panel   # admin tugmalar shu faylda

# ==========================
#   TOKEN VA BOT
# ==========================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7797502113   # o'zingning admin ID'ingni qo'y
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==========================
#   FLASK — UptimeRobot uchun
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ==========================
#   /start — oddiy foydalanuvchi + admin
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    is_admin = (message.from_user.id == ADMIN_ID)

    text = (
        "🎥 <b>Ongoing Animelar ro‘yxati</b>\n\n"
        "1) ...\n"
        "2) ...\n"
        "3) ...\n"
    )

    if is_admin:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("🛠 Boshqarish")
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        bot.send_message(message.chat.id, text)

# ==========================
#   ADMIN PANELGA KIRISH
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish" and m.from_user.id == ADMIN_ID)
def open_admin(message):
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Admin panel</b>",
        reply_markup=admin_panel()
    )

# ==========================
#   ADMIN PANELDAN ORQAGA
# ==========================
@bot.message_handler(func=lambda m: m.text == "◀️ Orqaga" and m.from_user.id == ADMIN_ID)
def back_to_user(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛠 Boshqarish")
    bot.send_message(
        message.chat.id,
        "◀️ Asosiy menyuga qaytdingiz.",
        reply_markup=kb
    )

# ==========================
#   POLLING — fon threadda
# ==========================
def run_polling():
    print(">>> POLLING STARTED <<<")
    bot.infinity_polling(skip_pending=True)

# ==========================
#   RUN SERVER
# ==========================
if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
