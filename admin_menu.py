from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    # 1-QATOR
    kb.row("❄️ Birlamchi sozlamalar")

    # 2-QATOR
    kb.row("📊 Statistika", "✉️ Xabar yuborish")

    # 3-QATOR
    kb.row("📬 Post tayyorlash")

    # 4-QATOR
    kb.row("🎥 Animelar sozlash", "💳 Hamyonlar")

    # 5-QATOR
    kb.row("🔍 Foydalanuvchini boshqarish")

    # 6-QATOR
    kb.row("📢 Kanallar", "🎛 Tugmalar", "📄 Matnlar")

    # 7-QATOR
    kb.row("📋 Adminlar", "🤖 Bot holati")

    # 8-QATOR
    kb.row("◀️ Orqaga")

    return kb
