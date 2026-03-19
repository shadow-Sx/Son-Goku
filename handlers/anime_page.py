from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   ANIME SAHIFASI
# ==========================
def open_anime_page(message, code):
    anime = db.animes.find_one({"code": code})

    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    caption = (
        f"<b>{anime['name']}</b>\n\n"
        f"{anime['info']}\n\n"
        f"👁 1.2K  |  @{bot.get_me().username}"
    )

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📥 YUKLAB OLISH", callback_data=f"open_eps_{code}")
    )

    if anime["media_type"] == "video":
        bot.send_video(
            message.chat.id,
            anime["media_file_id"],
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        bot.send_photo(
            message.chat.id,
            anime["media_file_id"],
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )


# ==========================
#   QISMLAR BO‘LIMI
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("open_eps_"))
def open_episodes(call):
    code = int(call.data.replace("open_eps_", ""))

    eps = list(db.episodes.find({"anime_code": code}).sort("episode", 1))

    if not eps:
        bot.answer_callback_query(call.id, "❌ Hali qismlar qo‘shilmagan!", show_alert=True)
        return

    kb = InlineKeyboardMarkup()

    for ep in eps:
        kb.row(
            InlineKeyboardButton(
                f"📺 {ep['episode']}-qism",
                callback_data=f"ep_{code}_{ep['episode']}"
            )
        )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )
