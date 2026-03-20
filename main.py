import os
from flask import Flask, request
import telebot

from loader import bot, db, APP_URL, is_admin, is_vip

# ==========================
#   HANDLERLARNI YUKLASH
# ==========================

# Anime sahifasi va qism ochish
from handlers.anime_page import open_anime_page, build_episode_keyboard

# Majburiy obuna oynasi
from handlers.channels.check import subscription_menu

# Admin panel (agar bo‘lsa)
try:
    from handlers.admin_panel import *
except:
    pass

# Anime qo‘shish, epizod qo‘shish va boshqalar (agar bo‘lsa)
try:
    from handlers.admin_anime import *
except:
    pass


app = Flask(__name__)


# ==========================
#   /start HANDLER
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # start param
    try:
        start_param = message.text.split(" ", 1)[1]
    except:
        start_param = None

    # ADMIN → obuna tekshiruvisiz
    if is_admin(user_id):
        return handle_start_param(message, start_param)

    # VIP → obuna tekshiruvisiz
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

        # DEEP LINK: code_episode (masalan: 4_7)
        if "_" in start_param:
            try:
                code, ep = start_param.split("_")
                return open_episode_from_start(message, int(code), int(ep))
            except:
                pass

        # Faqat kod: "4"
        if start_param.isdigit():
            return open_anime_page(message, int(start_param))

        # anime_4 format
        if start_param.startswith("anime_"):
            try:
                code = int(start_param.replace("anime_", ""))
                return open_anime_page(message, code)
            except:
                pass

    # Oddiy /start — ongoinglar ro‘yxati
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


def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
