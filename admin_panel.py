from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❄ Birlamchi sozlamalar", callback_data="primary_settings"),
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="stats"),
            InlineKeyboardButton(text="✉ Xabar Yuborish", callback_data="send_msg"),
        ],
        [
            InlineKeyboardButton(text="📬 Post tayyorlash", callback_data="make_post"),
        ],
        [
            InlineKeyboardButton(text="🎥 Animelar sozlash", callback_data="anime_settings"),
            InlineKeyboardButton(text="💳 Hamyonlar", callback_data="wallets"),
        ],
        [
            InlineKeyboardButton(text="🔍 Foydalanuvchini boshqarish", callback_data="user_manage"),
        ],
        [
            InlineKeyboardButton(text="📢 Kanallar", callback_data="channels"),
            InlineKeyboardButton(text="🎛 Tugmalar", callback_data="buttons"),
        ],
        [
            InlineKeyboardButton(text="📄 Matnlar", callback_data="texts"),
        ],
        [
            InlineKeyboardButton(text="📋 Adminlar", callback_data="admins"),
            InlineKeyboardButton(text="🤖 Bot holati", callback_data="bot_status"),
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_admin"),
        ]
    ])
    return kb
