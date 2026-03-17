import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

ADMIN_ID = 7797502113

# ==========================
#   /start
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        from telebot.types import ReplyKeyboardMarkup
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("🛠 Admin panel")
        bot.send_message(message.chat.id, "👋 Salom! Webhook ishlayapti.", reply_markup=kb)
    else:
        bot.send_message(message.chat.id, "👋 Salom! Webhook ishlayapti.")

# ==========================
#   ADMIN PANEL
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Admin panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    bot.send_message(message.chat.id, "⚙️ Admin panelga xush kelibsiz!")

# ==========================
#   FLASK WEBHOOK
# ==========================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# ==========================
#   WEBHOOK O‘RNATISH
# ==========================
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
