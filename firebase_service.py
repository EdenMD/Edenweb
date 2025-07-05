import os
import firebase_admin
from firebase_admin import credentials, db

# Set up credentials from Render environment
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token"
})

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    "databaseURL": f"https://{os.getenv('FIREBASE_PROJECT_ID')}.firebaseio.com"
})

# Keep track of milestones already announced
last_milestone = 0

def check_milestone():
    global last_milestone
    ref = db.reference("/members/count")
    count = ref.get()

    if not count:
        return None

    count = int(count)

    # Detect milestone: 1K, 10K, 100K, etc.
    if count >= 1000 and (last_milestone == 0 or count >= last_milestone * 10):
        last_milestone = count
        return f"🎉 Huge news! We just hit *{count}* members in Eden Technology!"

    return None