from loader import bot, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   1) Qo‘lda postni qabul qilish
# ==========================
@bot.message_handler(content_types=["text", "photo", "video", "document"])
def manual_post_receive(message):
    uid = message.from_user.id

    temp = post_temp.get(uid)
    if not temp:
        return

    # Faqat manual rejim
    if temp.get("mode") != "manual":
        return

    # Tugma qo‘shish jarayonida postni o‘zgartirmaymiz
    if temp.get("step") in ["btn_text", "btn_url", "btn_edit_text", "btn_edit_url"]:
        return

    if not is_admin(uid):
        return

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
