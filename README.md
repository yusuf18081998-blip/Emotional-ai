# 🤖 Emotional AI — Hissiyotli Sun'iy Intellekt (100% bepul)

Odam bilan gaplashganda **his-tuyg'ularni simulyatsiya qiluvchi** chatbot.
Kayfiyat, stress, energiya, ishonch, qo'rquv, sog'inch, g'urur, uyat,
umid, hasad va mehr kabi 11 xil "ichki holat" suhbat davomida o'zgarib
turadi va bot javoblarining ohangiga ta'sir qiladi.

> ⚠️ **Muhim halollik:** Bu HAQIQIY ongli hissiyot emas — matematik holat
> modeli + til modeli orqali hissiyotni ishonarli tarzda **taqlid qilish**.
> Botni chinakam his qiluvchi mavjudot sifatida taqdim etmang.

## Fayllar (barchasi bitta papkada, ichki papkalarsiz)

```
emotion_engine.py   # Hissiy holat modeli
memory.py            # Suhbat xotirasi (JSON fayl)
llm_client.py         # Ollama bilan bog'lanish
chatbot.py            # Terminal chat
app.py                # Flask veb-server (HTML/CSS/JS shu faylning ichida)
index.html             # GitHub Pages uchun statik vizual namuna
requirements.txt
README.md
```

## Nega pullik emas?

- LLM sifatida **Ollama** ishlatiladi — kompyuteringizda lokal, bepul model
- Xotira va hissiyot holati oddiy JSON fayllarda saqlanadi
- Sentiment tahlili kalit-so'zlarga asoslangan — tashqi pullik API kerak emas

## O'rnatish

```bash
pip install -r requirements.txt

# Ollama (bepul): https://ollama.com dan o'rnating, so'ng:
ollama pull llama3.1
```

### A) Terminalda ishlatish
```bash
python chatbot.py
```

### B) Brauzerda (chat interfeysi)
```bash
python app.py
```
Brauzerda oching: **http://localhost:5000**

## GitHub Pages haqida muhim eslatma

`index.html` — bu faqat **vizual namuna**. GitHub Pages statik hosting
bo'lgani uchun Python/Flask kodini bajara olmaydi, shuning uchun
`yourusername.github.io/repo-nomi/` orqali ochilgan sahifada chat
funksiyasi ishlamaydi (faqat dizaynni ko'rasiz). Botni chin ma'noda
ishlatish uchun `python app.py` ni **o'z kompyuteringizda** ishga
tushirishingiz shart — chunki Ollama ham faqat lokal ishlaydi.

## Litsenziya

MIT — erkin foydalaning, o'zgartiring, GitHub'ga qo'ying.
