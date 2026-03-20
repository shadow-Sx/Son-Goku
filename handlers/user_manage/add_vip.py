from loader import bot, db, is_admin
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

vip_temp = {}


# ==========================
#   1) VIP qo‘shishni boshlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data == "vip_add")
def vip_add_start(call):
    if not is_admin(call.from_user.id):
        return

    vip_temp[call.from_user.id] = {"step": 1}

    bot.send_message(
        call.message.chat.id,
        "➕ <b>VIP qo‘shish</b>\n\n"
        "VIPga qo‘shmoqchi bo‘lgan odamning <b>Telegram ID</b> raqamini kiriting.\n\n"
        "<b>Qoidalar:</b>\n"
        "1️⃣ Foydalanuvchi botga hech bo‘lmaganda /start yuborgan bo‘lishi kerak.\n\n"
        "ID raqamni kiriting:"
    )
    bot.answer_callback_query(call.id)


# ==========================
#   2) ID qabul qilish
# ==========================
@bot.message_handler(func=lambda m: vip_temp.get(m.from_user.id, {}).get("step") == 1)
def vip_add_get_id(message):
    admin_id = message.from_user.id

    try:
        user_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ ID faqat raqam bo‘lishi kerak.")
        return

    # Foydalanuvchi /start bosganmi?
    user = db.users.find_one({"user_id": user_id})
    if not user:
        bot.send_message(message.chat.id, "❌ Bu foydalanuvchi botga /start yubormagan.")
        return

    full_name = user.get("full_name", "Noma'lum")

    vip_temp[admin_id] = {
        "step": 2,
        "user_id": user_id,
        "full_name": full_name
    }

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("1 oy", callback_data="vip_1m"),
        InlineKeyboardButton("3 oy", callback_data="vip_3m")
    )
    kb.row(
        InlineKeyboardButton("6 oy", callback_data="vip_6m"),
        InlineKeyboardButton("1 yil", callback_data="vip_12m")
    )

    bot.send_message(
        message.chat.id,
        f"👤 <b>{full_name}</b> uchun VIP yoqmoqchimisiz?\n\n"
        "Kerakli muddatni tanlang:",
        reply_markup=kb
    )


# ==========================
#   3) Muddat tanlash
# ==========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def vip_add_duration(call):
    admin_id = call.from_user.id
    if not is_admin(admin_id):
        return

    if admin_id not in vip_temp:
        bot.answer_callback_query(call.id, "❌ Avval ID kiriting!", show_alert=True)
        return

    data = vip_temp[admin_id]
    user_id = data["user_id"]
    full_name = data["full_name"]

    duration_map = {
        "vip_1m": 30,
        "vip_3m": 90,
        "vip_6m": 180,
        "vip_12m": 365
    }

    days = duration_map[call.data]
    expires_at = int(time.time()) + days * 86400

    db.vip_users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "full_name": full_name,
                "expires_at": expires_at,
                "duration": f"{days} kun",
                "added_by": admin_id
            }
        },
        upsert=True
    )

    # Adminga xabar
    bot.send_message(
        call.message.chat.id,
        f"✅ <b>{full_name}</b> uchun VIP yoqildi!\n"
        f"Muddat: <b>{days} kun</b>"
    )

    # Foydalanuvchiga xabar
    try:
        bot.send_message(
            user_id,
            f"🎉 Sizga <b>{days} kunlik VIP</b> berildi!\n"
            "Botdan bemalol foydalanishingiz mumkin."
        )
    except:
        pass

    vip_temp.pop(admin_id, None)
    bot.answer_callback_query(call.id)
