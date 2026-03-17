from main import bot, ADMIN_ID, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# TEMP DATA
episode_temp = {}


# ==========================
#   1) Qism qo‘shish tugmasi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "anime_add_episode")
def add_episode_start(call):
    if call.from_user.id != ADMIN_ID:
        return

    episode_temp[call.from_user.id] = {"step": 1}

    bot.send_message(call.message.chat.id, "🎞 Qism qo‘shish\n\nAnime kodini kiriting:")
    bot.answer_callback_query(call.id)


# ==========================
#   2) Anime kodini qabul qilish
# ==========================
@bot.message_handler(func=lambda m: episode_temp.get(m.from_user.id, {}).get("step") == 1)
def add_episode_code(message):
    code = message.text.strip()

    # Kod raqam bo‘lishi shart
    if not code.isdigit():
        bot.send_message(message.chat.id, "❌ Kod faqat raqam bo‘lishi kerak.")
        return

    anime = db.animes.find_one({"code": int(code)})

    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday kodli anime topilmadi.")
        return

    # Tempga saqlaymiz
    episode_temp[message.from_user.id] = {
        "step": 2,
        "code": int(code),
        "anime_name": anime["name"]
    }

    bot.send_message(
        message.chat.id,
        f"🎞 <b>Anime: {anime['name']}</b>\n"
        f"KOD: {code}\n\n"
        "Qismlarni yuborishni boshlang.\n"
        "Tugagach <b>/stop</b> deb yozing."
    )


# ==========================
#   3) Qism qabul qilish (faqat video)
# ==========================
@bot.message_handler(content_types=["video"])
def add_episode_video(message):
    data = episode_temp.get(message.from_user.id)

    if not data or data.get("step") != 2:
        return

    code = data["code"]

    # Qism raqamini aniqlaymiz
    last = db.episodes.find_one(
        {"anime_code": code},
        sort=[("episode", -1)]
    )
    episode_number = (last["episode"] + 1) if last else 1

    # DB ga saqlaymiz
    db.episodes.insert_one({
        "anime_code": code,
        "episode": episode_number,
        "video_file_id": message.video.file_id
    })

    # Havola
    link = f"https://t.me/{bot.get_me().username}?start={code}={episode_number}"

    bot.send_message(
        message.chat.id,
        f"🎞 <b>{data['anime_name']}</b>\n"
        f"{episode_number}-qism qo‘shildi!\n\n"
        f"🔗 Havola: {link}"
    )


# ==========================
#   4) /stop — yakunlash
# ==========================
@bot.message_handler(commands=["stop"])
def add_episode_stop(message):
    if message.from_user.id not in episode_temp:
        return

    episode_temp.pop(message.from_user.id, None)

    bot.send_message(
        message.chat.id,
        "✅ Barchasi qo‘shildi!\n"
        "🛠 Admin paneliga qaytdingiz."
    )
