import os
import random
from loader import bot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   Majburiy obuna oynasi
# ==========================
def subscription_menu(user_id, start_param="check"):
    channels = list(db.forced_channels.find())
    random.shuffle(channels)

    kb = InlineKeyboardMarkup()

    # Har bir kanal uchun URL tugma
    for ch in channels:
        kb.row(
            InlineKeyboardButton(
                f"📢 {ch['title']}",
                url=f"https://t.me/{ch['username'].replace('@','')}"
            )
        )

    # Tekshirish tugmasi URL bo‘ladi
    bot_username = os.getenv("BOT_USERNAME")
    kb.row(
        InlineKeyboardButton(
            "✅ Tekshirish",
            url=f"https://t.me/{bot_username}?start={start_param}"
        )
    )

    return kb


# ==========================
#   Obunani tekshirish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    user_id = call.from_user.id
    channels = list(db.forced_channels.find())

    not_joined = []

    for ch in channels:
        channel_id = ch["channel_id"]  # ⭐ ID orqali tekshiramiz

        try:
            member = bot.get_chat_member(channel_id, user_id)

            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(ch)

        except:
            not_joined.append(ch)

    if not_joined:
        bot.answer_callback_query(call.id, "❌ Hali barcha kanallarga obuna bo‘lmadingiz!", show_alert=True)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=subscription_menu(user_id, start_param="check")
        )
        return

    bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!", show_alert=True)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "🎉 Siz botdan foydalanishingiz mumkin!")
