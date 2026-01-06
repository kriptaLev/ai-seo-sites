import os
import sys
from google import genai
from google.genai.errors import ClientError

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def check_quota():
    try:
        # минимальный, почти бесплатный запрос
        r = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents="Ответь одним словом: ok"
        )
        print("✅ КВОТА ДОСТУПНА")
        return True

    except ClientError as e:
        if e.status_code == 429:
            print("❌ КВОТА ИСЧЕРПАНА (429 RESOURCE_EXHAUSTED)")
            print("⏳ Нужно подождать, пока Google откроет лимиты")
            return False
        else:
            print("❌ ДРУГАЯ ОШИБКА API:")
            print(e)
            return False

if __name__ == "__main__":
    ok = check_quota()
    if not ok:
        sys.exit(1)
