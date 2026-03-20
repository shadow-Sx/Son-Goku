from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

ITEMS_PER_PAGE = 50


# ==========================
#   1) Ro‘yxat tugmasi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "anime_list")
def anime_list_start(call):
    if not is_admin(call.from_user.id):
        return

    show_anime_page(call.message.chat.id, 1)
    bot.answer_callback_query(call.id)


# ==========================
#   2) Sahifani chiqarish
# ==========================
def show_anime_page(chat_id, page):
    skip = (page - 1) * ITEMS_PER_PAGE

    total = db.animes.count_documents({})
    animes = list(
        db.animes.find().sort("code", 1).skip(skip).limit(ITEMS_PER_PAGE)
    )

    if not animes:
        bot.send_message(chat_id, "📭 Hozircha hech qanday anime yo‘q.")
        return

    text = "📚 <b>Anime ro‘yxati</b>\n\n"

    for anime in animes:
        code = anime["code"]
        name = anime["name"]
        status = anime["status"]

        text += (
            f"• <b>{name}</b> — ({status})\n"
            f"https://t.me/{bot.get_me().username}?start={code}\n\n"
        )

    kb = InlineKeyboardMarkup()

    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    row = []

    if page > 1:
        row.append(InlineKeyboardButton("◀️ Orqaga", callback_data=f"anime_page_{page-1}"))

    if page < total_pages:
        row.append(InlineKeyboardButton("▶️ Keyingi", callback_data=f"anime_page_{page+1}"))

    if row:
        kb.row(*row)

    bot.send_message(chat_id, text, reply_markup=kb)


# ==========================
#   3) Sahifa tugmalari
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("anime_page_"))
def anime_page_switch(call):
    if not is_admin(call.from_user.id):
        return

    page = int(call.data.split("_")[2])

    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_anime_page(call.message.chat.id, page)

    bot.answer_callback_query(call.id)
