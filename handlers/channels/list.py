from loader import bot, db

@bot.callback_query_handler(func=lambda c: c.data == "list_channels")
def list_channels(call):
    channels = list(db.forced_channels.find())

    if not channels:
        bot.send_message(call.message.chat.id, "📭 Kanallar ro‘yxati bo‘sh.")
        return

    text = "📢 <b>Majburiy obuna kanallari:</b>\n\n"
    for ch in channels:
        text += f"• {ch['title']} — {ch['username']}\n"

    bot.send_message(call.message.chat.id, text)
    bot.answer_callback_query(call.id)
