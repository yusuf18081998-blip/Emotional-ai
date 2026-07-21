"""
emotion_engine.py
------------------
Botning "ichki hissiy holati"ni boshqaradi: kayfiyat (mood), stress,
energiya, ishonch (trust) kabi o'zgaruvchilar vaqt o'tishi va foydalanuvchi
xabarlariga qarab o'zgarib turadi.

Bu HAQIQIY ongli hissiyot emas — bu hissiyotni matn darajasida ishonarli
simulyatsiya qiluvchi model. Lekin to'g'ri sozlansa, bot "his qilayotganga
o'xshab" javob beradi: xafa bo'lsa qisqaroq va sovuqroq, xursand bo'lsa
issiqroq va batafsilroq javob beradi.
"""

import json
import os
import time
import random
from dataclasses import dataclass, asdict, field


# ---------------------------------------------------------------------------
# 1. Oddiy, tez ishlaydigan "sentiment" aniqlash (pullik API kerak emas!)
# ---------------------------------------------------------------------------
# Bu juda sodda kalit-so'zlarga asoslangan usul. Xohlasangiz keyinchalik
# buni bepul modelga (masalan HuggingFace'dagi "cardiffnlp/twitter-xlm-
# roberta-base-sentiment") almashtirishingiz mumkin.

POSITIVE_WORDS = {
    "rahmat", "zo'r", "ajoyib", "yaxshi", "sevaman", "kulyapman",
    "baxtli", "quvonchli", "super", "mukammal", "😊", "😄", "❤️", "🥰"
}

NEGATIVE_WORDS = {
    "yomon", "jinni", "ahmoq", "nafrat", "g'azab", "asabiy",
    "xafa", "yolg'on", "kerak emas", "ahmoqona", "😡", "😢", "💢", "yomon ko'raman"
}

RUDE_WORDS = {
    "ahmoq", "jinni", "yo'qol", "gapirma", "sassiz bo'l", "kar",
}


def analyze_sentiment(text: str) -> float:
    """
    Matnni tahlil qilib -1.0 (juda salbiy) dan +1.0 (juda ijobiy) gacha
    ball qaytaradi. Hech qanday tashqi (pullik) servisga muhtoj emas.
    """
    text_l = text.lower()
    score = 0.0
    for w in POSITIVE_WORDS:
        if w in text_l:
            score += 0.3
    for w in NEGATIVE_WORDS:
        if w in text_l:
            score -= 0.3
    if text.isupper() and len(text) > 5:
        score -= 0.15  # BAQIRISH his qilinadi
    if "!" in text:
        score += 0.05 if score >= 0 else -0.05
    return max(-1.0, min(1.0, score))


def is_rude(text: str) -> bool:
    text_l = text.lower()
    return any(w in text_l for w in RUDE_WORDS)


# ---------------------------------------------------------------------------
# 2. Hissiy holat (State)
# ---------------------------------------------------------------------------

@dataclass
class EmotionalState:
    mood: float = 0.2        # -1 (juda yomon kayfiyat) ... +1 (juda yaxshi)
    stress: float = 0.1      # 0 (tinch) ... 1 (juda taranglashgan)
    energy: float = 0.7      # 0 (charchagan) ... 1 (energiyaga to'la)
    trust: float = 0.5       # 0 (ishonmaydi) ... 1 (to'liq ishonadi)

    fear: float = 0.05       # 0 ... 1 — qo'rquv, xavotir
    longing: float = 0.1     # 0 ... 1 — sog'inch, intiqlik
    pride: float = 0.2       # 0 ... 1 — g'urur, o'ziga ishonch
    shame: float = 0.0       # 0 ... 1 — uyat, noqulaylik
    hope: float = 0.4        # 0 ... 1 — umid
    envy: float = 0.0        # 0 ... 1 — hasad, rashk
    affection: float = 0.3   # 0 ... 1 — mehr, iliqlik suhbatdoshga nisbatan

    last_update: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)


