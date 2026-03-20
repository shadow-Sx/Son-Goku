from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

edit_temp = {}


# ==========================
#   1) Tahrirlash tugmasi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "anime_edit")
def edit_anime_start(call):
    if not is_admin(call.from_user.id):
        return

    edit_temp[call.from_user.id] = {"step": 1}

    bot.send_message(
        call.message.chat.id,
        "✏️ <b>Tahrirlash</b>\n\nTahrirlamoqchi bo‘lgan Anime kodini kiriting:"
    )
    bot.answer_callback_query(call.id)


# ==========================
#   2) Kodni qabul qilish
# ==========================
@bot.message_handler(func=lambda m: edit_temp.get(m.from_user.id, {}).get("step") == 1)
def edit_anime_code(message):
    code = message.text.strip()

    if not code.isdigit():
        bot.send_message(message.chat.id, "❌ Kod faqat raqam bo‘lishi kerak.")
        return

    anime = db.animes.find_one({"code": int(code)})
    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday kodli anime topilmadi.")
        return

    edit_temp[message.from_user.id] = {
        "step": 2,
        "code": int(code)
    }

    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("📝 Anime nomi", callback_data="edit_name"))
    kb.row(InlineKeyboardButton("🧾 Izoh", callback_data="edit_info"))
    kb.row(InlineKeyboardButton("🔄 Holati", callback_data="edit_status"))
    kb.row(InlineKeyboardButton("🎞 Qism", callback_data="edit_episode"))
    kb.row(InlineKeyboardButton("🗑 Anime o‘chirish", callback_data="edit_delete"))
    kb.row(InlineKeyboardButton("🧹 Qismlarni tozalash", callback_data="edit_clear_eps"))

    bot.send_message(
        message.chat.id,
        f"✏️ <b>{anime['name']}</b>\nHolati: {anime['status']}\n\nTahrirlash bo‘limini tanlang:",
        reply_markup=kb
    )


