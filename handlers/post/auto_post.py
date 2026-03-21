from loader import bot, db, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   AVTO REJIM — KOD QABUL QILISH
# ==========================
@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("mode") == "auto"
                               and post_temp.get(m.from_user.id, {}).get("step") == "auto_code")
def auto_post_get_code(message):
    uid = message.from_user.id

    if not is_admin(uid):
        return

    code_text = message.text.strip()
    if not code_text.isdigit():
        bot.send_message(message.chat.id, "❌ Kod faqat raqam bo‘lishi kerak.")
        return

    code = int(code_text)

    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday kodli anime topilmadi.")
        return

    episodes = db.episodes.count_documents({"anime_code": code})

    post_text = (
        f"<b>{anime['name']}</b>\n"
        "~~~~~~~~~~~~~~~~~~~~\n"
        f"{anime.get('info', 'Izoh yo‘q')}\n"
        "~~~~~~~~~~~~~~~~~~~~\n"
        f"Qism: {episodes}"
    )

    watch_button = {
        "text": "🔰 Tomosha qilish 🔰",
        "url": f"https://t.me/{bot.get_me().username}?start={code}"
    }

    post_temp[uid]["anime_code"] = code
    post_temp[uid]["text"] = post_text
    post_temp[uid]["buttons"] = [watch_button]
    post_temp[uid]["channels"] = []
    post_temp[uid]["step"] = None

    kb_next = InlineKeyboardMarkup()
    kb_next.row(
        InlineKeyboardButton("📡 Kanal tanlash", callback_data="post_select_channels")
    )

    # Preview
    kb_preview = InlineKeyboardMarkup()
    kb_preview.row(InlineKeyboardButton(watch_button["text"], url=watch_button["url"]))

    bot.send_message(
        message.chat.id,
        "📨 <b>Avto post tayyor!</b>\nQuyida preview:"
    )

    bot.send_message(
        message.chat.id,
        post_text,
        reply_markup=kb_preview
    )

    bot.send_message(
        message.chat.id,
        "Endi postni qaysi kanallarga yuborishni tanlang:",
        reply_markup=kb_next
    )
