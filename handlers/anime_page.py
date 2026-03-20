from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   EPISODE KEYBOARD
# ==========================
def build_episode_keyboard(code, page=1, current_ep=None):
    kb = InlineKeyboardMarkup()

    episodes = list(db.episodes.find({"anime_code": code}).sort("episode", 1))
    total = len(episodes)

    # 12 tadan bo‘lib chiqaramiz
    per_page = 12
    start = (page - 1) * per_page
    end = start + per_page
    page_eps = episodes[start:end]

    row = []
    for ep in page_eps:
        text = f"{ep['episode']}"
        if current_ep == ep["episode"]:
            text = f"▶️ {text}"
        row.append(InlineKeyboardButton(text, callback_data=f"open_ep:{code}:{ep['episode']}"))

        if len(row) == 3:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    # Navigatsiya
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"page:{code}:{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"page:{code}:{page+1}"))

    if nav:
        kb.row(*nav)

    return kb


# ==========================
#   ANIME PAGE OCHISH
# ==========================
def open_anime_page(message, code):
    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(message.chat.id, "❌ Anime topilmadi.")
        return

    text = f"<b>{anime['name']}</b>\n\n{anime.get('description', '')}"

    kb = build_episode_keyboard(code, 1)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=kb,
        parse_mode="HTML"
    )


# ==========================
#   CALLBACK HANDLERLAR
# ==========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("page:"))
def page_handler(call):
    _, code, page = call.data.split(":")
    code = int(code)
    page = int(page)

    kb = build_episode_keyboard(code, page)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("open_ep:"))
def open_episode(call):
    _, code, ep = call.data.split(":")
    code = int(code)
    ep = int(ep)

    anime = db.animes.find_one({"code": code})
    episode = db.episodes.find_one({"anime_code": code, "episode": ep})

    if not anime or not episode:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi.")
        return

    caption = f"<b>{anime['name']}</b>\n<i>{ep}-qism</i>"

    kb = build_episode_keyboard(code, 1, current_ep=ep)

    bot.send_video(
        call.message.chat.id,
        episode["video_file_id"],
        caption=caption,
        reply_markup=kb,
        parse_mode="HTML"
    )
