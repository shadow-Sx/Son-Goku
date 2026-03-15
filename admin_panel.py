from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("❄ Birlamchi sozlamalar"))
    kb.add(KeyboardButton("📊 Statistika"), KeyboardButton("✉ Xabar Yuborish"))
    kb.add(KeyboardButton("📬 Post tayyorlash"))
    kb.add(KeyboardButton("🎥 Animelar sozlash"), KeyboardButton("💳 Hamyonlar"))
    kb.add(KeyboardButton("🔍 Foydalanuvchini boshqarish"))
    kb.add(KeyboardButton("📢 Kanallar"), KeyboardButton("🎛 Tugmalar"))
    kb.add(KeyboardButton("📄 Matnlar"))
    kb.add(KeyboardButton("📋 Adminlar"), KeyboardButton("🤖 Bot holati"))
    kb.add(KeyboardButton("◀️ Orqaga"))

    return kb
