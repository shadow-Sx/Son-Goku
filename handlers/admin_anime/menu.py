from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def anime_menu():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("➕ Anime qo‘shish", callback_data="anime_add")
    )
    kb.row(
        InlineKeyboardButton("🎞 Qism qo‘shish", callback_data="anime_add_episode")
    )
    kb.row(
        InlineKeyboardButton("📚 Anime ro‘yxati", callback_data="anime_list")
    )
    kb.row(
        InlineKeyboardButton("✏️ Tahrirlash", callback_data="anime_edit")
    )
    return kb
