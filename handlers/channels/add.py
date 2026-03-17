from loader import bot, db, ADMIN_ID
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

waiting_for_channel = {}

@bot.callback_query_handler(func=lambda c: c.data == "add_channel")
def ask_channel(call):
    if call.from_user.id != ADMIN_ID:
        return

    bot.send_message(call.message.chat.id, "➕ Kanal username yuboring (masalan: @mychannel)")
    waiting_for_channel[call.from_user.id] = True
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_channel)
def save_channel(message):
    uid = message.from_user.id
    username = message.text.strip()

    if not username.startswith("@"):
        bot.send_message(message.chat.id, "❌ Username noto‘g‘ri. Masalan: @mychannel")
        return

    try:
        chat = bot.get_chat(username)
        title = chat.title
    except:
        bot.send_message(message.chat.id, "❌ Kanal topilmadi yoki bot kanalga a'zo emas.")
        return

    db.forced_channels.insert_one({
        "username": username,
        "title": title
    })

    bot.send_message(message.chat.id, f"✅ <b>{title}</b> kanali qo‘shildi!")
    waiting_for_channel.pop(uid)
