from loader import bot, db, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   1) Anime kodini qabul qilish
# ==========================
@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("mode") == "auto")
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

    # Qism soni
    episodes = db.episodes.count_documents({"anime_code": code})

    # Avtomatik post matni
    post_text = (
        f"<b>{anime['name']}</b>\n"
        "~~~~~~~~~~~~~~~~~~~~\n"
        f"{anime.get('info', 'Izoh yo‘q')}\n"
        "~~~~~~~~~~~~~~~~~~~~\n"
        f"Qism: {episodes}"
    )

    # Tomosha qilish tugmasi
    watch_button = {
        "text": "🔰 Tomosha qilish 🔰",
        "url": f"https://t.me/{bot.get_me().username}?start={code}"
    }

    # TEMP saqlash
    post_temp[uid] = {
        "mode": "auto",
        "anime_code": code,
        "text": post_text,
        "buttons": [watch_button],
        "channels": []
    }

    # Preview + Kanal tanlashga yo‘naltirish
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("📡 Kanal tanlash", callback_data="post_select_channels"))

    bot.send_message(
        message.chat.id,
        "📨 <b>Avto post tayyor!</b>\nQuyida preview:",
    )

    bot.send_message(
        message.chat.id,
        post_text,
        reply_markup=InlineKeyboardMarkup().row(
            InlineKeyboardButton(watch_button["text"], url=watch_button["url"])
        )
    )

    bot.send_message(
        message.chat.id,
        "Endi postni qaysi kanallarga yuborishni tanlang:",
        reply_markup=kb
    )
