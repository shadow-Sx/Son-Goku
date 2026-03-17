from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🛠 Boshqarish"))
    return kb
