import os
import json
import sys
import time
from google import genai
from google.genai import errors

# =========================
# ПУТИ И КОНФИГ
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "content")

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

ARTICLES_PER_RUN = int(config.get("articles_per_run", 1))

MODEL_NAME = "gemini-2.0-flash"

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# =========================
# ПРОМПТЫ (РУССКИЕ)
# =========================

TOPIC_PROMPT = """
Ты опытный крипто-аналитик и SEO-редактор.

СГЕНЕРИРУЙ ОДНУ ТЕМУ статьи.

Правила:
- строго легальная
- информационная
- не новость
- не инвестиционный совет
- связана с криптовалютами, блокчейном, Web3, DeFi, NFT, безопасностью
- избегай очевидных и повторяющихся формулировок
- верни ТОЛЬКО тему, без кавычек и пояснений
"""

ARTICLE_PROMPT = """
Ты пишешь как живой человек, который давно в криптоиндустрии.

НАПИШИ БОЛЬШУЮ, ПОЛЕЗНУЮ СТАТЬЮ.

ТРЕБОВАНИЯ:
- живой человеческий стиль
- можно писать от первого лица
- объясняй сложные вещи простым языком
- делись опытом, наблюдениями, ошибками
- НЕ используй шаблонные SEO-фразы

ДОБАВЛЯЙ ТОЛЬКО ЕСЛИ УМЕСТНО:
- подзаголовки (H2/H3)
- списки
- таблицы (markdown)
- FAQ
- практические советы
- типичные ошибки новичков
- вывод

ЗАПРЕЩЕНО:
- обещания дохода
- инвестиционные рекомендации
- серые и незаконные схемы

ФОРМАТ (СТРОГО):

TITLE:
<заголовок статьи>

CONTENT:
<полный текст статьи в Markdown>
"""

# =========================
# ОБЁРТКА С ЗАЩИТОЙ ОТ 429
# =========================

def safe_generate(**kwargs):
    try:
        return client.models.generate_content(**kwargs)
    except errors.ClientError as e:
        msg = str(e)

        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            print("⏸️ Лимит Gemini исчерпан. Генерация остановлена корректно.")
            sys.exit(0)

        print("❌ Ошибка Gemini API:")
        print(msg)
        sys.exit(1)

# =========================
# ГЕНЕРАЦИЯ
# =========================

def generate_topic():
    r = safe_generate(
        model=MODEL_NAME,
        contents=TOPIC_PROMPT,
    )
    return r.text.strip()


def generate_article(topic):
    r = safe_generate(
        model=MODEL_NAME,
        contents=f"""
ТЕМА СТАТЬИ:
{topic}

{ARTICLE_PROMPT}
"""
    )

    text = r.text.strip()

    if "TITLE:" not in text or "CONTENT:" not in text:
        print("⚠️ Неверный формат ответа, статья пропущена.")
        return None, None

    title = text.split("CONTENT:")[0].replace("TITLE:", "").strip()
    content = text.split("CONTENT:")[1].strip()

    return title, content


def save_article(title, content):
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title[:80].replace(' ', '_')}.md"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}")

    print(f"✅ Сохранено: {filename}")

# =========================
# MAIN
# =========================

def main():
    print(f"🚀 Генерация статей: {ARTICLES_PER_RUN}")

    for i in range(ARTICLES_PER_RUN):
        print(f"\n--- {i + 1}/{ARTICLES_PER_RUN} ---")

        topic = generate_topic()
        print(f"🧠 Тема: {topic}")

        title, content = generate_article(topic)

        if not title or not content:
            print("⚠️ Статья пропущена.")
            continue

        save_article(title, content)

        time.sleep(2)

if __name__ == "__main__":
    main()
