from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/api", methods=["GET", "POST"])
@app.route("/api/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({
            "status": "online",
            "bot": "Viraweb Support Assistant"
        })

    update = request.get_json(silent=True)

    print("Received update:", update)

    return jsonify({
        "ok": True
    })
