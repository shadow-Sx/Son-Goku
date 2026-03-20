from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, ADMINS
from admin_menu import admin_panel

# ==========================
#   KATTA ADMIN PANEL
# ==========================
def big_admin_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❄️ Birlamchi sozlamalar", callback_data="settings"))
    kb.row(
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("✉️ Xabar yuborish", callback_data="broadcast")
    )
    kb.row(InlineKeyboardButton("📬 Post tayyorlash", callback_data="post"))
    kb.row(
        InlineKeyboardButton("🎥 Animelar sozlash", callback_data="anime_menu"),
        InlineKeyboardButton("💳 Hamyonlar", callback_data="wallets")
    )
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


# ==========================
#   🛠 Boshqarish tugmasi
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish" and m.from_user.id == ADMINS)
def open_admin_menu(message):
    bot.send_message(message.chat.id, "🛠 <b>Admin panel</b>", reply_markup=big_admin_menu())


# ==========================
#   ◀️ Orqaga
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "admin_back")
def close_admin_menu(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "◀️ Orqaga qaytdingiz", reply_markup=admin_panel())
    bot.answer_callback_query(call.id)


# ==========================
#   📢 Kanallar bo‘limi
# ==========================
from handlers.channels.menu import channels_menu

@bot.callback_query_handler(func=lambda c: c.data == "channels")
def open_channels(call):
    bot.send_message(call.message.chat.id, "📢 <b>Majburiy obuna kanallari</b>", reply_markup=channels_menu())
    bot.answer_callback_query(call.id)


# ==========================
#   🔍 Foydalanuvchini boshqarish
# ==========================
from handlers.user_manage.menu import user_manage_menu

@bot.callback_query_handler(func=lambda c: c.data == "users")
def open_user_manage(call):
    bot.send_message(call.message.chat.id, "🔍 <b>Foydalanuvchini boshqarish</b>", reply_markup=user_manage_menu())
    bot.answer_callback_query(call.id)


# ==========================
#   FAOL BO‘LMAGAN TUGMALAR
# ==========================
@bot.callback_query_handler(func=lambda c: c.data in [
    "settings", "stats", "broadcast", "post", "wallets",
    "buttons", "texts", "admins", "bot_status"
])
def not_ready(call):
    bot.answer_callback_query(call.id, "❌ Bu bo‘lim hali faol emas!", show_alert=True)
