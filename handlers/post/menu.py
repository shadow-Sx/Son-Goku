from loader import bot, is_admin, post_temp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================
#   POST YUBORISH MENYUSI
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "post_menu")
def post_menu(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    # Admin uchun yangi temp yaratamiz
    post_temp[uid] = {
        "mode": None,
        "type": None,
        "file_id": None,
        "caption": None,
        "buttons": [],
        "channels": [],
        "anime_code": None,
        "step": None
    }

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🤖 Avto", callback_data="post_auto"),
        InlineKeyboardButton("✍️ Qo‘lda", callback_data="post_manual")
    )

    bot.send_message(
        call.message.chat.id,
        "📨 <b>Post yuborish</b>\n\nQaysi tarzda yubormoqchisiz?",
        reply_markup=kb
    )

    bot.answer_callback_query(call.id)


# ==========================
#   AVTO REJIMNI TANLASH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "post_auto")
def post_auto_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    post_temp[uid]["mode"] = "auto"
    post_temp[uid]["step"] = "auto_code"

    bot.send_message(
        call.message.chat.id,
        "🤖 <b>Avto rejim</b>\n\nAnime kodini kiriting:"
    )

    bot.answer_callback_query(call.id)


# ==========================
#   QO‘LDA REJIMNI TANLASH
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "post_manual")
def post_manual_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    post_temp[uid]["mode"] = "manual"
    post_temp[uid]["step"] = None
    post_temp[uid]["buttons"] = []
    post_temp[uid]["channels"] = []

    bot.send_message(
        call.message.chat.id,
        "✍️ <b>Qo‘lda post yaratish</b>\n\n"
        "Postni yuboring (matn, rasm, video yoki hujjat)."
    )

    bot.answer_callback_query(call.id)
