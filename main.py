import os
from flask import Flask, request
import telebot

from loader import bot, db, ADMIN_ID, is_vip
from admin_menu import admin_panel
from handlers.channels.check import subscription_menu

# HANDLERLARNI ULASH
from handlers.admin_panel import menu as admin_menu
from handlers.admin_anime import menu as anime_menu
from handlers.admin_anime import add_anime
from handlers.admin_anime import add_episode
from handlers.admin_anime import list_anime
from handlers.admin_anime import edit_anime

# VIP boshqaruv
from handlers.user_manage import menu as user_manage_menu
from handlers.user_manage import add_vip
from handlers.user_manage import delete_vip
from handlers.user_manage import list_vip

APP_URL = os.getenv("APP_URL")

app = Flask(__name__)


# ==========================
#   ANIME SAHIFASINI OCHISH
# ==========================
def open_anime_page(message, code):
    anime = db.animes.find_one({"code": int(code)})
    if not anime:
        bot.send_message(message.chat.id, "❌ Anime topilmadi.")
        return

    # Ko‘rishlar +1
    db.views.update_one(
        {"anime_code": int(code)},
        {"$inc": {"views": 1}},
        upsert=True
    )

    views = db.views.find_one({"anime_code": int(code)}).get("views", 0)

    text = f"🎬 <b>{anime['name']}</b>\n\n"
    text += f"{anime['info']}\n\n"
    text += f"🍿 {anime['post_channel']}\n"
    text += f"🔎 Ko‘rishlar: {views}\n"

    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(
        telebot.types.InlineKeyboardButton(
            "📥 YUKLAB OLISH",
            callback_data=f"open_eps_{code}"
        )
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)


# ==========================
#   QISMLAR OYNASI
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("open_eps_"))
def open_episodes(call):
    code = int(call.data.replace("open_eps_", ""))
    episodes = list(db.episodes.find({"anime_code": code}).sort("number", 1))

    if not episodes:
        bot.answer_callback_query(call.id, "❌ Qismlar topilmadi!", show_alert=True)
        return

    kb = telebot.types.InlineKeyboardMarkup()

    row = []
    for ep in episodes:
        row.append(
            telebot.types.InlineKeyboardButton(
                str(ep["number"]),
                callback_data=f"ep_{code}_{ep['number']}"
            )
        )
        if len(row) == 4:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    kb.row(
        telebot.types.InlineKeyboardButton("🔚 Orqaga", callback_data=f"back_{code}"),
        telebot.types.InlineKeyboardButton("❗️ Yopish", callback_data="close_eps"),
        telebot.types.InlineKeyboardButton("Keyingi 🔜", callback_data=f"next_{code}")
    )

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


# ==========================
#   QISMNI OCHISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("ep_"))
def open_episode(call):
    _, code, number = call.data.split("_")
    code = int(code)
    number = int(number)

    ep = db.episodes.find_one({"anime_code": code, "number": number})
    if not ep:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi!", show_alert=True)
        return

    # Video yoki rasm yuborish
    if ep.get("video"):
        bot.send_video(call.message.chat.id, ep["video"], caption=f"{ep['name']}\n{number}-qism")
    elif ep.get("photo"):
        bot.send_photo(call.message.chat.id, ep["photo"], caption=f"{ep['name']}\n{number}-qism")
    else:
        bot.send_message(call.message.chat.id, f"{number}-qism yuklanmagan.")

    bot.answer_callback_query(call.id)


# ==========================
#   YOPISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "close_eps")
def close_eps(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    parts = message.text.split()
    start_param = parts[1] if len(parts) > 1 else None

    # ADMIN
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "👋 Salom, admin!", reply_markup=admin_panel())
        return

    # VIP
    if is_vip(user_id):
        bot.send_message(message.chat.id, "🎉 VIP foydalanuvchi sifatida xush kelibsiz!")
        return

    # Havola orqali kelgan → anime sahifasi
    if start_param and start_param.startswith("anime_"):
        code = start_param.replace("anime_", "")
        return open_anime_page(message, code)

    # Havola orqali kelgan → majburiy obuna
    if start_param == "check":
        channels = list(db.forced_channels.find())
        if channels:
            bot.send_message(
                message.chat.id,
                "📢 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>",
                reply_markup=subscription_menu(user_id, start_param="check")
            )
            return

    # Oddiy /start → Ongoing Animelar
    animes = list(db.animes.find({"status": "Ongoing"}).sort("code", 1))

    if not animes:
        bot.send_message(message.chat.id, "🔥 Hozircha ongoing animelar yo‘q.")
        return

    text = "🔥 <b>Ongoing Animelar</b>\n\n"
    for a in animes:
        text += f"• {a['name']}\n"

    bot.send_message(message.chat.id, text)


# ==========================
#   WEBHOOK
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
