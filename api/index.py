import os
import json
import re
import urllib.request
import urllib.parse
import urllib.error

from flask import Flask, request, jsonify


# =========================================================
# APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.environ.get("BALE_BOT_TOKEN")

SUPPORT_USERNAME = os.environ.get(
    "SUPPORT_USERNAME",
    "@viraweb_support"
)

COURSE_LINK = os.environ.get(
    "COURSE_LINK",
    "https://example.com/course"
)


# =========================================================
# BALE API
# =========================================================

def bale_api(method, data=None):
    """
    ارسال درخواست به Bale Bot API
    """

    if not TOKEN:
        raise RuntimeError(
            "BALE_BOT_TOKEN environment variable is not configured."
        )

    url = f"https://tapi.bale.ai/bot{TOKEN}/{method}"

    if data:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")

        request_obj = urllib.request.Request(
            url,
            data=encoded_data,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
    else:
        request_obj = urllib.request.Request(
            url,
            method="GET"
        )

    try:

        with urllib.request.urlopen(
            request_obj,
            timeout=15
        ) as response:

            response_text = response.read().decode("utf-8")

            result = json.loads(response_text)

            print(
                f"Bale API [{method}] response:",
                result
            )

            return result

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print(
            f"Bale API HTTP ERROR [{method}]:",
            error.code,
            error_body
        )

        raise

    except Exception as error:

        print(
            f"Bale API ERROR [{method}]:",
            repr(error)
        )

        raise


# =========================================================
# SEND MESSAGE
# =========================================================

def send_message(
    chat_id,
    text,
    reply_markup=None
):

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(
            reply_markup,
            ensure_ascii=False
        )

    return bale_api(
        "sendMessage",
        data
    )


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():

    return {
        "inline_keyboard": [

            [
                {
                    "text": "🎓 مشاهده دوره‌ها",
                    "callback_data": "courses"
                }
            ],

            [
                {
                    "text": "❓ سوالات متداول",
                    "callback_data": "faq"
                }
            ],

            [
                {
                    "text": "👨‍💼 ارتباط با پشتیبان",
                    "callback_data": "support"
                }
            ],

            [
                {
                    "text": "📱 دریافت لینک دوره",
                    "callback_data": "get_link"
                }
            ]

        ]
    }


# =========================================================
# COURSES MENU
# =========================================================

def courses_menu():

    return {
        "inline_keyboard": [

            [
                {
                    "text": "📚 معرفی دوره",
                    "callback_data": "course_intro"
                }
            ],

            [
                {
                    "text": "🔗 دریافت لینک دوره",
                    "callback_data": "get_link"
                }
            ],

            [
                {
                    "text": "⬅️ بازگشت",
                    "callback_data": "home"
                }
            ]

        ]
    }


# =========================================================
# FAQ MENU
# =========================================================

def faq_menu():

    return {
        "inline_keyboard": [

            [
                {
                    "text": "💰 قیمت دوره",
                    "callback_data": "faq_price"
                }
            ],

            [
                {
                    "text": "⏱ مدت دوره",
                    "callback_data": "faq_duration"
                }
            ],

            [
                {
                    "text": "🎓 مناسب چه کسانی است؟",
                    "callback_data": "faq_target"
                }
            ],

            [
                {
                    "text": "📜 مدرک دوره",
                    "callback_data": "faq_certificate"
                }
            ],

            [
                {
                    "text": "👨‍💼 سوال دیگری دارم",
                    "callback_data": "support"
                }
            ],

            [
                {
                    "text": "⬅️ بازگشت",
                    "callback_data": "home"
                }
            ]

        ]
    }


# =========================================================
# WELCOME
# =========================================================

WELCOME_TEXT = """
سلام 👋

به **دستیار پشتیبان ویراوب** خوش اومدی! 🌱

من اینجام تا در مورد دوره‌های ویراوب، نحوه ثبت‌نام و سوالاتت کمکت کنم.

از منوی زیر انتخاب کن 👇
"""


# =========================================================
# COURSE PRESENTATION
# =========================================================

COURSE_INTRO_TEXT = """
🎓 **دوره‌های ویراوب**

اگر دنبال یادگیری مهارت‌های کاربردی و قابل استفاده در دنیای واقعی هستی، دوره‌های ویراوب برای همین طراحی شدن.

در دوره‌ها تلاش می‌کنیم مطالب به شکل ساده، کاربردی و مرحله‌به‌مرحله ارائه بشن.

✨ مزایای دوره:

• آموزش کاربردی
• مسیر یادگیری مرحله‌به‌مرحله
• مناسب برای شروع و پیشرفت
• پشتیبانی و راهنمایی
• دسترسی به محتوای دوره

برای دریافت اطلاعات بیشتر یا لینک دوره، از گزینه‌های زیر استفاده کن 👇
"""


# =========================================================
# FAQ ANSWERS
# =========================================================

FAQ_ANSWERS = {

    "faq_price": """
💰 **قیمت دوره**

برای اطلاع از قیمت و شرایط ثبت‌نام، روی گزینه دریافت لینک دوره بزن تا اطلاعات دوره برایت ارسال شود.
""",

    "faq_duration": """
⏱ **مدت دوره**

مدت دوره بر اساس محتوای آموزشی و مسیر یادگیری آن مشخص شده است.

اگر درباره مدت دقیق یک دوره سوال داری، می‌توانی با پشتیبان ارتباط بگیری.
""",

    "faq_target": """
🎓 **این دوره برای چه کسانی مناسب است؟**

دوره‌ها برای افرادی طراحی شده‌اند که می‌خواهند مهارت موردنظر را به شکل کاربردی و مرحله‌به‌مرحله یاد بگیرند.

اگر سطح فعلی خودت را بگویی، پشتیبان می‌تواند بهتر راهنمایی‌ات کند.
""",

    "faq_certificate": """
📜 **مدرک دوره**

برای اطلاع از شرایط دریافت مدرک هر دوره، با پشتیبان ویراوب در ارتباط باش.
"""
}


# =========================================================
# SIMPLE TEXT FAQ
# =========================================================

def detect_faq(text):

    text = text.lower().strip()

    price_words = [
        "قیمت",
        "هزینه",
        "شهریه",
        "چنده",
        "چند"
    ]

    duration_words = [
        "مدت",
        "چقدر طول",
        "چند ساعت",
        "زمان دوره"
    ]

    target_words = [
        "مناسب",
        "برای چه کسی",
        "برای کی",
        "سطح",
        "مبتدی"
    ]

    certificate_words = [
        "مدرک",
        "گواهی",
        "سرتیفیکیت"
    ]

    if any(word in text for word in price_words):
        return "faq_price"

    if any(word in text for word in duration_words):
        return "faq_duration"

    if any(word in text for word in target_words):
        return "faq_target"

    if any(word in text for word in certificate_words):
        return "faq_certificate"

    return None


# =========================================================
# PHONE NUMBER
# =========================================================

def normalize_phone(text):

    text = text.strip()

    # تبدیل اعداد فارسی و عربی به انگلیسی
    translation = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    text = text.translate(translation)

    # حذف فاصله، خط تیره و پرانتز
    clean = re.sub(
        r"[\s\-\(\)]",
        "",
        text
    )

    # فرمت‌های رایج شماره ایران
    if re.fullmatch(r"09\d{9}", clean):
        return clean

    if re.fullmatch(r"\+989\d{9}", clean):
        return "0" + clean[3:]

    if re.fullmatch(r"00989\d{9}", clean):
        return "0" + clean[4:]

    return None


# =========================================================
# CALLBACK HANDLER
# =========================================================

def handle_callback(chat_id, callback_data):

    if callback_data == "home":

        send_message(
            chat_id,
            WELCOME_TEXT,
            main_menu()
        )

        return


    if callback_data == "courses":

        send_message(
            chat_id,
            "🎓 دوره‌های ویراوب\n\n"
            "برای مشاهده معرفی دوره و دریافت لینک، "
            "یکی از گزینه‌های زیر را انتخاب کن:",
            courses_menu()
        )

        return


    if callback_data == "course_intro":

        send_message(
            chat_id,
            COURSE_INTRO_TEXT,
            courses_menu()
        )

        return


    if callback_data == "faq":

        send_message(
            chat_id,
            "❓ سوالات متداول\n\n"
            "سوالت رو انتخاب کن:",
            faq_menu()
        )

        return


    if callback_data in FAQ_ANSWERS:

        send_message(
            chat_id,
            FAQ_ANSWERS[callback_data],
            faq_menu()
        )

        return


    if callback_data == "support":

        send_message(
            chat_id,
            "👨‍💼 **ارتباط با پشتیبان**\n\n"
            "اگر سوالت در بخش سوالات متداول نبود، "
            "می‌تونی با پشتیبان ویراوب در ارتباط باشی.\n\n"
            f"📞 پشتیبان: {SUPPORT_USERNAME}",
            main_menu()
        )

        return


    if callback_data == "get_link":

        send_message(
            chat_id,
            "📱 برای دریافت لینک دوره، "
            "لطفاً شماره تلفنت رو همینجا ارسال کن.\n\n"
            "مثال:\n"
            "09123456789\n\n"
            "بعد از دریافت شماره، لینک دوره برایت ارسال می‌شود."
        )

        return


# =========================================================
# PROCESS MESSAGE
# =========================================================

def process_message(message):

    chat = message.get("chat")

    if not chat:
        return

    chat_id = chat.get("id")

    if not chat_id:
        return

    text = message.get(
        "text",
        ""
    ).strip()

    print("Chat ID:", chat_id)
    print("User text:", text)


    # -----------------------------------------
    # START
    # -----------------------------------------

    if text == "/start":

        send_message(
            chat_id,
            WELCOME_TEXT,
            main_menu()
        )

        return


    # -----------------------------------------
    # FAQ TEXT
    # -----------------------------------------

    faq_key = detect_faq(text)

    if faq_key:

        send_message(
            chat_id,
            FAQ_ANSWERS[faq_key],
            faq_menu()
        )

        return


    # -----------------------------------------
    # PHONE NUMBER
    # -----------------------------------------

    phone = normalize_phone(text)

    if phone:

        print(
            "Customer phone received:",
            phone
        )

        send_message(
            chat_id,
            "✅ شماره تلفنت دریافت شد.\n\n"
            "ممنون از اعتمادت 🌱\n\n"
            "🔗 لینک دوره:\n"
            f"{COURSE_LINK}\n\n"
            "اگر سوال دیگری داری، من در خدمتم.",
            main_menu()
        )

        return


    # -----------------------------------------
    # NORMAL MESSAGE
    # -----------------------------------------

    send_message(
        chat_id,
        "پیامت رو دریافت کردم 👌\n\n"
        "اگر سوالت درباره دوره‌هاست، "
        "می‌تونی سوالت رو همینجا بنویسی یا "
        "از منوی زیر استفاده کنی.",
        main_menu()
    )


# =========================================================
# WEBHOOK
# =========================================================

def handle_update(update):

    print("=" * 60)
    print("Received update:")
    print(update)
    print("=" * 60)

    if not update:
        return

    # -----------------------------------------
    # CALLBACK QUERY
    # -----------------------------------------

    callback_query = update.get(
        "callback_query"
    )

    if callback_query:

        data = callback_query.get(
            "data"
        )

        message = callback_query.get(
            "message"
        )

        if message and data:

            chat = message.get(
                "chat"
            )

            if chat:

                chat_id = chat.get(
                    "id"
                )

                handle_callback(
                    chat_id,
                    data
                )

        return


    # -----------------------------------------
    # MESSAGE
    # -----------------------------------------

    message = update.get(
        "message"
    )

    if message:

        process_message(
            message
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])
def home():

    return jsonify({
        "status": "online",
        "bot": "Viraweb Support Assistant",
        "webhook": "active"
    })


# =========================================================
# WEBHOOK ROUTE
# =========================================================

@app.route("/", methods=["POST"])
@app.route("/api", methods=["POST"])
@app.route("/api/", methods=["POST"])
def webhook():

    print("🔥🔥 NEW VERSION WEBHOOK RUNNING 🔥🔥")
    try:

        update = request.get_json(
            silent=True
        )

        handle_update(
            update
        )

        return jsonify({
            "ok": True
        })

    except Exception as error:

        print(
            "WEBHOOK ERROR:",
            repr(error)
        )

        # برای اینکه Bale دوباره Update را
        # پشت سر هم ارسال نکند، پاسخ 200 می‌دهیم.
        return jsonify({
            "ok": False
        })
