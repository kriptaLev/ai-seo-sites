import os
import json
import datetime
from google import genai

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "pages")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

os.makedirs(PAGES_DIR, exist_ok=True)

# ===== LOAD CONFIG =====
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

ARTICLES_PER_RUN = config.get("articles_per_run", 3)
MIN_WORDS = config.get("min_words", 1000)

# ===== GEMINI =====
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ===== TOPIC GENERATION =====
def generate_topic():
    prompt = """
Придумай ОДНУ уникальную, легальную и SEO-востребованную тему статьи про криптовалюты.

Правила:
- не новость
- не скам
- не инвестиционный совет
- тема может быть широкой или узкой
- избегай точных повторов популярных заголовков
- просто тема, без кавычек и пояснений
"""
    r = client.models.generate_content(
        model="models/gemini-1.5-pro",
        contents=prompt
    )
    return r.text.strip()

# ===== ARTICLE GENERATION =====
def generate_article(topic):
    prompt = f"""
Ты опытный крипто-энтузиаст и автор, который давно в индустрии.

Напиши ЖИВУЮ статью на тему:
{topic}

Требования:
- минимум {MIN_WORDS} слов
- человеческий стиль
- можно писать от первого лица
- делиться опытом, ошибками, наблюдениями
- структура НЕ шаблонная

ДОБАВЛЯЙ ТОЛЬКО ЕСЛИ УМЕСТНО:
- подзаголовки
- списки
- таблицы (markdown)
- FAQ
- практические советы
- типичные ошибки новичков
- вывод

Запрещено:
- обещания дохода
- инвестиционные рекомендации
- незаконные схемы

Формат: Markdown.
"""
    r = client.models.generate_content(
        model="models/gemini-1.5-pro",
        contents=prompt
    )
    return r.text.strip()

# ===== SAVE =====
def save_article(topic, content):
    safe = "".join(c for c in topic if c.isalnum() or c in " _-").strip()
    filename = safe.replace(" ", "_").lower()[:80]
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    path = os.path.join(PAGES_DIR, f"{filename}_{ts}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{content}")

    print(f"✅ Saved: {path}")

# ===== MAIN =====
def main():
    for i in range(ARTICLES_PER_RUN):
        print(f"--- {i+1}/{ARTICLES_PER_RUN} ---")
        topic = generate_topic()
        article = generate_article(topic)
        save_article(topic, article)

if __name__ == "__main__":
    main()# ---------- TOPIC GENERATION ----------
def generate_topic():
    prompt = """
Ты аналитик крипторынка и SEO-редактор.

СГЕНЕРИРУЙ ОДНУ ТЕМУ статьи:
- строго легальная
- информационная
- без инвестиционных советов
- связана с криптовалютами, блокчейном, Web3, DeFi, NFT, безопасностью, биржами, технологиями
- тема должна быть естественной и реальной

Верни ответ строго в JSON, без текста вокруг:

{
  "topic": "...",
  "type": "broad" или "narrow"
}

broad = широкая тема с высоким интересом
narrow = узкая под-тема
"""

    response = model.generate_content(prompt)
    data = json.loads(response.text.strip())
    return data["topic"], data["type"]

# ---------- ARTICLE GENERATION ----------
def generate_article(topic):
    prompt = f"""
Ты опытный крипто-энтузиаст, который несколько лет изучает рынок,
тестирует сервисы, следит за трендами и учится на собственных ошибках.

НАПИШИ БОЛЬШУЮ, ПОЛЕЗНУЮ СТАТЬЮ на тему:
«{topic}»

СТИЛЬ:
- как живой человек, а не учебник
- допускаются формулировки: "по моему опыту", "я сталкивался", "на практике"
- объясняй сложные вещи простым языком
- логика важнее структуры
- подзаголовки H2/H3 используй ТОЛЬКО если это действительно уместно
- списки и примеры — только если они реально помогают понять тему

ОБЪЁМ:
- 3000–5000 слов

ЗАПРЕТЫ:
- никакой воды
- никакого шаблонного SEO
- никаких клише
- не повторяй одинаковые фразы
- не делай одинаковое вступление

ФОРМАТ:
Чистый Markdown-текст.
"""

    response = model.generate_content(prompt)
    return response.text.strip()

# ---------- MAIN LOOP ----------
generated = 0

while generated < ARTICLES_COUNT:
    topic, t_type = generate_topic()

    count = topic_memory.get(topic, {}).get("count", 0)
    limit = MAX_BROAD if t_type == "broad" else MAX_NARROW

    if count >= limit:
        continue

    article_text = generate_article(topic)

    filename = unique_filename(topic)
    with open(os.path.join("pages", filename), "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{article_text}")

    topic_memory[topic] = {
        "count": count + 1,
        "type": t_type
    }

    save_memory()
    generated += 1
    time.sleep(2)

print("Генерация завершена. Старые статьи сохранены.")
