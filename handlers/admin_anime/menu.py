from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, ADMINS
from handlers.admin_panel.menu import big_admin_menu

def anime_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Anime qo‘shish", callback_data="anime_add"))
    kb.row(InlineKeyboardButton("🎞 Qism qo‘shish", callback_data="anime_add_episode"))
    kb.row(InlineKeyboardButton("📚 Anime ro‘yxati", callback_data="anime_list"))
    kb.row(InlineKeyboardButton("✏️ Tahrirlash", callback_data="anime_edit"))
    kb.row(InlineKeyboardButton("🗑 Anime o‘chirish", callback_data="anime_delete"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="anime_back"))
    return kb


@bot.callback_query_handler(func=lambda c: c.data == "anime_menu")
def open_anime_menu(call):
    bot.send_message(call.message.chat.id, "🎥 <b>Animelar sozlash</b>", reply_markup=anime_menu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "anime_back")
def back_to_admin(call):
    bot.send_message(call.message.chat.id, "◀️ Orqaga qaytdingiz", reply_markup=big_admin_menu())
    bot.answer_callback_query(call.id)
