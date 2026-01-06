import os
import json
import datetime
import time
from google import genai

# ===== CONFIG =====
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
PAGES_DIR = os.path.join(BASE_DIR, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

ARTICLES_PER_RUN = config.get("articles_per_run", 1)
MIN_WORDS = config.get("min_words", 1200)

# ===== GEMINI =====
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"

# ===== GENERATE ARTICLE (ONE CALL) =====
def generate_article():
    prompt = f"""
Ты опытный крипто-энтузиаст и автор.

СДЕЛАЙ ОДНОВРЕМЕННО:
1) придумай ОДНУ уникальную, легальную тему статьи про криптовалюты
2) напиши большую, полезную статью по этой теме

Требования к статье:
- минимум {MIN_WORDS} слов
- живой человеческий стиль
- можно от первого лица
- без инвестиционных советов
- без обещаний дохода
- если уместно: FAQ, таблицы, списки, подзаголовки
- формат Markdown

Верни СТРОГО в JSON, без текста вокруг:

{{
  "title": "заголовок статьи",
  "content": "markdown-текст статьи"
}}
"""

    r = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    data = json.loads(r.text)
    return data["title"], data["content"]

# ===== SAVE =====
def save_article(title, content):
    safe = "".join(c for c in title if c.isalnum() or c in " _-").strip()
    filename = safe.replace(" ", "_").lower()[:80]
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(PAGES_DIR, f"{filename}_{ts}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}")

    print(f"✅ Saved: {path}")

# ===== MAIN =====
def main():
    for i in range(ARTICLES_PER_RUN):
        print(f"--- {i+1}/{ARTICLES_PER_RUN} ---")
        title, content = generate_article()
        save_article(title, content)
        time.sleep(20)  # ОБЯЗАТЕЛЬНО, иначе 429

if __name__ == "__main__":
    main()
