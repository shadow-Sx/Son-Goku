from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.callback_query_handler(func=lambda c: c.data == "vip_list")
def vip_list(call):
    vips = list(db.vip_users.find())

    if not vips:
        bot.send_message(call.message.chat.id, "📭 VIP ro‘yxati bo‘sh.")
        bot.answer_callback_query(call.id)
        return

    text = "📋 <b>VIP foydalanuvchilar</b>\n\n"
    for v in vips:
        text += f"• {v['user_id']}\n"

    bot.send_message(call.message.chat.id, text)
    bot.answer_callback_query(call.id)
