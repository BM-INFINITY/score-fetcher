import requests
import json
import time
import hashlib
import threading
from datetime import datetime
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# 🔗 URLs (AUTO SWITCH innings)
URLS = [
    "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/2417-Innings2.js",
    "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/2417-Innings1.js"
]

CHECK_INTERVAL = 2

# 🔗 MongoDB
MONGO_URI = "mongodb+srv://bhavy:8yOSk1pf5r1XQ6RK@cluster0.optglus.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client["ipl_live"]
collection = db["innings_live"]


# 🔧 Clean JSON
def get_clean_json(text):
    if text.startswith("onScoring("):
        text = text[len("onScoring("):-2]
    return json.loads(text)


# 🔧 Hash (to detect changes)
def get_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


# 🔥 Fetch (SMART SWITCH)
def fetch_data():
    for url in URLS:
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })

            if response.status_code == 200:
                print(f"✅ Using: {url.split('/')[-1]}")
                return get_clean_json(response.text)

        except Exception as e:
            print("❌ Error:", e)

    print("⚠️ No valid innings data found")
    return None


# 💾 Save to Mongo
def save_to_mongo(data):
    try:
        collection.update_one(
            {"matchId": 2417},
            {
                "$set": {
                    "data": data,
                    "lastUpdated": datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"✅ Mongo Updated at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print("❌ Mongo Error:", e)


# 🔄 Background fetch loop
def live_fetcher():
    print("🚀 Live Fetcher Started...\n")
    last_hash = None

    while True:
        data = fetch_data()

        if data:
            current_hash = get_hash(data)

            if current_hash != last_hash:
                print("📡 Change detected! Updating MongoDB...")
                save_to_mongo(data)
                last_hash = current_hash
            else:
                print("⏳ No change...")
        else:
            print("⚠️ No data fetched")

        time.sleep(CHECK_INTERVAL)


# 🌐 API Route
@app.route("/data")
def get_data():
    doc = collection.find_one({"matchId": 2417}, {"_id": 0})
    return jsonify(doc if doc else {})


# 🏠 Home Route
@app.route("/")
def home():
    return "🏏 IPL Live API Running"


# ▶️ Start app
if __name__ == "__main__":
    threading.Thread(target=live_fetcher, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
