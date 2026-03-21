from loader import bot, post_temp, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   TUGMALARNI QATORLARGA BO‘LISH
# ==========================
def build_buttons(buttons):
    kb = InlineKeyboardMarkup()

    row = []
    for btn in buttons:
        row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))

        # Har 2 ta tugmadan keyin yangi qator
        if len(row) == 2:
            kb.row(*row)
            row = []

    # Agar oxirgi qatorda 1 ta tugma qolgan bo‘lsa
    if row:
        kb.row(*row)

    return kb


# ==========================
#   POSTNI YUBORISH
# ==========================
def send_post_to_channels(call):
    uid = call.from_user.id
    chat_id = call.message.chat.id

    if not is_admin(uid):
        return

    temp = post_temp.get(uid)
    if not temp:
        bot.send_message(chat_id, "❌ Post ma'lumotlari topilmadi.")
        return

    channels = temp.get("channels", [])
    if not channels:
        bot.send_message(chat_id, "❌ Hech qanday kanal tanlanmagan.")
        return

    mode = temp.get("mode")
    sent_count = 0

    # ==========================
    #   AVTO REJIM
    # ==========================
    if mode == "auto":
        text = temp["text"]
        buttons = temp["buttons"]
        kb = build_buttons(buttons)

        for ch_id in channels:
            try:
                bot.send_message(ch_id, text, reply_markup=kb)
                sent_count += 1
            except Exception as e:
                print(f"[AUTO] Kanalga yuborilmadi: {ch_id} | {e}")

    # ==========================
    #   QO‘LDA REJIM
    # ==========================
    elif mode == "manual":
        msg_type = temp["type"]
        file_id = temp["file_id"]
        caption = temp.get("caption")
        buttons = temp.get("buttons", [])

        kb = build_buttons(buttons) if buttons else None

        for ch_id in channels:
            try:
                if msg_type == "text":
                    bot.send_message(ch_id, caption, reply_markup=kb)

                elif msg_type == "photo":
                    bot.send_photo(ch_id, file_id, caption=caption, reply_markup=kb)

                elif msg_type == "video":
                    bot.send_video(ch_id, file_id, caption=caption, reply_markup=kb)

                elif msg_type == "document":
                    bot.send_document(ch_id, file_id, caption=caption, reply_markup=kb)

                sent_count += 1

            except Exception as e:
                print(f"[MANUAL] Kanalga yuborilmadi: {ch_id} | {e}")

    # ==========================
    #   YUBORISH TUGADI
    # ==========================
    bot.send_message(
        chat_id,
        f"✅ <b>{sent_count} ta kanalga yuborildi.</b>"
    )

    # TEMP tozalaymiz
    post_temp.pop(uid, None)