# ==========================
#   3) Anime nomi tahriri
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_name")
def edit_name_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    edit_temp[uid]["step"] = "edit_name"
    bot.send_message(call.message.chat.id, "📝 Yangi nomni kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: edit_temp.get(m.from_user.id, {}).get("step") == "edit_name")
def edit_name_save(message):
    uid = message.from_user.id
    new_name = message.text

    db.animes.update_one(
        {"code": edit_temp[uid]["code"]},
        {"$set": {"name": new_name}}
    )

    edit_temp[uid]["step"] = 2

    bot.send_message(message.chat.id, "✅ Anime nomi yangilandi!")


# ==========================
#   4) Izoh tahriri
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_info")
def edit_info_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    edit_temp[uid]["step"] = "edit_info"

    bot.send_message(call.message.chat.id, "🧾 Yangi izohni kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: edit_temp.get(m.from_user.id, {}).get("step") == "edit_info")
def edit_info_save(message):
    uid = message.from_user.id

    db.animes.update_one(
        {"code": edit_temp[uid]["code"]},
        {"$set": {"info": message.text}}
    )

    edit_temp[uid]["step"] = 2

    bot.send_message(message.chat.id, "✅ Izoh yangilandi!")


# ==========================
#   5) Holat tahriri
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_status")
def edit_status_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    code = edit_temp[uid]["code"]
    anime = db.animes.find_one({"code": code})

    kb = InlineKeyboardMarkup()
    if anime["status"] == "Ongoing":
        kb.row(InlineKeyboardButton("✔ Tugallangan", callback_data="status_done"))
    else:
        kb.row(InlineKeyboardButton("🔥 Ongoing", callback_data="status_ongoing"))

    bot.send_message(
        call.message.chat.id,
        f"Hozirgi holat: <b>{anime['status']}</b>\nYangi holatni tanlang:",
        reply_markup=kb
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data in ["status_done", "status_ongoing"])
def edit_status_save(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    new_status = "Tugallangan" if call.data == "status_done" else "Ongoing"

    db.animes.update_one(
        {"code": edit_temp[uid]["code"]},
        {"$set": {"status": new_status}}
    )

    edit_temp[uid]["step"] = 2

    bot.send_message(call.message.chat.id, "✅ Holat yangilandi!")
    bot.answer_callback_query(call.id)


# ==========================
#   6) Qism tahriri menyusi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_episode")
def edit_episode_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    edit_temp[uid]["step"] = "episode_number"

    bot.send_message(call.message.chat.id, "🎞 Qaysi qismni tahrirlamoqchisiz? Raqamni yuboring:")
    bot.answer_callback_query(call.id)


# ==========================
#   7) Qism raqamini qabul qilish
# ==========================
@bot.message_handler(func=lambda m: edit_temp.get(m.from_user.id, {}).get("step") == "episode_number")
def edit_episode_number(message):
    uid = message.from_user.id

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Qism raqami faqat raqam bo‘lishi kerak.")
        return

    episode = int(message.text)
    code = edit_temp[uid]["code"]

    ep = db.episodes.find_one({"anime_code": code, "episode": episode})
    if not ep:
        bot.send_message(message.chat.id, "❌ Bunday qism topilmadi.")
        return

    edit_temp[uid]["episode"] = episode
    edit_temp[uid]["step"] = "episode_menu"

    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("📝 Nom qo‘shish", callback_data="ep_name"))
    kb.row(InlineKeyboardButton("❌ O‘chirish", callback_data="ep_delete"))
    kb.row(InlineKeyboardButton("🎥 Videoni almashtirish", callback_data="ep_video"))

    bot.send_message(message.chat.id, "Qism bo‘limini tanlang:", reply_markup=kb)


# ==========================
#   8) Qism — Nom qo‘shish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "ep_name")
def edit_episode_name_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    edit_temp[uid]["step"] = "ep_name"

    bot.send_message(call.message.chat.id, "📝 Yangi nomni kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: edit_temp.get(m.from_user.id, {}).get("step") == "ep_name")
def edit_episode_name_save(message):
    uid = message.from_user.id
    code = edit_temp[uid]["code"]
    episode = edit_temp[uid]["episode"]

    db.episodes.update_one(
        {"anime_code": code, "episode": episode},
        {"$set": {"title": message.text}}
    )

    edit_temp[uid]["step"] = 2

    bot.send_message(message.chat.id, "✅ Qism nomi yangilandi!")


# ==========================
#   9) Qism — O‘chirish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "ep_delete")
def edit_episode_delete(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    code = edit_temp[uid]["code"]
    episode = edit_temp[uid]["episode"]

    db.episodes.delete_one({"anime_code": code, "episode": episode})

    episodes = list(db.episodes.find({"anime_code": code}).sort("episode", 1))

    new_num = 1
    for ep in episodes:
        db.episodes.update_one(
            {"_id": ep["_id"]},
            {"$set": {"episode": new_num}}
        )
        new_num += 1

    edit_temp[uid]["step"] = 2

    bot.send_message(call.message.chat.id, "🗑 Qism o‘chirildi va tartib qayta tiklandi!")
    bot.answer_callback_query(call.id)


# ==========================
#   10) Qism — Videoni almashtirish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "ep_video")
def edit_episode_video_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    edit_temp[uid]["step"] = "ep_video"

    bot.send_message(call.message.chat.id, "🎥 Yangi videoni yuboring:")
    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["video"])
def edit_episode_video_save(message):
    uid = message.from_user.id

    if edit_temp.get(uid, {}).get("step") != "ep_video":
        return

    code = edit_temp[uid]["code"]
    episode = edit_temp[uid]["episode"]

    db.episodes.update_one(
        {"anime_code": code, "episode": episode},
        {"$set": {"video_file_id": message.video.file_id}}
    )

    edit_temp[uid]["step"] = 2

    bot.send_message(message.chat.id, "✅ Video almashtirildi!")
