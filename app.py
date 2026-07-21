"""
app.py
-------
Brauzerda ishlaydigan chat interfeysi uchun kichik Flask serveri.
DIQQAT: bu versiyada HTML, CSS va JS barchasi shu faylning ichida —
hech qanday alohida papka (templates/, static/) kerak emas. Barcha
fayllarni bitta joyga (flat) tashlab GitHub'ga yuklasangiz ham ishlaydi.

Ishga tushirish:
    pip install -r requirements.txt
    python app.py
    # so'ng brauzerda: http://localhost:5000
"""

from flask import Flask, request, jsonify, Response

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


# ---------------------------------------------------------------------------
# Butun sahifa (HTML + CSS + JS) — bitta satrda, tashqi faylga muhtoj emas
# ---------------------------------------------------------------------------

PAGE_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__BOT_NAME__ — Hissiyotli suhbatdosh</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #17111F; --surface: #221A2C; --surface-2: #2B2136; --border: #3A2E47;
  --text: #F1E9F2; --text-dim: #B3A2BE;
  --accent-warm: #E8927C; --accent-warm-dim: #7A5348; --accent-cool: #8891C7;
  --accent-alert: #C75146; --accent-gold: #D9A441;
  --radius-lg: 22px; --radius-md: 14px; --radius-sm: 9px;
  --font-display: "Fraunces", Georgia, serif;
  --font-body: "Manrope", -apple-system, sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--bg); color: var(--text); font-family: var(--font-body); }
