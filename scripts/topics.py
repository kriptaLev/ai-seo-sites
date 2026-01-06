import google.generativeai as genai
import os
import json

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

prompt = """
Ты профессиональный крипто-аналитик и SEO-специалист.

Сгенерируй СПИСОК из 100 тем на русском языке ТОЛЬКО про криптовалюту.

ТЕМЫ ДОЛЖНЫ:
- быть реальными поисковыми запросами
- подходить для информационных статей
- интересны новичкам и среднему уровню и экспертному уровню
- иметь потенциал большого трафика
- быть легальными для РФ (информационный формат)

РАЗРЕШЁННЫЕ КАТЕГОРИИ:
- криптовалюты (BTC, ETH, альткоины)
- блокчейн
- DeFi
- NFT
- криптокошельки
- криптобиржи (обзорно)
- безопасность в крипте
- инвестиции в криптовалюту
- налоги и регулирование (инфо)
- ошибки новичков

ЗАПРЕЩЕНО:
- казино
- ставки
- схемы обмана
- нелегальные способы заработка
- обход законов РФ

ФОРМАТ ОТВЕТА:
ТОЛЬКО JSON-массив строк.
"""

response = model.generate_content(prompt)

topics = json.loads(response.text)

with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)

print(f"Крипто-тем создано: {len(topics)}")
