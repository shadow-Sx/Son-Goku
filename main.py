import os
from flask import Flask, request
import telebot

from admin_menu import admin_panel

# HANDLERLARNI YUKLAYMIZ
from handlers import (
    admin_settings,
    admin_stats,
    admin_broadcast,
    admin_posts,
    admin_anime,
    admin_wallets,
    admin_users,
    admin_channels,
    admin_buttons,
    admin_texts,
    admin_admins,
    admin_botstatus
)

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

ADMIN_ID = 7797502113

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        kb = admin_panel()
        bot.send_message(message.chat.id, "👋 Salom admin!", reply_markup=kb)
    else:
        bot.send_message(message.chat.id, "🔥 Ongoing Animelar ro‘yxati:\n1) Solo Leveling\n2) Mashle 2\n3) Dungeon Meshi")

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

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
