import os
import time
from flask import Flask, request
import telebot

# ==========================
#   LOADER
# ==========================
from loader import bot, db, ADMINS, is_vip, APP_URL


# ==========================
#   HANDLERLARNI IMPORT QILISH
# ==========================

# ADMIN PANEL
from handlers.admin_panel import menu as admin_menu

# ANIME ADMIN
from handlers.admin_anime import menu as anime_menu
from handlers.admin_anime import add_anime
from handlers.admin_anime import add_episode
from handlers.admin_anime import list_anime
from handlers.admin_anime import edit_anime

# KANALLAR
from handlers.channels import menu as channels_menu
from handlers.channels import add as channels_add
from handlers.channels import list as channels_list
from handlers.channels import delete as channels_delete
from handlers.channels import check as channels_check

# VIP
from handlers.user_manage import menu as user_manage_menu
from handlers.user_manage import add_vip
from handlers.user_manage import delete_vip
from handlers.user_manage import list_vip

# ANIME PAGE
from handlers.anime_page import open_anime_page, build_episode_keyboard
import handlers.anime_page


app = Flask(__name__)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    print("FULL MESSAGE:", message.text)

    user_id = message.from_user.id

    try:
        start_param = message.text.split(" ", 1)[1]
    except:
        start_param = None

    print("START PARAM:", start_param)

    # ADMIN → obuna tekshiruvi yo‘q
    if user_id in ADMINS:
        return handle_start_param(message, start_param)

    # VIP → obuna tekshiruvi yo‘q
    if is_vip(user_id):
        return handle_start_param(message, start_param)

    # MAJBURIY OBUNA
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

    return handle_start_param(message, start_param)


# ==========================
#   START PARAMETRNI ISHLASH
# ==========================
def handle_start_param(message, start_param):

    if start_param:

        # ⭐ DEEP LINK: code_episode
        if "_" in start_param:
            try:
                code, ep = start_param.split("_")
                return open_episode_from_start(message, int(code), int(ep))
            except:
                pass

        # Oddiy anime kodi
        if start_param.isdigit():
            return open_anime_page(message, int(start_param))

        # anime_4 format
        if start_param.startswith("anime_"):
            code = int(start_param.replace("anime_", ""))
            return open_anime_page(message, code)

    # Oddiy /start
    animes = list(db.animes.find({"status": "Ongoing"}).sort("code", 1))

    if not animes:
        bot.send_message(message.chat.id, "🔥 Hozircha ongoing animelar yo‘q.")
        return

    text = "🔥 <b>Ongoing Animelar</b>\n\n"
    for a in animes:
        text += f"• {a['name']}\n"

    bot.send_message(message.chat.id, text)


# ==========================
#   DEEP LINK → QISMNI OCHISH
# ==========================
def open_episode_from_start(message, code, ep_num):
    anime = db.animes.find_one({"code": code})
    ep = db.episodes.find_one({"anime_code": code, "episode": ep_num})

    if not anime or not ep:
        bot.send_message(message.chat.id, "❌ Qism topilmadi.")
        return

    caption = f"<b>{anime['name']}</b>\n<i>{ep_num}-qism</i>"

    kb = build_episode_keyboard(code, 1, current_ep=ep_num)

    bot.send_video(
        message.chat.id,
        ep["video_file_id"],
        caption=caption,
        reply_markup=kb,
        parse_mode="HTML"
    )


# ==========================
#   /stop — admin panel
# ==========================
@bot.message_handler(commands=["stop"])
def stop(message):
    if message.from_user.id in ADMINS:
        from handlers.admin_panel import admin_panel
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
