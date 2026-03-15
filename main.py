import telebot
from config import BOT_TOKEN, ADMIN_ID
from user_menu import user_menu
from admin_panel import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# /start
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    bot.send_message(
        msg.chat.id,
        "🌸 Anime botga xush kelibsiz!",
        reply_markup=user_menu(msg.from_user.id)
    )

# 🛠 Boshqarish tugmasi
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish")
def open_admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return bot.send_message(msg.chat.id, "⛔ Siz admin emassiz.")

    bot.send_message(
        msg.chat.id,
        "🌸 Admin panel",
        reply_markup=admin_panel()
    )

# Callbacklar (hozircha bo‘sh)
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data

    if data == "primary_settings":
        bot.answer_callback_query(call.id, "❄ Birlamchi sozlamalar — hali qo‘shilmagan.")
    elif data == "stats":
        bot.answer_callback_query(call.id, "📊 Statistika — hali qo‘shilmagan.")
    elif data == "send_msg":
        bot.answer_callback_query(call.id, "✉ Xabar yuborish — hali qo‘shilmagan.")
    elif data == "make_post":
        bot.answer_callback_query(call.id, "📬 Post tayyorlash — hali qo‘shilmagan.")
    elif data == "anime_settings":
        bot.answer_callback_query(call.id, "🎥 Animelar sozlash — hali qo‘shilmagan.")
    elif data == "wallets":
        bot.answer_callback_query(call.id, "💳 Hamyonlar — hali qo‘shilmagan.")
    elif data == "user_manage":
        bot.answer_callback_query(call.id, "🔍 Foydalanuvchi boshqaruvi — hali qo‘shilmagan.")
    elif data == "channels":
        bot.answer_callback_query(call.id, "📢 Kanallar — hali qo‘shilmagan.")
    elif data == "buttons":
        bot.answer_callback_query(call.id, "🎛 Tugmalar — hali qo‘shilmagan.")
    elif data == "texts":
        bot.answer_callback_query(call.id, "📄 Matnlar — hali qo‘shilmagan.")
    elif data == "admins":
        bot.answer_callback_query(call.id, "📋 Adminlar — hali qo‘shilmagan.")
    elif data == "bot_status":
        bot.answer_callback_query(call.id, "🤖 Bot holati — hali qo‘shilmagan.")
    elif data == "back_admin":
        bot.answer_callback_query(call.id, "◀️ Orqaga — hali qo‘shilmagan.")

bot.infinity_polling()
