from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel():
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("❄ Birlamchi sozlamalar", callback_data="primary_settings"))
    kb.add(
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("✉ Xabar Yuborish", callback_data="send_msg")
    )
    kb.add(InlineKeyboardButton("📬 Post tayyorlash", callback_data="make_post"))
    kb.add(
        InlineKeyboardButton("🎥 Animelar sozlash", callback_data="anime_settings"),
        InlineKeyboardButton("💳 Hamyonlar", callback_data="wallets")
    )
    kb.add(InlineKeyboardButton("🔍 Foydalanuvchini boshqarish", callback_data="user_manage"))
    kb.add(
        InlineKeyboardButton("📢 Kanallar", callback_data="channels"),
        InlineKeyboardButton("🎛 Tugmalar", callback_data="buttons")
    )
    kb.add(InlineKeyboardButton("📄 Matnlar", callback_data="texts"))
    kb.add(
        InlineKeyboardButton("📋 Adminlar", callback_data="admins"),
        InlineKeyboardButton("🤖 Bot holati", callback_data="bot_status")
    )
    kb.add(InlineKeyboardButton("◀️ Orqaga", callback_data="back_admin"))

    return kb
