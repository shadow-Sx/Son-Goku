from loader import bot, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   1) Qo‘lda postni qabul qilish
# ==========================
@bot.message_handler(content_types=["text", "photo", "video", "document"])
def manual_post_receive(message):
    uid = message.from_user.id

    if post_temp.get(uid, {}).get("mode") != "manual":
        return

    # Tugma qo‘shish / tahrirlash jarayonida postni o‘zgartirmaymiz
    if post_temp[uid].get("step") in ["btn_text", "btn_url", "btn_edit_text", "btn_edit_url"]:
        return

    if not is_admin(uid):
        return

    temp = post_temp[uid]

    if message.content_type == "text":
        temp["type"] = "text"
        temp["caption"] = message.text
        temp["file_id"] = None

    elif message.content_type == "photo":
        temp["type"] = "photo"
        temp["file_id"] = message.photo[-1].file_id
        temp["caption"] = message.caption

    elif message.content_type == "video":
        temp["type"] = "video"
        temp["file_id"] = message.video.file_id
        temp["caption"] = message.caption

    elif message.content_type == "document":
        temp["type"] = "document"
        temp["file_id"] = message.document.file_id
        temp["caption"] = message.caption

    post_temp[uid] = temp

    show_manual_preview(message.chat.id, uid)


# ==========================
#   2) Preview + menyu
# ==========================
def show_manual_preview(chat_id, uid):
    temp = post_temp[uid]

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("➕ Tugma qo‘shish", callback_data="manual_add_button"),
        InlineKeyboardButton("🗂 Tugmalar", callback_data="manual_buttons_menu")
    )
    kb.row(InlineKeyboardButton("📡 Yuborish", callback_data="post_select_channels"))

    if temp["type"] == "text":
        bot.send_message(chat_id, temp["caption"], reply_markup=kb)

    elif temp["type"] == "photo":
        bot.send_photo(chat_id, temp["file_id"], caption=temp["caption"], reply_markup=kb)

    elif temp["type"] == "video":
        bot.send_video(chat_id, temp["file_id"], caption=temp["caption"], reply_markup=kb)

    elif temp["type"] == "document":
        bot.send_document(chat_id, temp["file_id"], caption=temp["caption"], reply_markup=kb)


# ==========================
#   3) Tugma qo‘shishni boshlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "manual_add_button")
def manual_add_button_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    post_temp[uid]["step"] = "btn_text"

    bot.send_message(call.message.chat.id, "📝 Tugma matnini kiriting:")
    bot.answer_callback_query(call.id)


# ==========================
#   4) Tugma matnini qabul qilish
# ==========================
@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("step") == "btn_text")
def manual_button_text(message):
    uid = message.from_user.id

    post_temp[uid]["new_btn_text"] = message.text
    post_temp[uid]["step"] = "btn_url"

    bot.send_message(message.chat.id, "🔗 Tugma URL manzilini kiriting:")


# ==========================
#   5) Tugma URL qabul qilish
# ==========================
@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("step") == "btn_url")
def manual_button_url(message):
    uid = message.from_user.id

    text = post_temp[uid]["new_btn_text"]
    url = message.text

    post_temp[uid]["buttons"].append({"text": text, "url": url})

    post_temp[uid]["step"] = None
    post_temp[uid].pop("new_btn_text", None)

    bot.send_message(message.chat.id, "✅ Tugma qo‘shildi!")

    show_manual_preview(message.chat.id, uid)


# ==========================
#   6) Tugmalar menyusi
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "manual_buttons_menu")
def manual_buttons_menu(call):
    uid = call.from_user.id
    buttons = post_temp[uid].get("buttons", [])

    kb = InlineKeyboardMarkup()

    if not buttons:
        bot.answer_callback_query(call.id, "❌ Tugmalar yo‘q!", show_alert=True)
        return

    for i, btn in enumerate(buttons):
        kb.row(
            InlineKeyboardButton(f"{i+1}. {btn['text']}", callback_data=f"btn_edit:{i}"),
            InlineKeyboardButton("❌", callback_data=f"btn_delete:{i}")
        )

    kb.row(InlineKeyboardButton("⬆️ A‑Z", callback_data="btn_up_all"))
    kb.row(InlineKeyboardButton("⬇️ Z‑A", callback_data="btn_down_all"))
    kb.row(InlineKeyboardButton("◀️ Orqaga", callback_data="btn_back_preview"))

    bot.send_message(call.message.chat.id, "🗂 <b>Tugmalar ro‘yxati</b>", reply_markup=kb)
    bot.answer_callback_query(call.id)


# ==========================
#   7) Tugmani o‘chirish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("btn_delete:"))
def btn_delete(call):
    uid = call.from_user.id
    index = int(call.data.split(":")[1])

    post_temp[uid]["buttons"].pop(index)

    bot.answer_callback_query(call.id, "🗑 O‘chirildi!")
    manual_buttons_menu(call)


# ==========================
#   8) Tugmani tahrirlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("btn_edit:"))
def btn_edit(call):
    uid = call.from_user.id
    index = int(call.data.split(":")[1])

    post_temp[uid]["edit_index"] = index
    post_temp[uid]["step"] = "btn_edit_text"

    bot.send_message(call.message.chat.id, "📝 Yangi tugma matnini kiriting:")
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("step") == "btn_edit_text")
def btn_edit_text(message):
    uid = message.from_user.id

    post_temp[uid]["new_btn_text"] = message.text
    post_temp[uid]["step"] = "btn_edit_url"

    bot.send_message(message.chat.id, "🔗 Yangi URL manzilini kiriting:")


@bot.message_handler(func=lambda m: post_temp.get(m.from_user.id, {}).get("step") == "btn_edit_url")
def btn_edit_url(message):
    uid = message.from_user.id
    index = post_temp[uid]["edit_index"]

    post_temp[uid]["buttons"][index] = {
        "text": post_temp[uid]["new_btn_text"],
        "url": message.text
    }

    post_temp[uid]["step"] = None
    post_temp[uid].pop("new_btn_text", None)
    post_temp[uid].pop("edit_index", None)

    bot.send_message(message.chat.id, "✏️ Tugma tahrirlandi!")

    manual_buttons_menu(message)


# ==========================
#   9) Tugmalarni tartiblash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "btn_up_all")
def btn_up_all(call):
    uid = call.from_user.id
    post_temp[uid]["buttons"] = sorted(post_temp[uid]["buttons"], key=lambda x: x["text"])

    bot.answer_callback_query(call.id, "⬆️ A‑Z tartiblandi!")
    manual_buttons_menu(call)


@bot.callback_query_handler(func=lambda c: c.data == "btn_down_all")
def btn_down_all(call):
    uid = call.from_user.id
    post_temp[uid]["buttons"] = sorted(post_temp[uid]["buttons"], key=lambda x: x["text"], reverse=True)

    bot.answer_callback_query(call.id, "⬇️ Z‑A tartiblandi!")
    manual_buttons_menu(call)


# ==========================
#   10) Orqaga previewga qaytish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "btn_back_preview")
def btn_back_preview(call):
    uid = call.from_user.id
    show_manual_preview(call.message.chat.id, uid)
    bot.answer_callback_query(call.id)
