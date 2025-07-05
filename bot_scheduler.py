from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from gemini_client import generate_blog
from firebase_service import check_milestone
import datetime
import os
import json
import random

CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FACT_HISTORY_FILE = "messages/fact_history.json"

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
        history.clear()
        unused = facts

    selected = random.choice(unused)
    history.append(selected)

    with open(FACT_HISTORY_FILE, "w") as f:
        json.dump(history, f)

    return selected

def schedule_jobs(app):
    scheduler = BackgroundScheduler()
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    def send_fact():
        fact = get_unique_fact()
        bot.send_message(chat_id=CHAT_ID, text