import os
import time
from flask import Flask, request
import telebot

from loader import bot, db, is_admin, is_vip, check_vip_expiration, APP_URL

app = Flask(__name__)


# ==========================
#   /start
# ==========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Foydalanuvchini DB ga yozamiz
    db.users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "full_name": message.from_user.full_name,
                "username": message.from_user.username,
                "updated_at": int(time.time())
            },
            "$setOnInsert": {
                "created_at": int(time.time())
            }
        },
        upsert=True
    )

    # VIP muddatini tekshirish
    check_vip_expiration(user_id)

    # Admin bo‘lsa — admin panel
    if is_admin(user_id):
        from admin_menu import admin_panel
        bot.send_message(chat_id, "🛠 Admin panel", reply_markup=admin_panel())
        return

    # VIP foydalanuvchi
    if is_vip(user_id):
        bot.send_message(chat_id, "👑 Siz VIP foydalanuvchisiz.")
        return

    # Oddiy foydalanuvchi
    bot.send_message(chat_id, "Assalomu alaykum!\nAnime ko‘rish uchun botdan foydalaning.")


# ==========================
#   /stop — admin panelga qaytish
# ==========================
@bot.message_handler(commands=["stop"])
def stop(message):
    if is_admin(message.from_user.id):
        from admin_menu import admin_panel
        bot.send_message(message.chat.id, "🛠 Admin panel", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat adminlar uchun.")


# ==========================
#   FLASK ROUTES
# ==========================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{APP_URL}/webhook")
    print("WEBHOOK SET:", f"{APP_URL}/webhook")


# ==========================
#   HANDLER IMPORTLARI
# ==========================

# Anime sahifasi
import anime_page

# Admin panel
from handlers.admin_panel import menu as admin_panel_menu

# Anime boshqaruvi
from handlers.admin_anime import (
    add_anime,
    add_episode,
    edit_anime,
    list_anime,
    menu as anime_menu,
    delete_anime,
    clear_episodes,
)

# Kanal boshqaruvi
from handlers.channels import (
    add as ch_add,
    delete as ch_delete,
    list as ch_list,
    check as ch_check,
    menu as ch_menu,
)

# VIP boshqaruvi
from handlers.user_manage import (
    add_vip,
    delete_vip,
    list_vip,
    menu as user_menu,
)

# POST YUBORISH MODULLARI
from handlers.post import (
    menu,
    auto_post,
    manual_post,
    channel_select,
    send
)


# ==========================
#   ENTRY POINT
# ==========================
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
