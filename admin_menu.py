from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛠 Boshqarish"))
    return kb
