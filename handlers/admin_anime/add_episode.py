from loader import bot, db, is_admin

episode_temp = {}


@bot.callback_query_handler(func=lambda c: c.data == "add_episode")
def add_episode_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    episode_temp[uid] = {"step": "code"}

    bot.send_message(call.message.chat.id, "🎬 Qaysi animega qism qo‘shmoqchisiz?\nAnime kodini kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: episode_temp.get(m.from_user.id, {}).get("step") == "code")
def add_episode_code(message):
    uid = message.from_user.id
    code = message.text.strip()

    if not code.isdigit():
        bot.send_message(message.chat.id, "❌ Kod faqat raqam bo‘lishi kerak.")
        return

    code = int(code)

    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(message.chat.id, "❌ Bunday anime topilmadi.")
        return

    episode_temp[uid]["anime_code"] = code
    episode_temp[uid]["step"] = "count"

    bot.send_message(message.chat.id, "📌 Nechta qism qo‘shmoqchisiz? (masalan: 12)")


@bot.message_handler(func=lambda m: episode_temp.get(m.from_user.id, {}).get("step") == "count")
def add_episode_count(message):
    uid = message.from_user.id
    count = message.text.strip()

    if not count.isdigit():
        bot.send_message(message.chat.id, "❌ Faqat raqam kiriting.")
        return

    count = int(count)

    episode_temp[uid]["count"] = count
    episode_temp[uid]["videos"] = []
    episode_temp[uid]["step"] = "videos"

    bot.send_message(
        message.chat.id,
        f"🎥 Endi {count} ta videoni ketma-ket tashlang.\n"
        "Bot avtomatik ravishda 1‑qism, 2‑qism, ... qilib saqlaydi."
    )


@bot.message_handler(content_types=["video"], func=lambda m: episode_temp.get(m.from_user.id, {}).get("step") == "videos")
def add_episode_videos(message):
    uid = message.from_user.id
    temp = episode_temp[uid]

    temp["videos"].append(message.video.file_id)

    # Hali hammasi kelmagan bo‘lsa
    if len(temp["videos"]) < temp["count"]:
        bot.send_message(
            message.chat.id,
            f"📥 Qabul qilindi ({len(temp['videos'])}/{temp['count']}). Davom eting..."
        )
        return

    # Hammasi keldi → DB ga yozamiz
    anime_code = temp["anime_code"]

    for i, file_id in enumerate(temp["videos"], start=1):
        db.episodes.insert_one({
            "anime_code": anime_code,
            "number": i,
            "file_id": file_id
        })

    bot.send_message(
        message.chat.id,
        f"✅ {temp['count']} ta qism muvaffaqiyatli qo‘shildi!"
    )

    episode_temp.pop(uid, None)
