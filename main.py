import os
from flask import Flask, request
import telebot
from pymongo import MongoClient

# ==========================
#   ENV VARIABLES
# ==========================
TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7797502113"))

# ==========================
#   BOT & APP
# ==========================
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ==========================
#   DATABASE
# ==========================
mongo = MongoClient(MONGO_URI)
db = mongo["anime_bot"]   # xohlasang nomini o‘zgartirishing mumkin


# ==========================
#   ADMIN PANEL
# ==========================
from admin_menu import admin_panel


# ==========================
#   HANDLER MODULLARNI ULASH
# ==========================
from handlers.admin_anime import menu
from handlers.admin_anime import add_anime
from handlers.admin_anime import add_episode
from handlers.admin_anime import list_anime
from handlers.admin_anime import edit_anime


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # start param bo‘lsa (foydalanuvchi anime yoki qism ochishi)
    if " " in message.text:
        # Foydalanuvchi tomoni keyin yoziladi
        bot.send_message(message.chat.id, "🎬 Anime ko‘rish bo‘limi keyin yoziladi.")
        return

    # ADMIN
    if user_id == ADMIN_ID:
        kb = admin_panel()
        bot.send_message(
            message.chat.id,
            "👋 Salom, admin!\nAdmin panelga xush kelibsiz.",
            reply_markup=kb
        )
        return

    # ODDIY FOYDALANUVCHI
    animes = list(db.animes.find({"status": "Ongoing"}).sort("code", 1))

    if not animes:
        bot.send_message(message.chat.id, "🔥 Hozircha ongoing animelar yo‘q.")
        return

    text = "🔥 <b>Ongoing Animelar</b>\n\n"
    for a in animes:
        text += f"• {a['name']}\n"

    bot.send_message(message.chat.id, text)


# ==========================
#   WEBHOOK ROUTES
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
#   WEBHOOK SET
# ==========================
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")


# ==========================
#   RUN
# ==========================
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
