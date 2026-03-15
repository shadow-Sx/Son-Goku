from main import bot

def start_polling():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    start_polling()
