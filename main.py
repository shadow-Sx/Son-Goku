import os
import threading
import pytz
from datetime import datetime, timedelta
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup
from admin_menu import admin_panel
from databaza import db

# ==========================
#   TOKEN VA BOT
# ==========================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7797502113
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==========================
#   DATABASE
# ==========================
users = db["users"]

# ==========================
#   FLASK — UptimeRobot uchun
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ==========================
#   BROADCAST HOLATI
# ==========================
broadcast_state = {}

# ==========================
#   /start
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    is_admin = (message.from_user.id == ADMIN_ID)

    # foydalanuvchini bazaga yozish
    user_id = message.from_user.id
    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "joined": datetime.now(pytz.timezone("Asia/Tashkent"))
        })

    text = (
        "🎥 <b>Ongoing Animelar ro‘yxati</b>\n\n"
        "1) ...\n"
        "2) ...\n"
        "3) ...\n"
    )

    if is_admin:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("🛠 Boshqarish")
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        bot.send_message(message.chat.id, text)

# ==========================
#   ADMIN PANELGA KIRISH
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish" and m.from_user.id == ADMIN_ID)
def open_admin(message):
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Admin panel</b>",
        reply_markup=admin_panel()
    )

# ==========================
#   ADMIN PANELDAN ORQAGA
# ==========================
@bot.message_handler(func=lambda m: m.text == "◀️ Orqaga" and m.from_user.id == ADMIN_ID)
def back_to_user(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛠 Boshqarish")
    bot.send_message(
        message.chat.id,
        "◀️ Asosiy menyuga qaytdingiz.",
        reply_markup=kb
    )

# ==========================
#   📊 STATISTIKA
# ==========================
def get_stats():
    tz = pytz.timezone("Asia/Tashkent")
    now = datetime.now(tz)

    total_users = users.count_documents({})
    today_users = users.count_documents({
        "joined": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}
    })
    week_users = users.count_documents({
        "joined": {"$gte": now - timedelta(days=7)}
    })

    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{total_users}</b>\n"
        f"📅 Bugun qo‘shilganlar: <b>{today_users}</b>\n"
        f"🗓 Oxirgi 7 kunda: <b>{week_users}</b>\n\n"
        f"⏱ Sana va vaqt: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return text

@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID)
def show_stats(message):
    bot.send_message(message.chat.id, get_stats())

# ==========================
#   ✉️ XABAR YUBORISH
# ==========================
def confirm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Tasdiqlash", "Bekor qilish")
    return kb

def buttons_choice_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Ha", "O‘tkazib yuborish")
    return kb

def build_inline_keyboard(button_rows, link_rows):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()

    for btn_row, link_row in zip(button_rows, link_rows):
        row_buttons = []
        for name, link in zip(btn_row, link_row):
            row_buttons.append(InlineKeyboardButton(name, url=link))
        kb.row(*row_buttons)

    return kb

@bot.message_handler(func=lambda m: m.text == "✉️ Xabar yuborish" and m.from_user.id == ADMIN_ID)
def start_broadcast(message):
    broadcast_state[message.from_user.id] = {
        "step": "wait_message",
        "mode": None,
        "text": None,
        "forward": None,
        "buttons": [],
        "links": []
    }
    bot.send_message(message.chat.id, "✉️ *Menga xabar yuboring*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast_handler(message):
    state = broadcast_state.get(message.from_user.id)
    if not state:
        return

    # 1) Xabarni qabul qilish
    if state["step"] == "wait_message":
        if message.forward_from or message.forward_from_chat:
            state["mode"] = "forward"
            state["forward"] = message
            state["step"] = "confirm_forward"
            bot.send_message(
                message.chat.id,
                "📨 Forward xabar qabul qilindi.\nYuborishni tasdiqlaysizmi?",
                reply_markup=confirm_keyboard()
            )
        else:
            state["mode"] = "normal"
            state["text"] = message.text
            state["step"] = "ask_buttons"
            bot.send_message(
                message.chat.id,
                "Tugma qo‘shishni xohlaysizmi?",
                reply_markup=buttons_choice_keyboard()
            )
        return

    # 2) Tugma qo‘shish yoki o‘tkazib yuborish
    if state["step"] == "ask_buttons":
        if message.text == "O‘tkazib yuborish":
            state["step"] = "final_confirm"
            bot.send_message(
                message.chat.id,
                "Haqiqatdan ham shu xabarni yubormoqchimisiz?",
                reply_markup=confirm_keyboard()
            )
        elif message.text == "Ha":
            state["step"] = "ask_button_names"
            bot.send_message(message.chat.id, "Tugmalar nomini yuboring (qator-qator):\nMasalan:\nanime, kino\nmangalar, manhwa")
        return

    # 3) Tugma nomlari
    if state["step"] == "ask_button_names":
        rows = message.text.split("\n")
        buttons = []
        for row in rows:
            names = [n.strip() for n in row.split(",") if n.strip()]
            buttons.append(names)

        state["buttons"] = buttons
        state["step"] = "ask_links"

        bot.send_message(
            message.chat.id,
            "Endi har bir tugma uchun havolalarni yuboring.\n"
            "Tartib tugmalar bilan bir xil bo‘lsin.\n"
            "Masalan:\n"
            "https://link1, https://link2\n"
            "https://link3, https://link4"
        )
        return

    # 4) Havolalar
    if state["step"] == "ask_links":
        rows = message.text.split("\n")
        links = []

        for row in rows:
            row_links = [l.strip() for l in row.split(",") if l.strip()]
            for link in row_links:
                if not link.startswith("https://"):
                    bot.send_message(message.chat.id, "❌ Link 'https://' bilan boshlanishi kerak.")
                    return
            links.append(row_links)

        # tekshirish
        if len(links) != len(state["buttons"]):
            bot.send_message(message.chat.id, "❌ Qatorlar soni tugmalar bilan mos emas.")
            return

        for i in range(len(links)):
            if len(links[i]) != len(state["buttons"][i]):
                bot.send_message(message.chat.id, "❌ Tugmalar va havolalar soni mos emas.")
                return

        state["links"] = links
        state["step"] = "final_confirm"

        # tasdiqlash preview
        preview = ""
        for btn_row, link_row in zip(state["buttons"], state["links"]):
            line = " | ".join([f"{b} = {l}" for b, l in zip(btn_row, link_row)])
            preview += line + "\n"

        bot.send_message(
            message.chat.id,
            f"📌 Tugmalar tayyor:\n\n{preview}\n"
            "Haqiqatdan ham shu xabarni yubormoqchimisiz?",
            reply_markup=confirm_keyboard()
        )
        return

    # 5) Yakuniy tasdiqlash
    if state["step"] == "final_confirm":
        if message.text == "Bekor qilish":
            broadcast_state.pop(message.from_user.id, None)
            bot.send_message(message.chat.id, "Bekor qilindi.", reply_markup=admin_panel())
            return

        # TASDIQLASH
        if state["mode"] == "forward":
            for user in users.find({}):
                try:
                    bot.forward_message(user["user_id"], state["forward"].chat.id, state["forward"].message_id)
                except:
                    pass
        else:
            markup = None
            if state["buttons"]:
                markup = build_inline_keyboard(state["buttons"], state["links"])

            for user in users.find({}):
                try:
                    bot.send_message(user["user_id"], state["text"], reply_markup=markup)
                except:
                    pass

        bot.send_message(message.chat.id, "Xabar yuborildi!", reply_markup=admin_panel())
        broadcast_state.pop(message.from_user.id, None)

# ==========================
#   POLLING
# ==========================
def run_polling():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
