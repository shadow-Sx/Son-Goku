from loader import bot, db

@bot.callback_query_handler(func=lambda c: c.data == "vip_delete")
def vip_delete_menu(call):
    vips = list(db.vip_users.find())

    if not vips:
        bot.send_message(call.message.chat.id, "📭 VIP ro‘yxati bo‘sh.")
        bot.answer_callback_query(call.id)
        return

    kb = InlineKeyboardMarkup()

    for v in vips:
        kb.row(
            InlineKeyboardButton(
                f"🗑 {v['user_id']}",
                callback_data=f"delvip_{v['user_id']}"
            )
        )

    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="users"))

    bot.send_message(call.message.chat.id, "🗑 <b>VIP o‘chirish</b>", reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("delvip_"))
def delete_vip(call):
    user_id = int(call.data.replace("delvip_", ""))

    db.vip_users.delete_one({"user_id": user_id})

    bot.answer_callback_query(call.id, "🗑 VIP o‘chirildi!", show_alert=True)
    bot.delete_message(call.message.chat.id, call.message.message_id)
