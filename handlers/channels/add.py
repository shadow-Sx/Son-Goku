from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

waiting_channel = {}

@bot.callback_query_handler(func=lambda c: c.data == "add_channel")
def ask_channel(call):
    bot.send_message(call.message.chat.id, "📢 Kanal username yuboring (masalan: @AniGonUz)")
    waiting_channel[call.from_user.id] = True
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in waiting_channel)
def save_channel(message):
    uid = message.from_user.id
    username = message.text.strip()

    try:
        chat = bot.get_chat(username)
        channel_id = chat.id
        title = chat.title
    except:
        bot.send_message(message.chat.id, "❌ Kanal topilmadi yoki bot admin emas.")
        return

    db.forced_channels.insert_one({
        "username": username,
        "title": title,
        "channel_id": channel_id
    })

    bot.send_message(message.chat.id, f"✅ Kanal qo‘shildi:\n{title}\nID: {channel_id}")
    waiting_channel.pop(uid)
