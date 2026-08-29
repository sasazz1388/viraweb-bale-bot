import os
import json
import urllib.request
import urllib.parse

from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("BALE_BOT_TOKEN")


def send_message(chat_id, text):
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "bot": "Viraweb Support Assistant"
    })


@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)

    if not update:
        return jsonify({"ok": True})

    print("Received update:", update)

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat")
    text = message.get("text", "")

    if not chat:
        return jsonify({"ok": True})

    chat_id = chat.get("id")

    if text == "/start":
        send_message(
            chat_id,
            "سلام 👋\n"
            "به دستیار پشتیبان ویراوب خوش اومدی! 🌱\n\n"
            "من اینجام تا در مورد دوره‌های ویراوب "
            "و سوالاتت کمکت کنم."
        )

    return jsonify({"ok": True})
