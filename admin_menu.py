from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    # 1-qator
    kb.add(
        KeyboardButton("❄️ Birlamchi sozlamalar"),
        KeyboardButton("📊 Statistika")
    )

    # 2-qator
    kb.add(
        KeyboardButton("✉️ Xabar Yuborish"),
        KeyboardButton("📬 Post tayyorlash")
    )

    # 3-qator
    kb.add(
        KeyboardButton("🎥 Animelar sozlash"),
        KeyboardButton("💳 Hamyonlar")
    )

    # 4-qator
    kb.add(
        KeyboardButton("🔍 Foydalanuvchini boshqarish"),
        KeyboardButton("📢 Kanallar")
    )

    # 5-qator
    kb.add(
        KeyboardButton("🎛️ Tugmalar"),
        KeyboardButton("📄 Matnlar")
    )

    # 6-qator
    kb.add(
        KeyboardButton("📋 Adminlar"),
        KeyboardButton("🤖 Bot holati")
    )

    # Orqaga
    kb.add(KeyboardButton("◀️ Orqaga"))

    return kb
