import requests
import json
import time
import hashlib
import os
from datetime import datetime
from pymongo import MongoClient
from flask import Flask
import threading

# ================= CONFIG =================

MATCH_ID = 2417

URLS = [
    ("innings1", f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/{MATCH_ID}-Innings1.js"),
    ("innings2", f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/{MATCH_ID}-Innings2.js"),
]

CHECK_INTERVAL = 2  # seconds

# 🔐 Use ENV variable (IMPORTANT)
MONGO_URI = os.getenv("MONGO_URI")

# ================= DB SETUP =================

client = MongoClient(MONGO_URI)
db = client["ipl_live"]
collection = db["live_matches"]

# ================= APP =================

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ IPL Live Bot Running Successfully 🚀"

@app.route("/data")
def get_data():
    data = collection.find_one({"matchId": MATCH_ID}, {"_id": 0})
    return data if data else {"message": "No data yet"}

# ================= CORE LOGIC =================

def get_clean_json(text):
    if text.startswith("onScoring("):
        text = text[len("onScoring("):-2]
    return json.loads(text)


def get_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def fetch_data(url):
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()
        return get_clean_json(response.text)
    except Exception as e:
        print("❌ Fetch error:", e)
        return None


def save_to_mongo(combined_data):
    try:
        collection.update_one(
            {"matchId": MATCH_ID},
            {
                "$set": {
                    "data": combined_data,
                    "lastUpdated": datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"✅ Mongo Updated at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print("❌ Mongo Error:", e)


def worker():
    print("🚀 Live IPL Fetcher Started\n")

    last_hash = None

    while True:
        combined_data = {}

        for name, url in URLS:
            data = fetch_data(url)
            if data:
                combined_data[name] = data

        if combined_data:
            current_hash = get_hash(combined_data)

            if current_hash != last_hash:
                print("📡 Change detected! Updating MongoDB...")
                save_to_mongo(combined_data)
                last_hash = current_hash
            else:
                print("⏳ No change...")

        time.sleep(CHECK_INTERVAL)

# ================= RUN =================

if __name__ == "__main__":
    # Start background worker
    threading.Thread(target=worker).start()

    # Start Flask server (for Heroku web)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
