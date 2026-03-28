import requests
import json
import time
import hashlib
from datetime import datetime
from pymongo import MongoClient

URLS = [
    "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/2417-Innings2.js",
    "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/2417-Innings1.js"
]

MONGO_URI = "your_mongo_url"
client = MongoClient(MONGO_URI)

db = client["ipl_live"]
collection = db["innings_live"]


def get_clean_json(text):
    if text.startswith("onScoring("):
        text = text[len("onScoring("):-2]
    return json.loads(text)


def get_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def fetch_data():
    for url in URLS:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                print("✅ Using:", url)
                return get_clean_json(res.text)
        except:
            pass
    return None


def save(data):
    collection.update_one(
        {"matchId": 2417},
        {"$set": {"data": data, "lastUpdated": datetime.utcnow()}},
        upsert=True
    )
    print("✅ Updated")


print("🚀 Worker Started...")

last_hash = None

while True:
    data = fetch_data()

    if data:
        h = get_hash(data)
        if h != last_hash:
            save(data)
            last_hash = h
        else:
            print("⏳ No change")

    time.sleep(3)
