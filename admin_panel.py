from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📊 Statistika", callback_data="stats"))
    kb.add(InlineKeyboardButton("✉ Xabar yuborish", callback_data="send_msg"))
    # keyin boshqa bo‘limlar qo‘shamiz
    return kb
