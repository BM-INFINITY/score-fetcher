from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os

app = Flask(__name__)

# ✅ FIX CORS PROPERLY
CORS(app, resources={r"/*": {"origins": "*"}})

MONGO_URI = os.environ.get("MONGO_URI")
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
