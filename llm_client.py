"""
llm_client.py
--------------
Ollama orqali kompyuteringizda BEPUL ishlaydigan LLM bilan gaplashadi.
Hech qanday API kalit yoki to'lov kerak emas — model kompyuteringizda
lokal ishlaydi.

O'rnatish (bir marta):
    1) https://ollama.com dan Ollama'ni yuklab o'rnating
    2) Terminalda:  ollama pull llama3.1
       (yoki kichikroq/tezroq model uchun:  ollama pull qwen2.5:7b )
    3) Ollama fonda avtomatik ishga tushadi (localhost:11434)

Shu bilan hammasi bepul va internetga ham muhtoj emassiz (birinchi
yuklab olishdan keyin).
"""

import json
import requests


class LLMClient:
    def __init__(self, model: str = "llama3.1", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def chat(self, system_prompt: str, messages: list, temperature: float = 0.8) -> str:
        """
        system_prompt: bot shaxsiyati + hozirgi hissiy holat tavsifi
        messages: [{"role": "user"/"assistant", "content": "..."}]
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            resp = requests.post(f"{self.host}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]
        except requests.exceptions.ConnectionError:
            return (
                "[XATO] Ollama'ga ulanib bo'lmadi. Ollama o'rnatilganini va "
                "ishga tushirilganini tekshiring: https://ollama.com"
            )
        except Exception as e:
            return f"[XATO] {e}"
