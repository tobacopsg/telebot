import os
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("🤖 Bot đang hoạt động!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("BOT ĐANG CHẠY...")

    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
