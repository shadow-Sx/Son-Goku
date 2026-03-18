from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def channels_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Kanal qo‘shish", callback_data="add_channel"))
    kb.row(InlineKeyboardButton("📋 Ro‘yxat", callback_data="list_channels"))
    kb.row(InlineKeyboardButton("🗑 O‘chirish", callback_data="delete_channel"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="admin_back"))
    return kb
