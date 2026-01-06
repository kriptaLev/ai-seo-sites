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

MODEL_NAME = "models/gemini-1.5-flash"  # ✅ РАБОЧАЯ МОДЕЛЬ

# ===== TOPIC GENERATION =====
def generate_topic():
    prompt = """
Придумай ОДНУ уникальную, легальную и SEO-востребованную тему статьи про криптовалюты.

Правила:
- не новость
- не скам
- не инвестиционный совет
- тема может быть широкой или узкой
- избегай повторов
- верни только тему
"""
    r = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return r.text.strip()

# ===== ARTICLE GENERATION =====
def generate_article(topic):
    prompt = f"""
Ты опытный крипто-энтузиаст и автор.

Напиши живую статью на тему:
{topic}

Требования:
- минимум {MIN_WORDS} слов
- человеческий стиль
- допускается личный опыт
- без инвестиционных советов

Добавляй ТОЛЬКО если уместно:
- таблицы
- FAQ
- списки
- подзаголовки

Формат: Markdown.
"""
    r = client.models.generate_content(
        model=MODEL_NAME,
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
    main()
