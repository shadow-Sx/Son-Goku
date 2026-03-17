from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from main import bot, ADMIN_ID

def anime_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Anime qo‘shish", callback_data="anime_add"))
    kb.row(InlineKeyboardButton("🎞 Qism qo‘shish", callback_data="anime_add_episode"))
    kb.row(InlineKeyboardButton("📚 Anime ro‘yxati", callback_data="anime_list"))
    kb.row(InlineKeyboardButton("✏️ Tahrirlash", callback_data="anime_edit"))
    return kb


@bot.callback_query_handler(func=lambda c: c.data == "anime_menu")
def open_anime_menu(call):
    if call.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        call.message.chat.id,
        "🎥 <b>Animelar sozlash bo‘limi</b>",
        reply_markup=anime_menu()
    )
    bot.answer_callback_query(call.id)
