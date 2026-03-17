import os
from flask import Flask, request
import telebot

from loader import bot, db, ADMIN_ID
from admin_menu import admin_panel

# HANDLERLARNI ULASH
from handlers.admin_panel import menu as admin_menu
from handlers.admin_anime import menu as anime_menu
from handlers.admin_anime import add_anime
from handlers.admin_anime import add_episode
from handlers.admin_anime import list_anime
from handlers.admin_anime import edit_anime

APP_URL = os.getenv("APP_URL")

app = Flask(__name__)


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if " " in message.text:
        bot.send_message(message.chat.id, "🎬 Anime ko‘rish bo‘limi keyin yoziladi.")
        return

    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "👋 Salom, admin!", reply_markup=admin_panel())
        return

    animes = list(db.animes.find({"status": "Ongoing"}).sort("code", 1))

    if not animes:
        bot.send_message(message.chat.id, "🔥 Hozircha ongoing animelar yo‘q.")
        return

    text = "🔥 <b>Ongoing Animelar</b>\n\n"
    for a in animes:
        text += f"• {a['name']}\n"

    bot.send_message(message.chat.id, text)


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
