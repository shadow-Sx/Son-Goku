from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.callback_query_handler(func=lambda c: c.data == "list_channels")
def list_channels(call):
    channels = list(db.forced_channels.find())

    if not channels:
        bot.send_message(call.message.chat.id, "📭 Kanallar ro‘yxati bo‘sh.")
        bot.answer_callback_query(call.id)
        return

    kb = InlineKeyboardMarkup()

    for ch in channels:
        kb.row(
            InlineKeyboardButton(
                f"{ch['title']} ({ch['username']})",
                callback_data=f"del_{ch['username']}"
            )
        )

    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="channels"))

    bot.send_message(call.message.chat.id, "📋 <b>Kanallar ro‘yxati</b>", reply_markup=kb)
    bot.answer_callback_query(call.id)
