import telebot
from config import BOT_TOKEN, ADMIN_ID
from database import db
from admin_menu import admin_panel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ============================
# /start
# ============================
@bot.message_handler(commands=["start"])
def start_cmd(msg):
    db.users.update_one(
        {"user_id": msg.from_user.id},
        {"$setOnInsert": {"user_id": msg.from_user.id, "joined": msg.date}},
        upsert=True
    )

    animelist = list(db.anime.find({"status": {"$ne": "completed"}}))

    text = "🎥 *Hozirgi Ongoing Animelar:*\n\n"
    for i, anime in enumerate(animelist, start=1):
        name = anime.get("name", "Noma'lum")
        current = anime.get("current", 0)
        total = anime.get("total", 0)
        text += f"{i}. {name} ({current}/{total})\n"

    if msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id, text, reply_markup=admin_panel())
    else:
        bot.send_message(msg.chat.id, text)


# ============================
# Qolgan handlerlar o‘z holicha qoladi
# ============================


# ============================
# POLLING
# ============================
if __name__ == "__main__":
    print(">>> POLLING STARTED <<<")
    bot.infinity_polling(skip_pending=True)
