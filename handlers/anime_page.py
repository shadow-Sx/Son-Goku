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

    # Media yuborish
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
#   QISMLAR RO‘YXATI
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("open_eps_"))
def open_episodes(call):
    code = int(call.data.replace("open_eps_", ""))

    eps = list(db.episodes.find({"anime_code": code}).sort("episode", 1))

    if not eps:
        bot.answer_callback_query(call.id, "❌ Hali qismlar qo‘shilmagan!", show_alert=True)
        return

    kb = InlineKeyboardMarkup()

    # Har bir qism tugmasi
    for ep in eps:
        kb.row(
            InlineKeyboardButton(
                f"📺 {ep['episode']}-qism",
                callback_data=f"ep_{code}_{ep['episode']}"
            )
        )

    # Orqaga tugmasi
    kb.row(
        InlineKeyboardButton("◀️ Orqaga", callback_data=f"back_anime_{code}")
    )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )


# ==========================
#   QISMNI OCHISH (VIDEO)
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("ep_"))
def open_episode(call):
    _, code, ep_num = call.data.split("_")
    code = int(code)
    ep_num = int(ep_num)

    ep = db.episodes.find_one({"anime_code": code, "episode": ep_num})

    if not ep:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi!", show_alert=True)
        return

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("◀️ Qismlar ro‘yxati", callback_data=f"open_eps_{code}")
    )

    bot.send_video(
        call.message.chat.id,
        ep["video_file_id"],
        caption=f"📺 <b>{ep_num}-qism</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

    bot.answer_callback_query(call.id)


# ==========================
#   ANIME SAHIFASIGA QAYTISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("back_anime_"))
def back_to_anime(call):
    code = int(call.data.replace("back_anime_", ""))
    open_anime_page(call.message, code)
    bot.answer_callback_query(call.id)
