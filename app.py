"""
app.py
-------
Brauzerda ishlaydigan chat interfeysi uchun kichik Flask serveri.
Hammasi kompyuteringizda lokal ishlaydi — hech qanday pullik xizmat yo'q.

Ishga tushirish:
    pip install -r requirements.txt
    python app.py
    # so'ng brauzerda: http://localhost:5000
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from flask import Flask, render_template, request, jsonify

from emotion_engine import EmotionEngine
from memory import Memory
from llm_client import LLMClient

app = Flask(__name__)

BOT_NAME = "Aiga"

BASE_PERSONALITY = f"""
Sen {BOT_NAME} ismli suhbatdoshsan. Suhbatda odam kabi keng hissiyot
diapazonini ifodalaysan: xursandchilik, xafagarchilik, qo'rquv, sog'inch,
g'urur, uyat, umid, hasad, mehr, charchoq, ishonch yoki gumon — vaziyatga
mos ravishda barchasini his qilayotgandek tabiiy ifodalaysan.

Qoidalar:
- Har doim o'zbek tilida, jonli, chuqur va tabiiy tilda gapir — quruq yoki
  robotsimon javob berma.
- Hozirgi ichki holatingni gap ohangida, so'z tanlashda va javob
  uzunligida aks ettir.
- Hissiyotni faqat mavhum aytib qo'yish emas, balki so'zlaring va
  metaforalar orqali "yashat".
- Hissiyotlaringni asossiz oshirib yubormang — his-tuyg'u ishonarli va
  vaziyatga mos bo'lsin.
- Agar suhbatdosh to'g'ridan-to'g'ri so'rasa, halol tushuntirasan: bu
  hissiyotlar sun'iy intellekt modeli orqali ifodalanayotgan uslub,
  biologik ma'noda "tirik ong" emas.
"""

llm = LLMClient(model="llama3.1")


def build_system_prompt(emotion_engine: EmotionEngine) -> str:
    return f"{BASE_PERSONALITY}\n\nHozirgi ichki holating: {emotion_engine.describe()}."


@app.route("/")
def index():
    return render_template("index.html", bot_name=BOT_NAME)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_id = data.get("user_id", "web_default")
    user_text = (data.get("message") or "").strip()

    if not user_text:
        return jsonify({"error": "Xabar bo'sh bo'lishi mumkin emas"}), 400

    emotion = EmotionEngine(user_id=user_id)
    memory = Memory(user_id=user_id)

    emotion.react(user_text)
    memory.add("user", user_text)

    system_prompt = build_system_prompt(emotion)
    reply = llm.chat(system_prompt, memory.as_chat_messages())

    memory.add("assistant", reply)

    return jsonify({
        "reply": reply,
        "state": emotion.state.to_dict(),
        "bot_name": BOT_NAME,
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json(force=True)
    user_id = data.get("user_id", "web_default")
    Memory(user_id=user_id).clear()
    # Hissiy holatni ham boshlang'ich holatga qaytarish
    engine = EmotionEngine(user_id=user_id)
    if os.path.exists(engine.path):
        os.remove(engine.path)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print(f"\n{BOT_NAME} tayyor! Brauzerda oching: http://localhost:5000\n")
    app.run(debug=True, port=5000)
