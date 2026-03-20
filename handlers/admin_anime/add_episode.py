from loader import bot, db, ADMINS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

temp_ep = {}

@bot.callback_query_handler(func=lambda c: c.data == "anime_add_episode")
def add_episode_start(call):
    if call.from_user.id != ADMINS:
        return

    temp_ep[call.from_user.id] = {"step": 1}
    bot.send_message(call.message.chat.id, "🎞 Qism qo‘shish\n\nAnime kodini kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: temp_ep.get(m.from_user.id, {}).get("step") == 1)
def add_episode_code(message):
    code = message.text.strip()

    if not code.isdigit():
        bot.send_message(message.chat.id, "❌ Kod faqat raqam bo‘lishi kerak.")
        return

    anime = db.animes.find_one({"code": int(code)})
    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    temp_ep[message.from_user.id] = {"step": 2, "code": int(code)}
    bot.send_message(message.chat.id, "🎥 Qism videosini yuboring (faqat video).")


@bot.message_handler(content_types=["video"])
def add_episode_video(message):
    uid = message.from_user.id

    if temp_ep.get(uid, {}).get("step") != 2:
        return

    code = temp_ep[uid]["code"]
    file_id = message.video.file_id

    last = db.episodes.find_one({"anime_code": code}, sort=[("episode", -1)])
    episode_number = (last["episode"] + 1) if last else 1

    db.episodes.insert_one({
        "anime_code": code,
        "episode": episode_number,
        "video_file_id": file_id
    })

    temp_ep.pop(uid, None)

    # ⭐ TO‘G‘RI HAVOLA
    bot.send_message(
        message.chat.id,
        f"✅ {episode_number}-qism qo‘shildi!\n\n"
        f"🔗 Havola: https://t.me/{bot.get_me().username}?start={code}_{episode_number}"
    )
