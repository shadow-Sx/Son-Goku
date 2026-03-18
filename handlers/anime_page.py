from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def open_anime_page(message, code):
    anime = db.animes.find_one({"code": code})

    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📥 YUKLAB OLISH", callback_data=f"open_eps_{code}")
    )

    caption = (
        f"<b>{anime['name']}</b>\n\n"
        f"{anime['info']}\n\n"
        f"👁 1.2K  |  @{bot.get_me().username}"
    )

    # ⭐ TO‘G‘RI MAYDON NOMLARI
    media_type = anime["media_type"]
    file_id = anime["media_file_id"]

    if media_type == "video":
        bot.send_video(
            message.chat.id,
            file_id,
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        bot.send_photo(
            message.chat.id,
            file_id,
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
