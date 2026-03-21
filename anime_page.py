from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   ANIME SAHIFASINI CHIQARISH
# ==========================
def send_anime_page(chat_id: int, code: int):
    # Anime topamiz
    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(chat_id, "❌ Bunday anime topilmadi.")
        return

    # Qismlar
    episodes = list(db.episodes.find({"anime_code": code}).sort("number", 1))

    kb = InlineKeyboardMarkup()
    for ep in episodes:
        kb.row(
            InlineKeyboardButton(
                f"{ep['number']} - qism",
                callback_data=f"watch_ep:{code}:{ep['number']}"
            )
        )

    caption = (
        f"<b>{anime['name']}</b>\n"
        f"{anime.get('info', '')}\n\n"
        f"Qismlar soni: {len(episodes)}"
    )

    # Rasm bo‘lsa rasm bilan chiqaramiz
    if anime.get("photo_id"):
        bot.send_photo(chat_id, anime["photo_id"], caption=caption, reply_markup=kb)
    else:
        bot.send_message(chat_id, caption, reply_markup=kb)


# ==========================
#   QISMNI OCHISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("watch_ep:"))
def open_episode(call):
    _, code, number = call.data.split(":")
    code = int(code)
    number = int(number)

    ep = db.episodes.find_one({"anime_code": code, "number": number})
    if not ep:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi!", show_alert=True)
        return

    bot.send_video(
        call.message.chat.id,
        ep["file_id"],
        caption=f"{number}-qism"
    )

    bot.answer_callback_query(call.id)
