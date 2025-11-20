import os
import requests
from flask import Flask, request

# ==========================
#  CONFIG
# ==========================

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
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
            return challenge, 200
        else:
            print("❌ Verification Failed")
            return "Verification failed", 403

    # ----- 2) EVENTS (POST) -----
    data = request.get_json(silent=True) or {}
    print("📩 Incoming Event:", data)

    obj = data.get("object")

    # Messenger page messages OR Instagram DM (object: page / instagram)
    if obj in ("page", "instagram"):
        for entry in data.get("entry", []):
            # Naya format: entry["messaging"] for both Messenger + IG
            for msg_event in entry.get("messaging", []):
                sender_id = (msg_event.get("sender") or {}).get("id")
                message = msg_event.get("message") or {}

                # 🔹 Echo messages ignore (bot apne hi msg ko dobara reply na kare)
                if message.get("is_echo"):
                    print("↩️ Skipping echo message")
                    continue

                text = message.get("text")

                # Agar text ya sender na ho to skip
                if not text or not sender_id:
                    continue

                print(f"📨 Message from {sender_id}: {text}")
                send_auto_reply(sender_id)

    # Agar kisi aur type ka object aaye to bhi OK
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
