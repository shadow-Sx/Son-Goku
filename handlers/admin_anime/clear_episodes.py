from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.admin_anime.edit_anime import edit_temp


# ==========================
#   1) Qismlarni tozalashni boshlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_clear_eps")
def clear_episodes_start(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    code = edit_temp[uid]["code"]
    anime = db.animes.find_one({"code": code})

    if not anime:
        bot.send_message(call.message.chat.id, "❌ Anime topilmadi.")
        return

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🧹 Ha, tozalansin", callback_data=f"clear_yes_{code}"),
        InlineKeyboardButton("❌ Yo‘q", callback_data="clear_no")
    )

    bot.send_message(
        call.message.chat.id,
        f"⚠️ <b>{anime['name']}</b> ning barcha qismlari tozalansinmi?",
        reply_markup=kb
    )
    bot.answer_callback_query(call.id)


# ==========================
#   2) Bekor qilish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "clear_no")
def clear_cancel(call):
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "Tozalash bekor qilindi.")


# ==========================
#   3) Haqiqiy tozalash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("clear_yes_"))
def clear_episodes(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    code = int(call.data.replace("clear_yes_", ""))

    # Faqat epizodlar o‘chiriladi
    db.episodes.delete_many({"anime_code": code})

    bot.answer_callback_query(call.id, "🧹 Tozalandi!", show_alert=True)
    bot.send_message(
        call.message.chat.id,
        f"🧹 <b>{code}</b> kodli anime uchun barcha qismlar tozalandi!"
    )
