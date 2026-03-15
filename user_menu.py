from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_ID

def user_menu(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("🎥 Animelar"))
    kb.add(KeyboardButton("📚 Manga"))

    if user_id == ADMIN_ID:
        kb.add(KeyboardButton("🛠 Boshqarish"))

    return kb
