import os
import json
import datetime
from google import genai

# ===== CONFIG =====
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

ARTICLES_PER_RUN = config.get("articles_per_run", 3)
MIN_WORDS = config.get("min_words", 1200)

# ===== GEMINI =====
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.0-flash"

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

# ===== TOPIC GENERATION =====
def generate_topic():
    prompt = """
Придумай ОДНУ уникальную тему статьи про криптовалюты,
легальную, востребованную и полезную для SEO.
Ответь только текстом — только тему.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()

# ===== ARTICLE GENERATION =====
def generate_article(topic):
    prompt = f"""
Ты опытный крипто-автор, пишущий как человек.
Напиши живую, подробную статью на тему:
«{topic}»

Требования:
- минимум {MIN_WORDS} слов
- markdown-формат
- если уместно — добавь FAQ
- если уместно — добавь таблицы
- списки, подзаголовки, практические советы

Запрещено:
- инвестиционные советы
- обещания дохода
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()

# ===== SAVE ARTICLE =====
def save_article(topic, content):
    safe = "".join(c for c in topic if c.isalnum() or c in " _-").strip()
    filename = safe.replace(" ", "_").lower()[:80]
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(PAGES_DIR, f"{filename}_{ts}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{content}")

    print(f"✅ Saved: {path}")

# ===== MAIN LOOP =====
def main():
    for i in range(ARTICLES_PER_RUN):
        topic = generate_topic()
        article = generate_article(topic)
        save_article(topic, article)

if __name__ == "__main__":
    main()
