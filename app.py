from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = "mongodb+srv://bhavy:8yOSk1pf5r1XQ6RK@cluster0.optglus.mongodb.net/?retryWrites=true&w=majority"
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
