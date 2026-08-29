import os
import json
import urllib.request
import urllib.parse
import urllib.error

from flask import Flask, request, jsonify

app = Flask(__name__)

# دریافت Token از Environment Variable
TOKEN = os.environ.get("BALE_BOT_TOKEN")


# =========================
# ارسال پیام به بله
# =========================
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
            response_body = response.read().decode("utf-8")
            result = json.loads(response_body)

            print("Bale sendMessage response:", result)

            return result

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")

        print(
            "Bale sendMessage HTTP ERROR:",
            e.code,
            error_body
        )

        raise

    except Exception as e:
        print(
            "Bale sendMessage ERROR:",
            repr(e)
        )

        raise


# =========================
# صفحه اصلی / تست سلامت
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "bot": "Viraweb Support Assistant",
        "webhook": "active"
    })


# =========================
# Webhook بله
# =========================
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)

    print("Received update:", update)

    # اگر Update معتبر نبود
    if not update:
        return jsonify({
            "ok": True
        })

    # دریافت message
    message = update.get("message")

    if not message:
        return jsonify({
            "ok": True
        })

    # اطلاعات Chat
    chat = message.get("chat")

    if not chat:
        return jsonify({
            "ok": True
        })

    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    print("Chat ID:", chat_id)
    print("User text:", text)

    # =========================
    # دستور /start
    # =========================
    if text == "/start":
        welcome_message = (
            "سلام 👋\n"
            "به دستیار پشتیبان ویراوب خوش اومدی! 🌱\n\n"
            "من اینجام تا درباره دوره‌های ویراوب، "
            "سؤالاتت و نحوه ثبت‌نام کمکت کنم.\n\n"
            "از منوی ربات می‌تونی:\n"
            "🎓 دوره‌ها رو ببینی\n"
            "❓ سؤالات متداول رو بپرسی\n"
            "👨‍💼 با پشتیبان ارتباط بگیری"
        )

        result = send_message(
            chat_id,
            welcome_message
        )

        print("Start message sent:", result)

    # پاسخ به پیام‌های عادی
    else:
        send_message(
            chat_id,
            "پیامت رو دریافت کردم 👌\n"
            "به‌زودی می‌تونم به سؤالاتت درباره ویراوب پاسخ بدم."
        )

    return jsonify({
        "ok": True
    })
