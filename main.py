import os
import threading
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

# ==========================
#   FLASK — UptimeRobot uchun
# ==========================
@app.route("/")
def home():
    return "Bot is running!"

# ==========================
#   /start
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "<b>Yangi bot ishlayapti!</b>\n\n"
        "Bu bot 24/7 ishlaydi, polling + Flask bilan."
    )

# ==========================
#   POLLING — fon threadda
# ==========================
def run_polling():
    print(">>> POLLING STARTED <<<")
    bot.infinity_polling(skip_pending=True)

# ==========================
#   RUN SERVER
# ==========================
if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
