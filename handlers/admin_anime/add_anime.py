from main import bot, is_admin, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# TEMP DATA (admin uchun vaqtinchalik saqlash)
temp = {}

# ==========================
#   1) Anime qo‘shish tugmasi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "anime_add")
def anime_add_start(call):
    if call.from_user.id != ADMINS:
        return

    temp[call.from_user.id] = {"step": 1}

    bot.send_message(call.message.chat.id, "➕ <b>Anime qo‘shish</b>\n\nAnime nomini kiriting:")
    bot.answer_callback_query(call.id)


# ==========================
#   2) Anime nomi
# ==========================
@bot.message_handler(func=lambda m: temp.get(m.from_user.id, {}).get("step") == 1)
def anime_add_name(message):
    temp[message.from_user.id]["name"] = message.text
    temp[message.from_user.id]["step"] = 2

    bot.send_message(message.chat.id, "📝 Anime haqida izoh yuboring:")


# ==========================
#   3) Anime info
# ==========================
@bot.message_handler(func=lambda m: temp.get(m.from_user.id, {}).get("step") == 2)
def anime_add_info(message):
    temp[message.from_user.id]["info"] = message.text
    temp[message.from_user.id]["step"] = 3

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🔥 Ongoing", callback_data="anime_status_ongoing"),
        InlineKeyboardButton("✔ Tugallangan", callback_data="anime_status_done")
    )

    bot.send_message(message.chat.id, "📌 Anime holatini tanlang:", reply_markup=kb)


# ==========================
#   4) Anime holati
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("anime_status_"))
def anime_add_status(call):
    if call.from_user.id != ADMINS:
        return

    status = "Ongoing" if call.data.endswith("ongoing") else "Tugallangan"
    temp[call.from_user.id]["status"] = status
    temp[call.from_user.id]["step"] = 4

    bot.send_message(call.message.chat.id, "📷 Anime uchun rasm yoki video yuboring:")
    bot.answer_callback_query(call.id)


# ==========================
#   5) Anime media (photo/video)
# ==========================
@bot.message_handler(content_types=["photo", "video"])
def anime_add_media(message):
    if temp.get(message.from_user.id, {}).get("step") != 4:
        return

    data = temp[message.from_user.id]

    # Media type
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    else:
        file_id = message.video.file_id
        media_type = "video"

    # Generate anime code
    last = db.animes.find_one(sort=[("code", -1)])
    code = (last["code"] + 1) if last else 1

    # Save to DB
    db.animes.insert_one({
        "code": code,
        "name": data["name"],
        "info": data["info"],
        "status": data["status"],
        "media_type": media_type,
        "media_file_id": file_id
    })

    # Clear temp
    temp.pop(message.from_user.id, None)

    bot.send_message(
        message.chat.id,
        f"✅ <b>Anime qo‘shildi!</b>\n\n"
        f"📌 Anime kodi: <b>{code}</b>\n"
        f"🔗 Havola: https://t.me/{bot.get_me().username}?start={code}"
    )
