from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

anime_add_temp = {}


@bot.callback_query_handler(func=lambda c: c.data == "add_anime")
def add_anime_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    anime_add_temp[uid] = {"step": "name"}

    bot.send_message(call.message.chat.id, "🎬 Anime nomini kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: anime_add_temp.get(m.from_user.id, {}).get("step") == "name")
def add_anime_name(message):
    uid = message.from_user.id
    anime_add_temp[uid]["name"] = message.text
    anime_add_temp[uid]["step"] = "info"

    bot.send_message(message.chat.id, "ℹ️ Anime haqida qisqacha info kiriting:")


@bot.message_handler(func=lambda m: anime_add_temp.get(m.from_user.id, {}).get("step") == "info")
def add_anime_info(message):
    uid = message.from_user.id
    anime_add_temp[uid]["info"] = message.text
    anime_add_temp[uid]["step"] = "media"

    bot.send_message(message.chat.id, "📸 Anime uchun rasm yoki video yuboring:")


@bot.message_handler(content_types=["photo", "video"], func=lambda m: anime_add_temp.get(m.from_user.id, {}).get("step") == "media")
def add_anime_media(message):
    uid = message.from_user.id

    if message.content_type == "photo":
        anime_add_temp[uid]["photo_id"] = message.photo[-1].file_id
        anime_add_temp[uid]["video_id"] = None

    elif message.content_type == "video":
        anime_add_temp[uid]["video_id"] = message.video.file_id
        anime_add_temp[uid]["photo_id"] = None

    # Kod generatsiya qilamiz
    last = db.animes.find_one(sort=[("code", -1)])
    code = (last["code"] + 1) if last else 1

    anime_add_temp[uid]["code"] = code

    # DB ga yozamiz
    db.animes.insert_one({
        "code": code,
        "name": anime_add_temp[uid]["name"],
        "info": anime_add_temp[uid]["info"],
        "photo_id": anime_add_temp[uid]["photo_id"],
        "video_id": anime_add_temp[uid]["video_id"]
    })

    bot.send_message(
        message.chat.id,
        f"✅ Anime qo‘shildi!\n\n<b>Kod:</b> {code}\n"
        f"<b>Havola:</b> https://t.me/{bot.get_me().username}?start={code}"
    )

    anime_add_temp.pop(uid, None)
