import os
import json
import urllib.request
import urllib.parse
import urllib.error

from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("BALE_BOT_TOKEN")


def send_message(chat_id, text):
    if not TOKEN:
        raise RuntimeError("BALE_BOT_TOKEN is not configured")

    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

            print("Bale response:", result)

            return result

    except urllib.error.HTTPError as e:
        error = e.read().decode("utf-8", errors="replace")
        print("Bale HTTP Error:", e.code, error)
        raise

    except Exception as e:
        print("Bale Error:", repr(e))
        raise


@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "bot": "Viraweb Support Assistant"
    })


@app.route("/", methods=["POST"])
@app.route("/api", methods=["POST"])
@app.route("/api/", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)

    print("Received update:", update)

    if not update:
        return jsonify({"ok": True})

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat")

    if not chat:
        return jsonify({"ok": True})

    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    print("Chat ID:", chat_id)
    print("User text:", text)

    if text == "/start":
        send_message(
            chat_id,
            "سلام 👋\n"
            "به دستیار پشتیبان ویراوب خوش اومدی! 🌱\n\n"
            "من اینجام تا درباره دوره‌های ویراوب، "
            "سؤالاتت و نحوه ثبت‌نام کمکت کنم."
        )

    else:
        send_message(
            chat_id,
            "پیامت رو دریافت کردم 👌\n"
            "به‌زودی می‌تونم به سؤالاتت درباره ویراوب پاسخ بدم."
        )

    return jsonify({"ok": True})
