import os
import threading
import pytz
from datetime import datetime, timedelta
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup
from admin_menu import admin_panel
from database import db

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
#   ADMIN PANEL
# ==========================
@bot.message_handler(func=lambda m: m.text == "🛠 Boshqarish" and m.from_user.id == ADMIN_ID)
def open_admin(message):
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Admin panel</b>",
        reply_markup=admin_panel()
    )

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
#   KLAVIATURALAR
# ==========================
def confirm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Tasdiqlash", "Bekor qilish")
    return kb

def buttons_choice_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Ha", "O‘tkazib yuborish")
    return kb

def more_media_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➕ Yana media qo‘shish")
    kb.row("➡️ Keyingi bosqich")
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

# ==========================
#   ✉️ XABAR YUBORISH — START
# ==========================
@bot.message_handler(func=lambda m: m.text == "✉️ Xabar yuborish" and m.from_user.id == ADMIN_ID)
def start_broadcast(message):
    broadcast_state[message.from_user.id] = {
        "step": "wait_content",
        "mode": None,          # "forward" yoki "normal"
        "media": [],           # [{"type": "photo", "file_id": "..."} ...]
        "text": None,          # matn (caption yoki alohida)
        "buttons": [],
        "links": [],
        "forward": None
    }
    bot.send_message(
        message.chat.id,
        "✉️ *Menga xabar yuboring*\n\n"
        "Matn, rasm, video, GIF, hujjat, audio, voice yoki forward yuborishingiz mumkin.",
        parse_mode="Markdown"
    )

# ==========================
#   KONTENTNI SAQLASH YORDAMCHISI
# ==========================
def save_content_to_state(message, state):
    # forward bo‘lsa alohida
    if message.forward_from or message.forward_from_chat:
        state["mode"] = "forward"
        state["forward"] = message
        return

    state["mode"] = "normal"

    # captionni matn sifatida saqlash (agar hali text yo‘q bo‘lsa)
    caption = getattr(message, "caption", None)
    if caption and not state["text"]:
        state["text"] = caption

    ct = message.content_type

    if ct == "text":
        state["text"] = message.text

    elif ct == "photo":
        file_id = message.photo[-1].file_id
        state["media"].append({"type": "photo", "file_id": file_id})

    elif ct == "video":
        file_id = message.video.file_id
        state["media"].append({"type": "video", "file_id": file_id})

    elif ct == "animation":
        file_id = message.animation.file_id
        state["media"].append({"type": "animation", "file_id": file_id})

    elif ct == "document":
        file_id = message.document.file_id
        state["media"].append({"type": "document", "file_id": file_id})

    elif ct == "audio":
        file_id = message.audio.file_id
        state["media"].append({"type": "audio", "file_id": file_id})

    elif ct == "voice":
        file_id = message.voice.file_id
        state["media"].append({"type": "voice", "file_id": file_id})

    elif ct == "sticker":
        file_id = message.sticker.file_id
        state["media"].append({"type": "sticker", "file_id": file_id})

