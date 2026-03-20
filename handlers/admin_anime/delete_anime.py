from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.admin_anime.edit_anime import edit_temp


# ==========================
#   1) O‘chirishni boshlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "edit_delete")
def delete_anime_start(call):
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
        InlineKeyboardButton("🗑 Ha, o‘chirilsin", callback_data=f"delete_yes_{code}"),
        InlineKeyboardButton("❌ Yo‘q", callback_data="delete_no")
    )

    bot.send_message(
        call.message.chat.id,
        f"⚠️ <b>{anime['name']}</b> anime o‘chirilsinmi?",
        reply_markup=kb
    )
    bot.answer_callback_query(call.id)


# ==========================
#   2) Bekor qilish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "delete_no")
def delete_cancel(call):
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "O‘chirish bekor qilindi.")


# ==========================
#   3) Haqiqiy o‘chirish
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("delete_yes_"))
def delete_anime(call):
    uid = call.from_user.id
    if not is_admin(uid):
        return

    code = int(call.data.replace("delete_yes_", ""))

    anime = db.animes.find_one({"code": code})
    if not anime:
        bot.send_message(call.message.chat.id, "❌ Anime topilmadi.")
        return

    # Anime o‘chiriladi
    db.animes.delete_one({"code": code})

    # Barcha qismlar ham o‘chiriladi
    db.episodes.delete_many({"anime_code": code})

    bot.answer_callback_query(call.id, "🗑 O‘chirildi!", show_alert=True)
    bot.send_message(
        call.message.chat.id,
        f"🗑 <b>{anime['name']}</b> va uning barcha qismlari o‘chirildi!"
    )
