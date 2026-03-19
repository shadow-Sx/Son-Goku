from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

EPISODES_PER_PAGE = 12   # 4x3 format


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
        InlineKeyboardButton("📥 YUKLAB OLISH", callback_data=f"open_eps_{code}_1")
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
#   QISMLAR RO‘YXATI (SAHIFALI)
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("open_eps_"))
def open_episodes(call):
    _, code, page = call.data.split("_")
    code = int(code)
    page = int(page)

    eps = list(db.episodes.find({"anime_code": code}).sort("episode", 1))

    if not eps:
        bot.answer_callback_query(call.id, "❌ Hali qismlar qo‘shilmagan!", show_alert=True)
        return

    total = len(eps)
    total_pages = (total + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE

    start = (page - 1) * EPISODES_PER_PAGE
    end = start + EPISODES_PER_PAGE
    page_eps = eps[start:end]

    kb = InlineKeyboardMarkup()

    # 4x3 format
    row = []
    for ep in page_eps:
        row.append(
            InlineKeyboardButton(
                f"{ep['episode']}",
                callback_data=f"ep_{code}_{ep['episode']}"
            )
        )
        if len(row) == 4:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    # Pastki tugmalar
    nav_row = []

    # 🔙 Orqaga (oldingi sahifa)
    if page > 1:
        nav_row.append(
            InlineKeyboardButton("🔙 Orqaga", callback_data=f"open_eps_{code}_{page-1}")
        )

    # ❌ Yopish
    nav_row.append(
        InlineKeyboardButton("❌ Yopish", callback_data=f"close_eps_{code}")
    )

    # Keyingi 🔜 (keyingi sahifa)
    if page < total_pages:
        nav_row.append(
            InlineKeyboardButton("Keyingi 🔜", callback_data=f"open_eps_{code}_{page+1}")
        )

    kb.row(*nav_row)

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

    anime = db.animes.find_one({"code": code})
    ep = db.episodes.find_one({"anime_code": code, "episode": ep_num})

    if not ep:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi!", show_alert=True)
        return

    caption = (
        f"<b>{anime['name']}</b>\n"
        f"<i>{ep_num}-qism</i>"
    )

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🔙 Orqaga", callback_data=f"open_eps_{code}_1")
    )
    kb.row(
        InlineKeyboardButton("❌ Yopish", callback_data=f"close_eps_{code}")
    )

    bot.send_video(
        call.message.chat.id,
        ep["video_file_id"],
        caption=caption,
        reply_markup=kb,
        parse_mode="HTML"
    )

    # Eski tugmalarni o‘chiramiz
    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except:
        pass

    bot.answer_callback_query(call.id)


# ==========================
#   YOPISH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("close_eps_"))
def close_episodes(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
