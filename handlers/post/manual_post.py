from loader import bot, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   1) Qo‘lda postni qabul qilish
# ==========================
@bot.message_handler(content_types=["text", "photo", "video", "document"])
def manual_post_receive(message):
    uid = message.from_user.id

    # Faqat manual rejimda ishlaydi
    if post_temp.get(uid, {}).get("mode") != "manual":
        return

    # Tugma qo‘shish jarayonida media qabul qilmaymiz
    if post_temp[uid].get("step") in ["btn_text", "btn_url"]:
        return

    if not is_admin(uid):
        return

    temp = post_temp[uid]

    # ==========================
    #   MATN
    # ==========================
    if message.content_type == "text":
        temp["type"] = "text"
        temp["caption"] = message.text
        temp["file_id"] = None

    # ==========================
    #   RASM
    # ==========================
    elif message.content_type == "photo":
        temp["type"] = "photo"
        temp["file_id"] = message.photo[-1].file_id
        temp["caption"] = message.caption

    # ==========================
    #   VIDEO
    # ==========================
    elif message.content_type == "video":
        temp["type"] = "video"
        temp["file_id"] = message.video.file_id
        temp["caption"] = message.caption

    # ==========================
    #   HUJJAT
    # ==========================
    elif message.content_type == "document":
        temp["type"] = "document"
        temp["file_id"] = message.document.file_id
        temp["caption"] = message.caption

    # TEMP saqlanadi
    post_temp[uid] = temp

    # Preview
    show_manual_preview(message.chat.id, uid)


# ==========================
#   2) Preview + menyu
# ==========================
def show_manual_preview(chat_id, uid):
    temp = post_temp[uid]

    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("➕ Tugma qo‘shish", callback_data="manual_add_button"))
    kb.row(InlineKeyboardButton("🗑 Tugmalarni tozalash", callback_data="manual_clear_buttons"))
    kb.row(InlineKeyboardButton("📡 Yuborish", callback_data="post_select_channels"))

    # Post preview
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

    # Tugmani qo‘shamiz
    post_temp[uid]["buttons"].append({"text": text, "url": url})

    # Step reset
    post_temp[uid]["step"] = None
    post_temp[uid].pop("new_btn_text", None)

    bot.send_message(message.chat.id, "✅ Tugma qo‘shildi!")

    # Preview qayta ko‘rsatamiz
    show_manual_preview(message.chat.id, uid)


# ==========================
#   6) Tugmalarni tozalash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "manual_clear_buttons")
def manual_clear_buttons(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    post_temp[uid]["buttons"] = []

    bot.send_message(call.message.chat.id, "🗑 Barcha tugmalar o‘chirildi!")

    # Preview qayta ko‘rsatamiz
    show_manual_preview(call.message.chat.id, uid)

    bot.answer_callback_query(call.id)
