import os
from flask import Flask, request
import telebot

from admin_menu import admin_panel   # <-- admin tugmalarni chaqiramiz

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
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        # ADMIN PANEL
        kb = admin_panel()
        bot.send_message(
            message.chat.id,
            "👋 Salom, admin!\nAdmin panelga xush kelibsiz.",
            reply_markup=kb
        )
    else:
        # ODDIY USER UCHUN
        ongoing = (
            "🔥 <b>Ongoing Animelar</b>\n\n"
            "1️⃣ Solo Leveling\n"
            "2️⃣ Mashle Season 2\n"
            "3️⃣ Dungeon Meshi\n"
            "4️⃣ One Piece (weekly)\n"
            "5️⃣ Blue Lock Season 2\n"
        )

        bot.send_message(message.chat.id, ongoing)

# ==========================
#   ADMIN PANEL HANDLER
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Admin panel" and m.from_user.id == ADMIN_ID)
def admin_panel_open(message):
    kb = admin_panel()
    bot.send_message(message.chat.id, "⚙️ Admin panelga qaytdingiz.", reply_markup=kb)

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
