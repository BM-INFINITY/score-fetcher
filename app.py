from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "your_mongo_url"
client = MongoClient(MONGO_URI)

db = client["ipl_live"]
collection = db["innings_live"]

@app.route("/")
def home():
    return "🏏 IPL API Running"

@app.route("/data")
def get_data():
    doc = collection.find_one({"matchId": 2417}, {"_id": 0})
    return jsonify(doc if doc else {})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
