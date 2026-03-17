from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def user_manage_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ VIP qo‘shish", callback_data="vip_add"))
    kb.row(InlineKeyboardButton("🗑 VIP o‘chirish", callback_data="vip_delete"))
    kb.row(InlineKeyboardButton("📋 VIP ro‘yxati", callback_data="vip_list"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="admin_back"))
    return kb
