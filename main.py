import os
import json
import random
import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.background import BackgroundScheduler
from firebase_admin import credentials, db, initialize_app

# --- Load ENV Vars ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")

# --- Firebase Setup ---
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": FIREBASE_PROJECT_ID,
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": FIREBASE_CLIENT_EMAIL,
    "token_uri": "https://oauth2.googleapis.com/token"
})
initialize_app(cred, {"databaseURL": f"https://{FIREBASE_PROJECT_ID}.firebaseio.com"})

last_milestone = 0
FACT_HISTORY_FILE = "messages/fact_history.json"

# --- Utility Functions ---
def load_facts():
    with open("messages/funny_facts.json", "r") as f:
        return json.load(f)

def get_unique_fact():
    facts = load_facts()
    if not os.path.exists(FACT_HISTORY_FILE):
        history = []
    else:
        with open(FACT_HISTORY_FILE, "r") as f:
            history = json.load(f)
    unused = [fact for fact in facts if fact not in history]
    if not unused:
        history = []
        unused = facts
    selected = random.choice(unused)
    history.append(selected)
    with open(FACT_HISTORY_FILE, "w") as f:
        json.dump(history, f)
    return selected

def generate_blog(prompt):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return f"❌ Gemini error {response.status_code}: {response.text}"

def get_greeting(kind):
    with open("messages/greetings.json", "r") as f:
        greetings = json.load(f)
    return greetings.get(kind, "🌞 Hello, Eden!")

def check_milestone():
    global last_milestone
    ref = db.reference("/members/count")
    count = ref.get()
    if count and isinstance(count, int):
        if count >= 1000 and (last_milestone == 0 or count >= last_milestone * 10):
            last_milestone = count
            return f"🎉 Milestone reached! Eden now has {count} members!"
    return None

# --- Scheduler Tasks ---
def schedule_jobs(app):
    bot = Bot(token=TELEGRAM_TOKEN)
    scheduler = BackgroundScheduler()

    scheduler.add_job(lambda: bot.send_message(chat_id=CHAT_ID, text=get_greeting("morning")), 'cron', hour=6)
    scheduler.add_job(lambda: bot.send_message(chat_id=CHAT_ID, text=f"🤣 Funny Fact: {get_unique_fact()}"), 'cron', hour=15)
    scheduler.add_job(lambda: bot.send_message(chat_id=CHAT_ID, text=f"📝 {generate_blog('Eden Technology daily update')}"), 'cron', hour=19)
    scheduler.add_job(lambda: bot.send_message(chat_id=CHAT_ID, text=get_greeting("night")), 'cron', hour=21)
    scheduler.add_job(lambda: announce_milestone(bot), 'interval', minutes=10)

    scheduler.start()

def announce_milestone(bot):
    msg = check_milestone()
    if msg:
        bot.send_message(chat_id=CHAT_ID, text=msg)

# --- App Entry ---
def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise Exception("Missing required environment variables.")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    schedule_jobs(app)
    print("🚀 Eden Technology Bot is live!")
    app.run_polling()

if __name__ == "__main__":
    main()