body {
  background-image:
    radial-gradient(ellipse 900px 500px at 20% -10%, rgba(232,146,124,0.08), transparent),
    radial-gradient(ellipse 700px 500px at 90% 10%, rgba(136,145,199,0.10), transparent);
}
.app { max-width: 720px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; padding: 20px 20px 14px; }
.app-header { display: flex; align-items: center; gap: 16px; padding: 10px 6px 18px; border-bottom: 1px solid var(--border); }
.orb-wrap { width: 56px; height: 56px; flex: 0 0 auto; }
.orb-svg { width: 100%; height: 100%; display: block; animation: breathe 4.2s ease-in-out infinite; transition: filter 0.6s ease; }
@keyframes breathe { 0%,100% { transform: scale(0.94); } 50% { transform: scale(1.04); } }
.header-text { flex: 1; min-width: 0; }
.header-text h1 { font-family: var(--font-display); font-weight: 600; font-size: 1.5rem; margin: 0 0 2px; letter-spacing: 0.01em; }
.mood-label { margin: 0; font-size: 0.82rem; color: var(--text-dim); font-style: italic; font-family: var(--font-display); transition: color 0.5s ease; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.reset-btn { background: transparent; border: 1px solid var(--border); color: var(--text-dim); font-family: var(--font-body); font-size: 0.78rem; padding: 8px 12px; border-radius: 999px; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; }
.reset-btn:hover { border-color: var(--accent-warm); color: var(--accent-warm); }
.chat-area { flex: 1; overflow-y: auto; padding: 22px 6px; display: flex; flex-direction: column; gap: 14px; }
.msg { display: flex; } .msg.user { justify-content: flex-end; } .msg.bot { justify-content: flex-start; }
.bubble { max-width: 78%; padding: 13px 17px; line-height: 1.5; font-size: 0.96rem; white-space: pre-wrap; animation: rise 0.28s ease; }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.msg.bot .bubble { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 4px; color: var(--text); }
.msg.user .bubble { background: linear-gradient(135deg, var(--accent-warm), #C9765F); color: #241611; font-weight: 500; border-radius: var(--radius-md) var(--radius-md) 4px var(--radius-md); }
.typing-indicator { display: flex; gap: 4px; padding: 0 6px 10px; }
.typing-indicator span { width: 6px; height: 6px; border-radius: 50%; background: var(--text-dim); animation: blink 1.2s infinite; }
.typing-indicator span:nth-child(2) { animation-delay: 0.15s; } .typing-indicator span:nth-child(3) { animation-delay: 0.3s; }
@keyframes blink { 0%,80%,100% { opacity: 0.25; } 40% { opacity: 1; } }
.composer { display: flex; gap: 10px; padding: 10px 6px 4px; }
#messageInput { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 13px 18px; color: var(--text); font-family: var(--font-body); font-size: 0.95rem; outline: none; transition: border-color 0.2s ease; }
#messageInput:focus { border-color: var(--accent-warm); } #messageInput::placeholder { color: var(--text-dim); }
#sendBtn { width: 46px; height: 46px; flex: 0 0 auto; border-radius: 50%; border: none; background: var(--accent-warm); color: #241611; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.15s ease, background 0.2s ease; }
#sendBtn:hover { transform: scale(1.06); } #sendBtn:active { transform: scale(0.96); } #sendBtn:disabled { opacity: 0.5; cursor: default; transform: none; }
.footnote { text-align: center; font-size: 0.72rem; color: var(--text-dim); margin: 10px 0 0; opacity: 0.7; }
.footnote code { background: var(--surface-2); padding: 1px 5px; border-radius: 4px; }
@media (max-width: 480px) { .app { padding: 14px 12px 10px; } .header-text h1 { font-size: 1.25rem; } .bubble { max-width: 86%; } }
@media (prefers-reduced-motion: reduce) { .orb-svg { animation: none; } .bubble { animation: none; } }
</style>
</head>
<body>
<div class="app">
  <header class="app-header">
    <div class="orb-wrap">
      <svg viewBox="0 0 200 200" class="orb-svg">
        <defs>
          <radialGradient id="orbGradient" cx="35%" cy="30%" r="75%">
            <stop id="orbStop1" offset="0%" stop-color="#E8927C"/>
            <stop id="orbStop2" offset="100%" stop-color="#7B4B6B"/>
          </radialGradient>
          <filter id="orbBlur" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6"/>
          </filter>
        </defs>
        <circle id="orbGlow" cx="100" cy="100" r="70" fill="url(#orbGradient)" filter="url(#orbBlur)" opacity="0.55"/>
        <path id="orbBlob" fill="url(#orbGradient)" />
      </svg>
    </div>
    <div class="header-text">
      <h1>__BOT_NAME__</h1>
      <p class="mood-label" id="moodLabel">hissiy holat kuzatilmoqda&hellip;</p>
    </div>
    <button class="reset-btn" id="resetBtn">Qayta boshlash</button>
  </header>

  <main class="chat-area" id="chatArea">
    <div class="msg bot">
      <div class="bubble">
        Assalomu alaykum. Men __BOT_NAME__man — suhbat davomida kayfiyatim,
        xavotirim, umidim o'zgarib turadi. Nima haqida gaplashamiz?
      </div>
    </div>
  </main>

  <div class="typing-indicator" id="typingIndicator" hidden>
    <span></span><span></span><span></span>
  </div>

  <form class="composer" id="composerForm">
    <input type="text" id="messageInput" placeholder="Xabar yozing…" autocomplete="off" autofocus />
    <button type="submit" id="sendBtn" aria-label="Yuborish">
      <svg viewBox="0 0 24 24" width="20" height="20"><path d="M3 11.5L21 3L13 21L11 13L3 11.5Z" fill="currentColor"/></svg>
    </button>
  </form>

  <p class="footnote">
    Bu — hissiyotni matn darajasida taqlid qiluvchi model, haqiqiy ong emas. ·
    Backend: <code>Ollama</code> (lokal, bepul)
  </p>
</div>

<script>
(function () {
  const chatArea = document.getElementById("chatArea");
  const form = document.getElementById("composerForm");
  const input = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const typingIndicator = document.getElementById("typingIndicator");
  const moodLabel = document.getElementById("moodLabel");
  const resetBtn = document.getElementById("resetBtn");
  const orbSvg = document.querySelector(".orb-svg");
  const orbBlob = document.getElementById("orbBlob");
  const orbStop1 = document.getElementById("orbStop1");
  const orbStop2 = document.getElementById("orbStop2");

  let userId = localStorage.getItem("emo_user_id");
  if (!userId) {
    userId = "web_" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("emo_user_id", userId);
  }

  function buildBlobPath(amplitude, seed) {
    const points = 8, cx = 100, cy = 100, base = 62;
    let d = "";
    for (let i = 0; i <= points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const wobble = Math.sin(angle * 3 + seed) * amplitude;
      const r = base + wobble;
      d += (i === 0 ? "M" : "L") + (cx + Math.cos(angle) * r).toFixed(1) + "," + (cy + Math.sin(angle) * r).toFixed(1) + " ";
    }
    return d + "Z";
  }

  let blobSeed = 0, currentAmplitude = 6;
  function animateBlob() {
    blobSeed += 0.015 + currentAmplitude * 0.002;
    orbBlob.setAttribute("d", buildBlobPath(currentAmplitude, blobSeed));
    requestAnimationFrame(animateBlob);
  }
  animateBlob();

  function lerpColor(hexA, hexB, t) {
    const a = parseInt(hexA.slice(1), 16), b = parseInt(hexB.slice(1), 16);
    const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
    const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
    return `rgb(${Math.round(ar+(br-ar)*t)},${Math.round(ag+(bg-ag)*t)},${Math.round(ab+(bb-ab)*t)})`;
  }

  function describeMoodShort(state) {
    if (state.stress > 0.55) return "taranglashgan holat";
    if (state.mood > 0.5) return "kayfiyati zo'r, ochiq";
    if (state.mood < -0.4) return "xafa, dili og'rigan";
    if (state.longing > 0.5) return "sog'ingan holatda";
    if (state.hope > 0.6) return "umidvor kayfiyatda";
    if (state.energy < 0.3) return "charchagan holatda";
    return "tinch, neytral holat";
  }

  function updateOrb(state) {
    const moodT = (state.mood + 1) / 2;
    let colorA = lerpColor("#8891C7", "#E8927C", moodT);
    let colorB = state.stress > 0.5 ? lerpColor("#5A4358", "#C75146", Math.min(1, state.stress)) : "#7A5348";
    orbStop1.setAttribute("stop-color", colorA);
    orbStop2.setAttribute("stop-color", colorB);
    currentAmplitude = 4 + state.energy * 6 + state.stress * 10;
    const duration = Math.max(1.6, 4.5 - state.stress * 3);
    orbSvg.style.animationDuration = duration.toFixed(2) + "s";
    moodLabel.textContent = describeMoodShort(state);
  }

  function addBubble(text, who) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + who;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    wrap.appendChild(bubble);
    chatArea.appendChild(wrap);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  async function sendMessage(text) {
    addBubble(text, "user");
    input.value = "";
    sendBtn.disabled = true;
    typingIndicator.hidden = false;
    chatArea.scrollTop = chatArea.scrollHeight;
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: text }),
      });
      const data = await res.json();
      typingIndicator.hidden = true;
      sendBtn.disabled = false;
      if (data.error) { addBubble("Xato: " + data.error, "bot"); return; }
      addBubble(data.reply, "bot");
      updateOrb(data.state);
    } catch (err) {
      typingIndicator.hidden = true;
      sendBtn.disabled = false;
      addBubble("Serverga ulanib bo'lmadi. `python app.py` ishga tushirilganini va Ollama fonda ishlab turganini tekshiring.", "bot");
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    sendMessage(text);
  });

  resetBtn.addEventListener("click", async () => {
    if (!confirm("Suhbat tarixi va hissiy holat butunlay tozalansinmi?")) return;
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    chatArea.innerHTML = "";
    addBubble("Suhbat tozalandi. Yangidan tanishaylikmi?", "bot");
    moodLabel.textContent = "hissiy holat kuzatilmoqda…";
  });

  input.focus();
})();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    html = PAGE_HTML.replace("__BOT_NAME__", BOT_NAME)
    return Response(html, mimetype="text/html")


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

    return jsonify({"reply": reply, "state": emotion.state.to_dict(), "bot_name": BOT_NAME})


@app.route("/api/reset", methods=["POST"])
def reset():
    import os
    data = request.get_json(force=True)
    user_id = data.get("user_id", "web_default")
    Memory(user_id=user_id).clear()
    engine = EmotionEngine(user_id=user_id)
    if os.path.exists(engine.path):
        os.remove(engine.path)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print(f"\n{BOT_NAME} tayyor! Brauzerda oching: http://localhost:5000\n")
    app.run(debug=True, port=5000)
