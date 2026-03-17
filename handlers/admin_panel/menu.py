from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from main import bot, ADMIN_ID
from admin_menu import admin_panel

def big_admin_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❄️ Birlamchi sozlamalar", callback_data="settings"))
    kb.row(
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("✉️ Xabar yuborish", callback_data="broadcast")
    )
    kb.row(InlineKeyboardButton("📬 Post tayyorlash", callback_data="post"))
    kb.row(InlineKeyboardButton("🎥 Animelar sozlash", callback_data="anime_menu"))
    kb.row(InlineKeyboardButton("💳 Hamyonlar", callback_data="wallets"))
    kb.row(InlineKeyboardButton("🔍 Foydalanuvchini boshqarish", callback_data="users"))
    kb.row(
        InlineKeyboardButton("📢 Kanallar", callback_data="channels"),
        InlineKeyboardButton("🎛 Tugmalar", callback_data="buttons"),
        InlineKeyboardButton("📄 Matnlar", callback_data="texts")
    )
    kb.row(
        InlineKeyboardButton("📋 Adminlar", callback_data="admins"),
        InlineKeyboardButton("🤖 Bot holati", callback_data="bot_status")
    )
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="admin_back"))
    return kb


# 🛠 Boshqarish tugmasi
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish" and m.from_user.id == ADMIN_ID)
def open_admin_menu(message):
    bot.send_message(message.chat.id, "🛠 <b>Admin panel</b>", reply_markup=big_admin_menu())


# ◀️ Orqaga → ReplyKeyboard ga qaytish
@bot.callback_query_handler(func=lambda c: c.data == "admin_back")
def close_admin_menu(call):
    bot.send_message(call.message.chat.id, "◀️ Orqaga qaytdingiz", reply_markup=admin_panel())
    bot.answer_callback_query(call.id)
