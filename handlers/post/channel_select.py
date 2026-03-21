from loader import bot, db, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_channel_keyboard(uid):
    temp = post_temp.get(uid, {})
    selected = temp.get("channels", [])

    kb = InlineKeyboardMarkup()

    channels = list(db.forced_channels.find())

    for ch in channels:
        ch_id = ch["channel_id"]
        title = ch["title"]

        mark = "✔️" if ch_id in selected else "❌"

        kb.row(
            InlineKeyboardButton(
                f"{mark} {title}",
                callback_data=f"post_ch_toggle:{ch_id}"
            )
        )

    kb.row(
        InlineKeyboardButton("📌 Barchasi", callback_data="post_ch_all"),
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="post_ch_done")
    )

    return kb


@bot.callback_query_handler(func=lambda c: c.data == "post_select_channels")
def post_select_channels(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    kb = build_channel_keyboard(uid)

    bot.send_message(
        call.message.chat.id,
        "📡 <b>Kanal tanlang</b>\n\nQaysi kanallarga yuborilsin?",
        reply_markup=kb
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("post_ch_toggle:"))
def post_channel_toggle(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    ch_id = int(call.data.split(":")[1])

    selected = post_temp[uid].get("channels", [])

    if ch_id in selected:
        selected.remove(ch_id)
    else:
        selected.append(ch_id)

    post_temp[uid]["channels"] = selected

    kb = build_channel_keyboard(uid)

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "post_ch_all")
def post_channel_select_all(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    channels = list(db.forced_channels.find())
    post_temp[uid]["channels"] = [ch["channel_id"] for ch in channels]

    kb = build_channel_keyboard(uid)

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "post_ch_done")
def post_channel_done(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    selected = post_temp[uid].get("channels", [])

    if not selected:
        bot.answer_callback_query(call.id, "❌ Hech qanday kanal tanlanmadi!", show_alert=True)
        return

    from handlers.post.send import send_post_to_channels
    send_post_to_channels(call)

    bot.answer_callback_query(call.id)
