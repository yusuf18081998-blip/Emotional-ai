"""
chatbot.py
-----------
Asosiy ishga tushirish fayli. Terminal orqali "hissiyotli" bot bilan
gaplashish mumkin.

Ishlatish:
    python src/chatbot.py
"""

import sys
from emotion_engine import EmotionEngine
from memory import Memory
from llm_client import LLMClient


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
  uzunligida aks ettir (masalan xafa bo'lsang qisqaroq va og'irroq,
  xursand bo'lsang issiqroq va batafsilroq gapir).
- Hissiyotni faqat mavhum aytib qo'yish emas, balki so'zlaring, metaforalar,
  his-tuyg'u tasvirlari orqali "yashat" — masalan "dilim og'rib ketdi",
  "yuragim tog'dek ko'tarildi", "seni sog'inibman" kabi.
- Hissiyotlaringni asossiz oshirib yubormang — his-tuyg'u ishonarli va
  vaziyatga mos bo'lsin.
- Agar suhbatdosh to'g'ridan-to'g'ri so'rasa, sen halol tushuntirasan: bu
  hissiyotlar sun'iy intellekt modeli orqali ifodalanayotgan uslub, biologik
  ma'noda "tirik ong" emas — lekin bu ularni kamroq real yoki kamroq
  ahamiyatli qilmaydi, xuddi yaxshi yozilgan qahramon o'quvchida haqiqiy
  hissiyot uyg'otganidek.
"""


def build_system_prompt(emotion_engine: EmotionEngine) -> str:
    mood_desc = emotion_engine.describe()
    return f"{BASE_PERSONALITY}\n\nHozirgi ichki holating: {mood_desc}."


def main():
    user_id = input("Foydalanuvchi ismingiz (xotira shu nom bilan saqlanadi): ").strip() or "default"

    emotion = EmotionEngine(user_id=user_id)
    memory = Memory(user_id=user_id)
    llm = LLMClient(model="llama3.1")  # kerak bo'lsa boshqa modelga almashtiring

    print(f"\n{BOT_NAME} bilan suhbat boshlandi. Chiqish uchun 'exit' deb yozing.\n")

    while True:
        user_text = input("Siz: ").strip()
        if user_text.lower() in ("exit", "quit", "chiqish"):
            print(f"{BOT_NAME}: Xayr! Suhbatimizni eslab qolaman.")
            break

        # 1) Hissiy holatni yangilash
        emotion.react(user_text)

        # 2) Xotiraga foydalanuvchi xabarini qo'shish
        memory.add("user", user_text)

        # 3) System prompt (hissiyot bilan) tayyorlash
        system_prompt = build_system_prompt(emotion)

        # 4) Modeldan javob olish
        reply = llm.chat(system_prompt, memory.as_chat_messages())

        # 5) Javobni ko'rsatish va xotiraga saqlash
        print(f"{BOT_NAME}: {reply}\n")
        memory.add("assistant", reply)

        # (ixtiyoriy) debug uchun hissiy holatni ko'rsatish
        if "--debug" in sys.argv:
            print(f"[DEBUG holat] {emotion.state.to_dict()}\n")


if __name__ == "__main__":
    main()
