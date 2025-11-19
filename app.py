import os
import requests
from flask import Flask, request

# ==========================
#  CONFIG
# ==========================

# Railway / env se
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
# Verify token ko hard-code kar dete hain taa-ke 100% match ho
VERIFY_TOKEN = "instabot2025"

PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)


# ==========================
#  WEBHOOK (VERIFY + EVENTS)
# ==========================

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # ----- 1) VERIFY (GET) -----
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook Verified")
            # Facebook ko sirf challenge string chahiye
            return challenge, 200
        else:
            print("❌ Verification Failed")
            return "Verification failed", 403

    # ----- 2) EVENTS (POST) -----
    # silent=True -> agar JSON na ho to error nahi, sirf None de
    data = request.get_json(silent=True) or {}
    print("📩 Incoming Event:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):

            # 2a) Messenger messages
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id")
                message_text = (messaging.get("message") or {}).get("text")

                if sender_id and message_text:
                    send_auto_reply(sender_id)

            # 2b) Instagram messages
            for change in entry.get("changes", []):
                value = change.get("value") or {}
                if value.get("messaging_product") == "instagram":
                    for msg in value.get("messages", []):
                        ig_sender = msg.get("from")
                        text_body = (msg.get("text") or {}).get("body")

                        if ig_sender and text_body:
                            send_auto_reply(ig_sender)

    return "EVENT_RECEIVED", 200


# ==========================
#  AUTO REPLY
# ==========================

def send_auto_reply(sender_id):
    reply_text = (
        "Bhai, main ne aap ka message receive kar liya hai 😊 "
        "Main abhi busy hoon — free hote hi reply kar dunga. Don't mind ❤️"
    )

    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": reply_text},
        "messaging_type": "RESPONSE",
    }

    resp = requests.post(url, params=params, json=payload)
    print("➡️ Message Sent:", resp.status_code, resp.text)


# ==========================
#  MAIN
# ==========================

if __name__ == "__main__":
    print(f"🚀 Bot Starting on port {PORT} ...")
    app.run(host="0.0.0.0", port=PORT)
