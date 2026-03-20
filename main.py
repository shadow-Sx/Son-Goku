import os
import time
from flask import Flask, request
import telebot

# ==========================
#   LOADER
# ==========================
from loader import bot, db, is_admin, is_vip, ADMINS, APP_URL


# ==========================
#   HANDLER IMPORTLARI
# ==========================

# ADMIN PANEL
from handlers.admin_panel.menu import admin_panel

# ANIME PAGE
from handlers.anime_page import open_anime_page, build_episode_keyboard


app = Flask(__name__)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    print("START HANDLER WORKING, USER:", user_id)

    # ADMIN → boshqarish tugmasi chiqadi
    if is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "🛠 Admin panel",
            reply_markup=admin_panel()
        )
        return

    # VIP → obuna tekshiruvi yo‘q
    if is_vip(user_id):
        return bot.send_message(message.chat.id, "VIP foydalanuvchi, hush kelibsiz!")

    # ODDIY USER → oddiy start
    bot.send_message(message.chat.id, "Assalomu alaykum! Ongoing animelarni ko‘rishingiz mumkin.")


# ==========================
#   /stop — admin panel
# ==========================
@bot.message_handler(commands=["stop"])
def stop(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🛠 Admin panel", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat admin uchun.")


# ==========================
#   WEBHOOK
# ==========================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
