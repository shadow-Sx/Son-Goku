from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from main import bot, ADMIN_ID
from handlers.admin_panel.menu import big_admin_menu

def anime_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Anime qo‘shish", callback_data="anime_add"))
    kb.row(InlineKeyboardButton("🎞 Qism qo‘shish", callback_data="anime_add_episode"))
    kb.row(InlineKeyboardButton("📚 Anime ro‘yxati", callback_data="anime_list"))
    kb.row(InlineKeyboardButton("✏️ Tahrirlash", callback_data="anime_edit"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="anime_back"))
    return kb


# 🎥 Animelar sozlash → anime menyusi
@bot.callback_query_handler(func=lambda c: c.data == "anime_menu")
def open_anime_menu(call):
    bot.send_message(call.message.chat.id, "🎥 <b>Animelar sozlash</b>", reply_markup=anime_menu())
    bot.answer_callback_query(call.id)


# ◀️ Orqaga → katta admin panelga qaytish
@bot.callback_query_handler(func=lambda c: c.data == "anime_back")
def back_to_admin(call):
    bot.send_message(call.message.chat.id, "◀️ Orqaga qaytdingiz", reply_markup=big_admin_menu())
    bot.answer_callback_query(call.id)
