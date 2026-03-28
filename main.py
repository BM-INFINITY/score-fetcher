import requests
import json
import time
import hashlib
from datetime import datetime
from pymongo import MongoClient

# 🔗 IPL URL
URL = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/2417-Innings1.js"

CHECK_INTERVAL = 2  # seconds

# 🔗 MongoDB Connection
MONGO_URI = "mongodb+srv://bhavy:8yOSk1pf5r1XQ6RK@cluster0.optglus.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

# ✅ Create NEW DB (auto created if not exists)
db = client["ipl_live"]   # 👉 new DB name

# ✅ Create collection
collection = db["innings1_live"]


def get_clean_json(text):
    if text.startswith("onScoring("):
        text = text[len("onScoring("):-2]
    return json.loads(text)


def get_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def fetch_data():
    try:
        response = requests.get(URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()
        return get_clean_json(response.text)
    except Exception as e:
        print("❌ Fetch error:", e)
        return None


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


def main():
    print("🚀 Live IPL Fetcher Started (Render Ready)\n")

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

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
