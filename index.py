from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Viraweb Bot is alive!"
    })


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    print("Received update:", data)

    return jsonify({
        "ok": True
    })
