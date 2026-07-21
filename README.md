# 🤖 Emotional AI — Hissiyotli Sun'iy Intellekt (100% bepul)

Odam bilan gaplashganda **his-tuyg'ularni simulyatsiya qiluvchi** chatbot.
Kayfiyat, stress, energiya va ishonch kabi "ichki holatlar" suhbat davomida
o'zgarib turadi va bot javoblarining ohangiga ta'sir qiladi — masalan, siz
qo'pol gapirsangiz "dili og'riydi", iliq gapirsangiz "kayfiyati ko'tariladi".

> ⚠️ **Muhim halollik:** Bu HAQIQIY ongli hissiyot emas. Bu — matematik
> holat modeli + til modeli orqali hissiyotni ishonarli tarzda
> **taqlid qilish**. Hozirgi fan darajasida haqiqiy "sun'iy ong/tuyg'u"
> yaratish mumkin emas. Foydalanuvchilarga botni chinakam his qiluvchi
> mavjudot sifatida taqdim etmang.

## Nega pullik emas?

- LLM sifatida **Ollama** ishlatiladi — kompyuteringizda lokal, bepul
  ishlaydigan model (Llama 3.1, Qwen, Mistral va h.k.)
- Xotira va hissiyot holati oddiy JSON fayllarda saqlanadi — pullik
  bazaga ehtiyoj yo'q
- Sentiment tahlili kalit-so'zlarga asoslangan — tashqi pullik API kerak
  emas

## O'rnatish

```bash
# 1) Reponi klonlash
git clone <sizning-repo-havolangiz>
cd emotional-ai

# 2) Python kutubxonalarini o'rnatish
pip install -r requirements.txt

# 3) Ollama'ni o'rnatish (bepul): https://ollama.com
#    O'rnatgandan keyin terminalda:
ollama pull llama3.1
# (sekinroq kompyuter uchun kichikroq model: ollama pull qwen2.5:7b)
```

### A) Terminalda ishlatish

```bash
cd src
python chatbot.py
```

Debug rejimida (hissiy holatni har qadamda ko'rish uchun):
```bash
python chatbot.py --debug
```

### B) Brauzerda (veb-chat interfeysi)

```bash
python app.py
```

So'ng brauzerda oching: **http://localhost:5000**

Bu — hissiy holatga qarab rangi va "nafas olish" tezligi o'zgaradigan
jonli orb bilan chat sahifasi. Bu faqat kompyuteringizda ishlaydi (lokal
server); GitHub Pages orqali internetga ochiq holda ishlatib bo'lmaydi,
chunki Ollama ham lokal ishlaydi.

## Loyiha tuzilishi

```
emotional-ai/
├── src/
│   ├── emotion_engine.py   # Hissiy holat modeli (11 ta o'zgaruvchi)
│   ├── memory.py           # Suhbat xotirasi (JSON fayl)
│   ├── llm_client.py       # Ollama bilan bog'lanish
│   └── chatbot.py          # Terminal chat
├── templates/
│   └── index.html          # Veb-chat sahifasi
├── static/
│   ├── style.css           # Dizayn (jonli "orb" + chat balonchalar)
│   └── app.js               # Chat mantiqi va orb animatsiyasi
├── app.py                  # Flask serveri (veb-chat uchun)
├── data/                   # Avtomatik yaratiladi — holat/xotira
├── requirements.txt
└── README.md
```

## Qanday ishlaydi?

1. **Sentiment tahlil**: har bir xabaringiz kalit-so'zlar bo'yicha tahlil
   qilinadi (ijobiy/salbiy/qo'pol).
2. **Hissiy holat yangilanadi**: `mood`, `stress`, `energy`, `trust`
   qiymatlari shunga qarab o'zgaradi va vaqt o'tishi bilan asta-sekin
   "normal holat"ga qaytadi (`EmotionEngine.DECAY_RATE`).
3. **System prompt yaratiladi**: hozirgi holat tabiiy tilga o'giriladi
   ("kayfiyating yomon, dilingiz og'rigan" kabi) va LLM'ga yuboriladi.
4. **LLM javob beradi**: Ollama orqali lokal model shu hissiy ohangda
   javob yozadi.
5. **Xotiraga saqlanadi**: suhbat tarixi keyingi safar ham eslab
   qolinishi uchun saqlanadi.

## Kengaytirish g'oyalari

- `emotion_engine.py`dagi oddiy kalit-so'z sentiment tahlilini bepul
  HuggingFace modeliga (`transformers` kutubxonasi orqali, masalan
  `cardiffnlp/twitter-xlm-roberta-base-sentiment`) almashtirish
- Ovozli kirish/chiqish qo'shish (bepul: `whisper.cpp` + `piper-tts`)
- Web interfeys qo'shish (Flask/FastAPI + oddiy HTML)
- Har xil "shaxsiyat"lar yaratish (BASE_PERSONALITY'ni o'zgartirish orqali)

## Litsenziya

MIT — erkin foydalaning, o'zgartiring, GitHub'ga qo'ying.
