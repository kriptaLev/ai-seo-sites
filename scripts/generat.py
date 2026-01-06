import google.generativeai as genai
import json
import os
import re

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

with open("topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

os.makedirs("pages", exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^а-яa-z0-9 ]', '', text)
    return "-".join(text.split())[:80]

for topic in topics:
    prompt = f"""
Ты опытный крипто-эксперт и автор, который пишет живые статьи для людей.

ЗАДАЧА:
Напиши полноценную, полезную и ЧЕЛОВЕЧЕСКУЮ статью на русском языке на тему:

«{topic}»

ТРЕБОВАНИЯ К ТЕКСТУ:
- 2000–3000 слов
- стиль: эксперт объясняет простым языком
- текст должен читаться легко и естественно
- логика важнее структуры
- структура должна появляться ТОЛЬКО если уместна
- разрешены H2 и H3, но они не обязательны
- можно использовать списки, примеры, подзаголовки
- без шаблонных блоков
- без одинаковых повторяющихся разделов
- без воды и общих фраз
- без выдуманных фактов
- информационный формат (легально для РФ)

ПИШИ КАК ЧЕЛОВЕК, А НЕ КАК ШАБЛОННЫЙ SEO-БОТ.

НЕ ИСПОЛЬЗУЙ:
- одинаковые вступления
- клише
- фразы типа "В этой статье мы рассмотрим"
- маркированные списки без смысла

РЕЗУЛЬТАТ:
Один цельный, связный текст в формате Markdown.
"""

    response = model.generate_content(prompt)
    text = response.text.replace("**", "").strip()

    article = f"# {topic}\n\n{text}"

    filename = f"pages/{slugify(topic)}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)

print("Генерация живых крипто-статей завершена")
