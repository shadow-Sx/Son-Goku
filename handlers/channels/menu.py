from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def channels_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel"))
    kb.row(InlineKeyboardButton("📋 Kanallar ro‘yxati", callback_data="list_channels"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="admin_back"))
    return kb
