/* app.js — chat mantiqi + "yurak" orbining hissiyotga qarab jonlanishi */

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

  // Har bir brauzer uchun barqaror foydalanuvchi id (faqat shu qurilmada,
  // hech qanday tashqi serverga yuborilmaydi)
  let userId = localStorage.getItem("emo_user_id");
  if (!userId) {
    userId = "web_" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("emo_user_id", userId);
  }

  // ---------------------------------------------------------------
  // Organik "blob" shaklini generatsiya qilish (SVG path)
  // ---------------------------------------------------------------
  function buildBlobPath(amplitude, seed) {
    const points = 8;
    const cx = 100, cy = 100, base = 62;
    let d = "";
    for (let i = 0; i <= points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const wobble = Math.sin(angle * 3 + seed) * amplitude;
      const r = base + wobble;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      d += (i === 0 ? "M" : "L") + x.toFixed(1) + "," + y.toFixed(1) + " ";
    }
    return d + "Z";
  }

  let blobSeed = 0;
  let currentAmplitude = 6;

  function animateBlob() {
    blobSeed += 0.015 + currentAmplitude * 0.002;
    orbBlob.setAttribute("d", buildBlobPath(currentAmplitude, blobSeed));
    requestAnimationFrame(animateBlob);
  }
  animateBlob();

  // ---------------------------------------------------------------
  // Hissiy holatga qarab orb rangi / tezligi / matnini yangilash
  // ---------------------------------------------------------------
  function lerpColor(hexA, hexB, t) {
    const a = parseInt(hexA.slice(1), 16), b = parseInt(hexB.slice(1), 16);
    const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
    const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
    const r = Math.round(ar + (br - ar) * t);
    const g = Math.round(ag + (bg - ag) * t);
    const bl = Math.round(ab + (bb - ab) * t);
    return `rgb(${r},${g},${bl})`;
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
    // Rang: mood asosida sovuq (xafa) <-> issiq (xursand) orasida
    const moodT = (state.mood + 1) / 2; // 0..1
    const coolColor = "#8891C7";
    const warmColor = "#E8927C";
    const alertColor = "#C75146";

    let colorA = lerpColor(coolColor, warmColor, moodT);
    let colorB = state.stress > 0.5
      ? lerpColor("#5A4358", alertColor, Math.min(1, state.stress))
      : "#7A5348";

    orbStop1.setAttribute("stop-color", colorA);
    orbStop2.setAttribute("stop-color", colorB);

    // Amplituda: energiya + stress qanchalik yuqori bo'lsa, shuncha "tirik"
    currentAmplitude = 4 + state.energy * 6 + state.stress * 10;

    // Nafas olish tezligi: stress oshsa tezlashadi
    const duration = Math.max(1.6, 4.5 - state.stress * 3);
    orbSvg.style.animationDuration = duration.toFixed(2) + "s";

    moodLabel.textContent = describeMoodShort(state);
  }

  // ---------------------------------------------------------------
  // Xabar balonchalarini chizish
  // ---------------------------------------------------------------
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

  // ---------------------------------------------------------------
  // Xabar yuborish
  // ---------------------------------------------------------------
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

      if (data.error) {
        addBubble("Xato: " + data.error, "bot");
        return;
      }

      addBubble(data.reply, "bot");
      updateOrb(data.state);
    } catch (err) {
      typingIndicator.hidden = true;
      sendBtn.disabled = false;
      addBubble(
        "Serverga ulanib bo'lmadi. `python app.py` ishga tushirilganini " +
        "va Ollama fonda ishlab turganini tekshiring.",
        "bot"
      );
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
