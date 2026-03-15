import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID
from database import db

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")


# ============================
# /start — Ongoing Animelar
# ============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    # Ongoing animelarni olish (status != completed)
    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    if not animelist:
        return bot.send_message(msg.chat.id, "Hozircha ongoing animelar mavjud emas.")

    text = "🎥 *Hozirgi Ongoing Animelar:*\n\n"
    i = 1

    for anime in animelist:
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)

        text += f"{i}. {name} ({current}/{total})\n"
        i += 1

    # Inline tugmalar (raqamlar)
    kb = InlineKeyboardMarkup()

    for n in range(1, i):
        kb.add(InlineKeyboardButton(str(n), callback_data=f"anime_{n}"))

    # Admin uchun boshqaruv tugmasi
    if msg.from_user.id == ADMIN_ID:
        kb.add(InlineKeyboardButton("🛠 Boshqarish", callback_data="admin_panel"))

    bot.send_message(msg.chat.id, text, reply_markup=kb)


# ============================
# Inline tugmalar callbacklari
# ============================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    # Admin panelga o'tish
    if data == "admin_panel":
        from admin_panel import admin_panel
        return bot.send_message(call.message.chat.id, "🌸 Admin panel", reply_markup=admin_panel())

    # Anime tanlash
    if data.startswith("anime_"):
        index = int(data.split("_")[1]) - 1

        animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

        if index < 0 or index >= len(animelist):
            return bot.answer_callback_query(call.id, "Xato raqam!")

        anime = animelist[index]

        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)

        bot.send_message(
            call.message.chat.id,
            f"🎬 *{name}*\n\nEpizodlar: {current}/{total}",
            parse_mode="Markdown"
        )

        return bot.answer_callback_query(call.id)

    # Admin panel tugmalari (hozircha bo‘sh)
    bot.answer_callback_query(call.id, "Bu bo‘lim hali qo‘shilmagan.")


# ============================
# 24/7 ishlash
# ============================
bot.infinity_polling(skip_pending=True)