# ==========================
#   ✉️ XABAR YUBORISH — HANDLER
# ==========================
@bot.message_handler(func=lambda m: m.from_user.id in broadcast_state)
def broadcast_handler(message):
    state = broadcast_state.get(message.from_user.id)
    if not state:
        return

    step = state["step"]

    # 1) KONTENTNI QABUL QILISH
    if step == "wait_content":
        save_content_to_state(message, state)

        if state["mode"] == "forward":
            state["step"] = "final_confirm"
            bot.send_message(
                message.chat.id,
                "📨 Forward xabar qabul qilindi.\n\n"
                "Haqiqatdan ham shu xabarni yubormoqchimisiz?",
                reply_markup=confirm_keyboard()
            )
            return

        if not state["media"] and not state["text"]:
            bot.send_message(message.chat.id, "❌ Hech qanday kontent topilmadi. Qayta yuboring.")
            return

        state["step"] = "more_media"
        bot.send_message(
            message.chat.id,
            "➕ Yana media qo‘shasizmi yoki keyingi bosqichga o‘tasizmi?",
            reply_markup=more_media_keyboard()
        )
        return

    # 2) YANA MEDIA QO‘SHISH / KEYINGI BOSQICH
    if step == "more_media":
        if message.text == "➕ Yana media qo‘shish":
            state["step"] = "wait_more_media"
            bot.send_message(
                message.chat.id,
                "Yana media yuboring (rasm, video, GIF, hujjat, audio, voice, sticker)."
            )
        elif message.text == "➡️ Keyingi bosqich":
            state["step"] = "ask_buttons"
            bot.send_message(
                message.chat.id,
                "Tugma qo‘shishni xohlaysizmi?",
                reply_markup=buttons_choice_keyboard()
            )
        return

    # 3) YANA MEDIA QABUL QILISH
    if step == "wait_more_media":
        save_content_to_state(message, state)

        if state["mode"] == "forward":
            state["step"] = "final_confirm"
            bot.send_message(
                message.chat.id,
                "📨 Forward xabar qabul qilindi.\n\n"
                "Haqiqatdan ham shu xabarni yubormoqchimisiz?",
                reply_markup=confirm_keyboard()
            )
            return

        if not state["media"] and not state["text"]:
            bot.send_message(message.chat.id, "❌ Hech qanday kontent topilmadi. Qayta yuboring.")
            return

        state["step"] = "more_media"
        bot.send_message(
            message.chat.id,
            "➕ Yana media qo‘shasizmi yoki keyingi bosqichga o‘tasizmi?",
            reply_markup=more_media_keyboard()
        )
        return

    # 4) TUGMA QO‘SHISH YOKI O‘TKAZIB YUBORISH
    if step == "ask_buttons":
        if message.text == "O‘tkazib yuborish":
            state["step"] = "final_confirm"

            preview = build_preview_text(state)
            bot.send_message(
                message.chat.id,
                f"{preview}\n\nHaqiqatdan ham yuborilsinmi?",
                reply_markup=confirm_keyboard()
            )
        elif message.text == "Ha":
            state["step"] = "ask_button_names"
            bot.send_message(
                message.chat.id,
                "Tugmalar nomini yuboring (qator-qator):\n"
                "Masalan:\n"
                "anime, kino\n"
                "mangalar, manhwa"
            )
        return

    # 5) TUGMA NOMLARI
    if step == "ask_button_names":
        rows = message.text.split("\n")
        buttons = []
        for row in rows:
            names = [n.strip() for n in row.split(",") if n.strip()]
            if names:
                buttons.append(names)

        if not buttons:
            bot.send_message(message.chat.id, "❌ Hech qanday tugma topilmadi. Qayta yuboring.")
            return

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

    # 6) HAVOLALAR
    if step == "ask_links":
        rows = message.text.split("\n")
        links = []

        for row in rows:
            row_links = [l.strip() for l in row.split(",") if l.strip()]
            for link in row_links:
                if not link.startswith("https://"):
                    bot.send_message(message.chat.id, "❌ Har bir link 'https://' bilan boshlanishi kerak.")
                    return
            if row_links:
                links.append(row_links)

        if len(links) != len(state["buttons"]):
            bot.send_message(message.chat.id, "❌ Qatorlar soni tugmalar bilan mos emas.")
            return

        for i in range(len(links)):
            if len(links[i]) != len(state["buttons"][i]):
                bot.send_message(message.chat.id, "❌ Tugmalar va havolalar soni mos emas.")
                return

        state["links"] = links
        state["step"] = "final_confirm"

        preview = build_preview_text(state)
        bot.send_message(
            message.chat.id,
            f"{preview}\n\nHaqiqatdan ham yuborilsinmi?",
            reply_markup=confirm_keyboard()
        )
        return

    # 7) YAKUNIY TASDIQLASH
    if step == "final_confirm":
        if message.text == "Bekor qilish":
            broadcast_state.pop(message.from_user.id, None)
            bot.send_message(message.chat.id, "Bekor qilindi.", reply_markup=admin_panel())
            return

        if message.text != "Tasdiqlash":
            return

        # FORWARD REJIMI
        if state["mode"] == "forward" and state["forward"]:
            for user in users.find({}):
                try:
                    bot.forward_message(
                        user["user_id"],
                        state["forward"].chat.id,
                        state["forward"].message_id
                    )
                except:
                    pass
        else:
            # INLINE TUGMALAR
            markup = None
            if state["buttons"]:
                markup = build_inline_keyboard(state["buttons"], state["links"])

            # AVVAL MEDIA(LAR)
            if state["media"]:
                for m in state["media"]:
                    t = m["type"]
                    fid = m["file_id"]
                    for user in users.find({}):
                        try:
                            if t == "photo":
                                bot.send_photo(user["user_id"], fid)
                            elif t == "video":
                                bot.send_video(user["user_id"], fid)
                            elif t == "animation":
                                bot.send_animation(user["user_id"], fid)
                            elif t == "document":
                                bot.send_document(user["user_id"], fid)
                            elif t == "audio":
                                bot.send_audio(user["user_id"], fid)
                            elif t == "voice":
                                bot.send_voice(user["user_id"], fid)
                            elif t == "sticker":
                                bot.send_sticker(user["user_id"], fid)
                        except:
                            pass

            # KEYIN MATN (AGAR BO‘LSA)
            if state["text"]:
                for user in users.find({}):
                    try:
                        bot.send_message(
                            user["user_id"],
                            state["text"],
                            reply_markup=markup
                        )
                    except:
                        pass
            elif markup:
                # Agar faqat tugma bo‘lsa, matnsiz yuborishning ma’nosi yo‘q,
                # shuning uchun bu holatda tugmalarni e’tiborsiz qoldiramiz.
                pass

        bot.send_message(message.chat.id, "Xabar yuborildi!", reply_markup=admin_panel())
        broadcast_state.pop(message.from_user.id, None)

# ==========================
#   PREVIEW YORDAMCHISI
# ==========================
def build_preview_text(state):
    lines = ["📨 Yuboriladigan xabar:\n"]

    if state["mode"] == "forward":
        lines.append("🔁 Forward xabar yuboriladi.\n")
        return "\n".join(lines)

    if state["media"]:
        lines.append(f"📷 Media soni: {len(state['media'])}")
        types = {}
        for m in state["media"]:
            types[m["type"]] = types.get(m["type"], 0) + 1
        for t, c in types.items():
            lines.append(f"   • {t}: {c} ta")
        lines.append("")

    if state["text"]:
        lines.append("📝 Matn:")
        lines.append(state["text"])
        lines.append("")

    if state["buttons"]:
        lines.append("📌 Tugmalar:")
        for btn_row, link_row in zip(state["buttons"], state["links"]):
            row = " | ".join([f"{b} = {l}" for b, l in zip(btn_row, link_row)])
            lines.append(row)

    return "\n".join(lines)

# ==========================
#   POLLING
# ==========================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flaskni alohida thread’da ishga tushiramiz
    threading.Thread(target=run_flask, daemon=True).start()

    # Polling asosiy thread’da ishlaydi
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

