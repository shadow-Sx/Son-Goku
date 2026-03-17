from loader import bot, db

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
def delete_channel(call):
    username = call.data.replace("del_", "")

    db.forced_channels.delete_one({"username": username})

    bot.answer_callback_query(call.id, "🗑 Kanal o‘chirildi!", show_alert=True)
    bot.delete_message(call.message.chat.id, call.message.message_id)
