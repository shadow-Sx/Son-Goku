import os
from flask import Flask, request
import telebot

from loader import bot, db, ADMIN_ID, is_vip
from admin_menu import admin_panel

# ADMIN PANEL
from handlers.admin_panel import menu as admin_menu

# ANIME ADMIN BO‘LIMI
from handlers.admin_anime import menu as anime_menu
from handlers.admin_anime import add_anime
from handlers.admin_anime import add_episode
from handlers.admin_anime import list_anime
from handlers.admin_anime import edit_anime

# KANALLAR BO‘LIMI
from handlers.channels import menu as channels_menu
from handlers.channels import add as channels_add
from handlers.channels import list as channels_list
from handlers.channels import delete as channels_delete
from handlers.channels import check as channels_check

# VIP FOYDALANUVCHI BOSHQARUV
from handlers.user_manage import menu as user_manage_menu
from handlers.user_manage import add_vip
from handlers.user_manage import delete_vip
from handlers.user_manage import list_vip

# ⭐ ANIME SAHIFASI FUNKSIYASI
from handlers.anime_page import open_anime_page

APP_URL = os.getenv("APP_URL")

app = Flask(__name__)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # start paramni olish
    try:
        start_param = message.text.split(" ", 1)[1]
    except:
        start_param = None

    print("START PARAM:", start_param)

    # ADMIN → majburiy obuna yo‘q
    if user_id == ADMIN_ID:
        return handle_start_param(message, start_param)

    # VIP → majburiy obuna yo‘q
    if is_vip(user_id):
        return handle_start_param(message, start_param)

    # ==========================
    #   MAJBURIY OBUNA (HAR QANDAY start uchun)
    # ==========================
    channels = list(db.forced_channels.find())

    if channels:
        not_joined = []

        for ch in channels:
            try:
                member = bot.get_chat_member(ch["channel_id"], user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    not_joined.append(ch)
            except:
                not_joined.append(ch)

        if not_joined:
            from handlers.channels.check import subscription_menu
            bot.send_message(
                message.chat.id,
                "📢 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>",
                reply_markup=subscription_menu(user_id, start_param)
            )
            return

    # Obuna bo‘lgan → start parametrni ishlatamiz
    return handle_start_param(message, start_param)


# ==========================
#   START PARAMETRNI ISHLASH
# ==========================
def handle_start_param(message, start_param):

    # ⭐ Anime sahifasi
    if start_param:

        # start=2 → anime kodi
        if start_param.isdigit():
            return open_anime_page(message, int(start_param))

        # start=anime_2 → anime kodi
        if start_param.startswith("anime_"):
            code = int(start_param.replace("anime_", ""))
            return open_anime_page(message, code)

    # ⭐ Oddiy /start → Ongoing Animelar
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
