from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


@bot.message_handler(commands=["start"])
def open_anime_page(message):
    text = message.text.strip()

    # 1) start parametrlari yo‘q → oddiy /start
    if text == "/start":
        return

    # 2) start parametri bor
    param = text.replace("/start", "").strip()

    # /start 5
    if param.isdigit():
        code = int(param)

    # /start anime_5
    elif param.startswith("anime_") and param.replace("anime_", "").isdigit():
        code = int(param.replace("anime_", ""))

    else:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri havola.")
        return

    # Anime topamiz
    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    # Qismlar soni
    episodes = list(db.episodes.find({"anime_code": code}).sort("number", 1))

    # Tugmalar
    kb = InlineKeyboardMarkup()

    # Qismlar tugmalari
    for ep in episodes:
        kb.row(
            InlineKeyboardButton(
                f"{ep['number']} - qism",
                callback_data=f"watch_ep:{code}:{ep['number']}"
            )
        )

    # Anime ma’lumotini chiqaramiz
    caption = (
        f"<b>{anime['name']}</b>\n"
        f"{anime.get('info', '')}\n\n"
        f"Qismlar soni: {len(episodes)}"
    )

    # Rasm bo‘lsa — rasm bilan chiqaramiz
    if anime.get("photo_id"):
        bot.send_photo(
            message.chat.id,
            anime["photo_id"],
            caption=caption,
            reply_markup=kb
        )
    else:
        bot.send_message(
            message.chat.id,
            caption,
            reply_markup=kb
        )
