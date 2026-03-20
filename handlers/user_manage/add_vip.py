from loader import bot, db, ADMINS

waiting_vip = {}

@bot.callback_query_handler(func=lambda c: c.data == "vip_add")
def ask_vip(call):
    if call.from_user.id != ADMINS:
        return

    bot.send_message(call.message.chat.id, "➕ VIP qilish uchun foydalanuvchi ID sini yuboring:")
    waiting_vip[call.from_user.id] = True
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: m.from_user.id in waiting_vip)
def save_vip(message):
    uid = message.from_user.id
    try:
        user_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Foydalanuvchi ID noto‘g‘ri.")
        return

    db.vip_users.insert_one({"user_id": user_id})

    bot.send_message(message.chat.id, f"✅ <b>{user_id}</b> VIP foydalanuvchi sifatida qo‘shildi!")
    waiting_vip.pop(uid)
