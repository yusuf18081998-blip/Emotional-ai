"""
memory.py
----------
Suhbat tarixini saqlaydi (oddiy JSON fayl — pullik vektor bazasi shart
emas). Bot "meni eslab qolyapti" degan hissiyot uyg'otish uchun oxirgi
N ta xabarni har safar promptga qo'shib yuboradi.
"""

import json
import os
from datetime import datetime


class Memory:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

    def __init__(self, user_id: str = "default", max_messages: int = 30):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.path = os.path.join(self.DATA_DIR, f"memory_{user_id}.json")
        self.max_messages = max_messages
        self.history = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat(timespec="seconds"),
        })
        # Faqat oxirgi N ta xabarni saqlab qolamiz (xotira "cheklangan")
        self.history = self.history[-self.max_messages:]
        self._save()

    def as_chat_messages(self):
        """Ollama/chat API formatiga mos ro'yxat qaytaradi."""
        return [{"role": m["role"], "content": m["content"]} for m in self.history]

    def clear(self):
        self.history = []
        self._save()
