from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("❄️ Birlamchi sozlamalar", callback_data="settings")
    )
    kb.row(
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("✉️ Xabar yuborish", callback_data="broadcast")
    )
    kb.row(
        InlineKeyboardButton("📬 Post tayyorlash", callback_data="post")
    )
    kb.row(
        InlineKeyboardButton("🎥 Animelar sozlash", callback_data="anime_menu")
    )
    kb.row(
        InlineKeyboardButton("💳 Hamyonlar", callback_data="wallets")
    )
    kb.row(
        InlineKeyboardButton("🔍 Foydalanuvchini boshqarish", callback_data="users")
    )
    kb.row(
        InlineKeyboardButton("📢 Kanallar", callback_data="channels"),
        InlineKeyboardButton("🎛 Tugmalar", callback_data="buttons"),
        InlineKeyboardButton("📄 Matnlar", callback_data="texts")
    )
    kb.row(
        InlineKeyboardButton("📋 Adminlar", callback_data="admins"),
        InlineKeyboardButton("🤖 Bot holati", callback_data="bot_status")
    )
    return kb
