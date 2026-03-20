import os
import time
from flask import Flask, request
import telebot

from loader import bot, db, is_admin, is_vip, ADMINS, APP_URL
from admin_menu import admin_panel  # reply keyboard

app = Flask(__name__)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    print("START HANDLER WORKING, USER:", user_id)

    # Admin bo‘lsa — boshqarish tugmasi chiqadi
    if is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "🛠 Admin panel",
            reply_markup=admin_panel()
        )
        return

    # VIP bo‘lsa
    if is_vip(user_id):
        bot.send_message(message.chat.id, "👑 VIP foydalanuvchi, hush kelibsiz!")
        return

    # Oddiy foydalanuvchi
    bot.send_message(message.chat.id, "Assalomu alaykum! Ongoing animelarni ko‘rishingiz mumkin.")


# ==========================
#   /stop — admin panelga tez kirish
# ==========================
@bot.message_handler(commands=["stop"])
def stop(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🛠 Admin panel", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat adminlar uchun.")


# ==========================
#   FLASK ROUTELAR
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


# ==========================
#   HANDLERLARNI IMPORT QILISH
# ==========================
# Muhim: bularni bot va app e’lon qilingandan KEYIN import qilamiz

# Anime sahifasi va callbacklari
import anime_page  # open_anime_page, build_episode_keyboard va callbacklar

# Admin panel (inline)
from handlers.admin_panel import menu as admin_panel_menu

# Admin anime bo‘limi
from handlers.admin_anime import (
    add_anime,
    add_episode,
    edit_anime,
    list_anime,
    menu as anime_menu,
)

# Kanallar bo‘limi
from handlers.channels import (
    add as ch_add,
    delete as ch_delete,
    list as ch_list,
    check as ch_check,
    menu as ch_menu,
)

# Foydalanuvchilarni boshqarish
from handlers.user_manage import (
    add_vip,
    delete_vip,
    list_vip,
    menu as user_menu,
)

# Agar qo‘shimcha fayllar (delete_anime.py, clear_episodes.py) bo‘lsa, ularni ham shu yerda import qilasan:
# from handlers.admin_anime import delete_anime, clear_episodes


# ==========================
#   ENTRY POINT
# ==========================
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
