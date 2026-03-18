from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.callback_query_handler(func=lambda c: c.data == "delete_channel")
def delete_channel_menu(call):
    channels = list(db.forced_channels.find())

    if not channels:
        bot.send_message(call.message.chat.id, "📭 Kanallar yo‘q.")
        return

    kb = InlineKeyboardMarkup()

    for ch in channels:
        kb.row(
            InlineKeyboardButton(
                f"🗑 {ch['title']}",
                callback_data=f"delch_{ch['channel_id']}"
            )
        )

    bot.send_message(call.message.chat.id, "🗑 O‘chirish uchun kanalni tanlang:", reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("delch_"))
def delete_channel(call):
    channel_id = int(call.data.replace("delch_", ""))

    db.forced_channels.delete_one({"channel_id": channel_id})

    bot.answer_callback_query(call.id, "🗑 Kanal o‘chirildi!", show_alert=True)
    bot.delete_message(call.message.chat.id, call.message.message_id)
