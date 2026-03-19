from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

EPISODES_PER_PAGE = 12


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
    kb.row(InlineKeyboardButton("📥 YUKLAB OLISH", callback_data=f"eps_{code}_1"))

    if anime["media_type"] == "video":
        bot.send_video(message.chat.id, anime["media_file_id"], caption=caption, reply_markup=kb, parse_mode="HTML")
    else:
        bot.send_photo(message.chat.id, anime["media_file_id"], caption=caption, reply_markup=kb, parse_mode="HTML")


# ==========================
#   QISMLAR RO‘YXATI (SAHIFALI)
# ==========================
def build_episode_keyboard(code, page, current_ep=None):
    eps = list(db.episodes.find({"anime_code": code}).sort("episode", 1))
    total = len(eps)
    total_pages = (total + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE

    start = (page - 1) * EPISODES_PER_PAGE
    end = start + EPISODES_PER_PAGE
    page_eps = eps[start:end]

    kb = InlineKeyboardMarkup()

    row = []
    for ep in page_eps:
        ep_num = ep["episode"]

        # 💽 belgilash
        if current_ep == ep_num:
            text = f"💽 - {ep_num}"
        else:
            text = f"{ep_num}"

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=f"ep_{code}_{ep_num}_{page}"
            )
        )

        if len(row) == 4:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    # Agar 12 yoki kam bo‘lsa → pastki tugmalar yo‘q
    if total <= EPISODES_PER_PAGE:
        return kb

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("🔙 Orqaga", callback_data=f"eps_{code}_{page-1}"))

    nav.append(InlineKeyboardButton("❌ Yopish", callback_data=f"close_eps_{code}"))

    if page < total_pages:
        nav.append(InlineKeyboardButton("Keyingi 🔜", callback_data=f"eps_{code}_{page+1}"))

    kb.row(*nav)
    return kb


@bot.callback_query_handler(func=lambda c: c.data.startswith("eps_"))
def open_episodes(call):
    _, code, page = call.data.split("_")
    code = int(code)
    page = int(page)

    kb = build_episode_keyboard(code, page)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


# ==========================
#   QISMNI OCHISH (VIDEO + belgilash)
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("ep_"))
def open_episode(call):
    _, code, ep_num, page = call.data.split("_")
    code = int(code)
    ep_num = int(ep_num)
    page = int(page)

    anime = db.animes.find_one({"code": code})
    ep = db.episodes.find_one({"anime_code": code, "episode": ep_num})

    caption = (
        f"<b>{anime['name']}</b>\n"
        f"<i>{ep_num}-qism</i>"
    )

    kb = build_episode_keyboard(code, page, current_ep=ep_num)

    bot.send_video(call.message.chat.id, ep["video_file_id"], caption=caption, reply_markup=kb, parse_mode="HTML")

    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass

    bot.answer_callback_query(call.id)


# ==========================
#   YOPISH → Anime sahifasiga qaytish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("close_eps_"))
def close_episodes(call):
    code = int(call.data.replace("close_eps_", ""))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    open_anime_page(call.message, code)
    bot.answer_callback_query(call.id)
