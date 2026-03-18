from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================
#   ANIME SAHIFASINI OCHISH
# ==========================
def open_anime_page(message, code):
    anime = db.animes.find_one({"code": code})

    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    # Inline tugma: Epizodlar bo‘limi
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📥 YUKLAB OLISH", callback_data=f"open_eps_{code}")
    )

    caption = (
        f"<b>{anime['name']}</b>\n\n"
        f"{anime['info']}\n\n"
        f"👁 1.2K  |  @{anime.get('channel_username','AnimeUz')}"
    )

    # Rasm yoki video chiqarish
    if anime.get("type") == "video":
        bot.send_video(
            message.chat.id,
            anime["file_id"],
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        bot.send_photo(
            message.chat.id,
            anime["file_id"],
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )


# ==========================
#   EPIZODLAR RO‘YXATI
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("open_eps_"))
def open_episodes(call):
    code = int(call.data.replace("open_eps_", ""))

    eps = list(db.episodes.find({"anime_code": code}).sort("ep_number", 1))

    if not eps:
        bot.answer_callback_query(call.id, "❌ Epizodlar hali qo‘shilmagan!", show_alert=True)
        return

    kb = InlineKeyboardMarkup()

    for ep in eps:
        kb.row(
            InlineKeyboardButton(
                f"📺 {ep['ep_number']}-qism",
                callback_data=f"ep_{code}_{ep['ep_number']}"
            )
        )

    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data=f"back_anime_{code}"))

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )


# ==========================
#   EPIZODNI OCHISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("ep_"))
def send_episode(call):
    _, code, ep_number = call.data.split("_")
    code = int(code)
    ep_number = int(ep_number)

    ep = db.episodes.find_one({"anime_code": code, "ep_number": ep_number})

    if not ep:
        bot.answer_callback_query(call.id, "❌ Bu epizod topilmadi!", show_alert=True)
        return

    bot.answer_callback_query(call.id)

    if ep["type"] == "video":
        bot.send_video(call.message.chat.id, ep["file_id"])
    else:
        bot.send_photo(call.message.chat.id, ep["file_id"])


# ==========================
#   ORQAGA QAYTISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("back_anime_"))
def back_to_anime(call):
    code = int(call.data.replace("back_anime_", ""))
    bot.answer_callback_query(call.id)
    open_anime_page(call.message, code)