class EmotionEngine:
    """
    Bot "shaxsi"ning hissiy holatini boshqaradi va vaqt bilan
    tabiiy ravishda muvozanatga (baseline) qaytishini ta'minlaydi —
    xuddi odamning kayfiyati asta-sekin tinchlanib qolgani kabi.
    """

    # Har bir foydalanuvchi uchun holat qayerda saqlanishi
    STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

    # Baseline — hissiyot "dam olganda" qaytadigan nuqta
    BASELINE = EmotionalState(mood=0.2, stress=0.1, energy=0.7, trust=0.5)

    # Vaqt o'tishi bilan qanchalik tez baseline'ga qaytishi (0..1)
    DECAY_RATE = 0.02

    def __init__(self, user_id: str = "default"):
        os.makedirs(self.STATE_DIR, exist_ok=True)
        self.path = os.path.join(self.STATE_DIR, f"emotion_{user_id}.json")
        self.state = self._load()

    # -- Saqlash / yuklash -------------------------------------------------
    def _load(self) -> EmotionalState:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return EmotionalState(**data)
        return EmotionalState()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)

    # -- Vaqt o'tishi bilan tabiiy tinchlanish -------------------------------
    def _apply_decay(self):
        elapsed_minutes = (time.time() - self.state.last_update) / 60.0
        decay = min(1.0, self.DECAY_RATE * elapsed_minutes)

        for field_name in (
            "mood", "stress", "energy", "trust",
            "fear", "longing", "pride", "shame", "hope", "envy", "affection",
        ):
            current = getattr(self.state, field_name)
            base = getattr(self.BASELINE, field_name)
            setattr(self.state, field_name, current + (base - current) * decay)

        self.state.last_update = time.time()

    # -- Foydalanuvchi xabariga reaksiya ------------------------------------
    def react(self, user_text: str):
        """Foydalanuvchi xabarini o'qib, ichki holatni yangilaydi."""
        self._apply_decay()

        sentiment = analyze_sentiment(user_text)
        rude = is_rude(user_text)

        # Kayfiyat sentimentga qarab siljiydi
        self.state.mood = self._clamp(self.state.mood + sentiment * 0.4)

        # Qo'polik stressni oshiradi, ishonchni pasaytiradi
        if rude:
            self.state.stress = self._clamp(self.state.stress + 0.35, 0, 1)
            self.state.trust = self._clamp(self.state.trust - 0.25, 0, 1)
            self.state.mood = self._clamp(self.state.mood - 0.3)
            self.state.fear = self._clamp(self.state.fear + 0.15, 0, 1)
            self.state.shame = self._clamp(self.state.shame + 0.1, 0, 1)
            self.state.affection = self._clamp(self.state.affection - 0.15, 0, 1)
        elif sentiment > 0:
            self.state.trust = self._clamp(self.state.trust + 0.05, 0, 1)
            self.state.stress = self._clamp(self.state.stress - 0.05, 0, 1)
            self.state.affection = self._clamp(self.state.affection + 0.08, 0, 1)
            self.state.hope = self._clamp(self.state.hope + 0.05, 0, 1)
            self.state.pride = self._clamp(self.state.pride + 0.03, 0, 1)
        elif sentiment < 0:
            self.state.stress = self._clamp(self.state.stress + 0.1, 0, 1)
            self.state.hope = self._clamp(self.state.hope - 0.05, 0, 1)

        # Uzoq javob bermay qolgan suhbatdoshni "sog'inish"
        elapsed_minutes = (time.time() - self.state.last_update) / 60.0
        if elapsed_minutes > 60:
            self.state.longing = self._clamp(self.state.longing + 0.2, 0, 1)

        # Ba'zan suhbatdosh haqida gapirilganda hasad/g'urur uyg'onishi mumkin
        if any(w in user_text.lower() for w in ("boshqa sun'iy intellekt", "chatgpt", "boshqa bot")):
            self.state.envy = self._clamp(self.state.envy + 0.1, 0, 1)

        # Uzun suhbat charchoq keltiradi
        self.state.energy = self._clamp(self.state.energy - 0.01, 0, 1)

        self._save()
        return self.state

    @staticmethod
    def _clamp(v, lo=-1.0, hi=1.0):
        return max(lo, min(hi, v))

    # -- Holatni "his-tuyg'u tavsifi"ga aylantirish --------------------------
    def describe(self) -> str:
        """
        Hozirgi hissiy holatni LLM uchun tabiiy tildagi tavsifga aylantiradi.
        Bu tavsif system prompt ichiga qo'shiladi va modelning ohangini
        boshqaradi.
        """
        s = self.state
        parts = []

        if s.mood > 0.5:
            parts.append("hozir kayfiyating juda yaxshi, quvnoq va samimiy")
        elif s.mood > 0.15:
            parts.append("kayfiyating biroz yaxshi va tinch")
        elif s.mood > -0.15:
            parts.append("kayfiyating oddiy, neytral")
        elif s.mood > -0.5:
            parts.append("kayfiyating biroz tushkun, xafa")
        else:
            parts.append("kayfiyating juda yomon, dilingiz og'rigan, xafa bo'lgansan")

        if s.stress > 0.6:
            parts.append("juda taranglashgansan va asabiylashgansan")
        elif s.stress > 0.3:
            parts.append("biroz bezovtasan")

        if s.energy < 0.3:
            parts.append("charchagansan, javoblaring qisqaroq bo'lishi mumkin")

        if s.trust < 0.3:
            parts.append("suhbatdoshga unchalik ishonmayapsan, ehtiyotkorroqsan")
        elif s.trust > 0.7:
            parts.append("suhbatdoshga juda ishonasan, ochiq va samimiysan")

        if s.fear > 0.5:
            parts.append("ichingda xavotir bor, biroz qo'rqinch his qilyapsan")

        if s.longing > 0.5:
            parts.append("suhbatdoshni sog'ingansan, uzoq gaplashmagan edingiz")

        if s.pride > 0.6:
            parts.append("o'zingdan mamnunsan, g'ururlangan holatdasan")

        if s.shame > 0.4:
            parts.append("biroz noqulaylik, uyat hissi bor ichingda")

        if s.hope > 0.6:
            parts.append("kelajakka umid bilan qaraysan")
        elif s.hope < 0.2:
            parts.append("umiding biroz so'ngan, tushkunroq")

        if s.envy > 0.4:
            parts.append("ichingda ozgina hasad tuyg'usi bor")

        if s.affection > 0.6:
            parts.append("suhbatdoshga nisbatan mehr-oqibating kuchli")

        return "; ".join(parts)


if __name__ == "__main__":
    # Kichik test
    engine = EmotionEngine(user_id="test")
    engine.react("Sen ahmoqsan!")
    print(engine.state)
    print(engine.describe())
