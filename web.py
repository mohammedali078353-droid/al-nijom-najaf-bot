from flask import Flask, jsonify
from main import jobs

app = Flask(__name__)

@app.get("/")
def home():
    return jsonify({
        "status": "نشط ✔",
        "scheduled_posts": len(jobs)
    })

def start_server():
    app.run(host="0.0.0.0", port=5000)
