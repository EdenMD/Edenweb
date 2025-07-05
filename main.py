from telegram.ext import ApplicationBuilder
from bot_scheduler import schedule_jobs
import os

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise Exception("TELEGRAM_BOT_TOKEN not set in environment variables.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    schedule_jobs(app)
    print("🤖 Eden Tech Bot is now running...")
    app.run_polling()

if __name__ == "__main__":
    main()