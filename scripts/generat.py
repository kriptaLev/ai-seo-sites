import google.generativeai as genai
import json, os, random, re, uuid, time

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------- CONFIG ----------
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

ARTICLES_COUNT = config["articles_per_run"]
MAX_NARROW = config["max_articles_per_narrow_topic"]
MAX_BROAD = config["max_articles_per_broad_topic"]

# ---------- MEMORY ----------
MEMORY_FILE = "topic_memory.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        topic_memory = json.load(f)
else:
    topic_memory = {}

os.makedirs("pages", exist_ok=True)

# ---------- HELPERS ----------
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^а-яa-z0-9 ]', '', text)
    return "-".join(text.split())[:70]

def unique_filename(topic):
    return f"{slugify(topic)}-{uuid.uuid4().hex[:6]}.md"

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(topic_memory, f, ensure_ascii=False, indent=2)

# ---------- TOPIC GENERATION ----------
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
