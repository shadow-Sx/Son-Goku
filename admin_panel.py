from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📊 Statistika"))
    kb.add(KeyboardButton("✉ Xabar yuborish"))
    return kb
