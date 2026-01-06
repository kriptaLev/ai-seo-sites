import os
import sys
from google import genai
from google.genai import errors

def check_quota():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    try:
        client.models.generate_content(
            model="gemini-2.0-flash",
            contents="ping"
        )
        print("✅ КВОТА ДОСТУПНА")
        return True

    except errors.ClientError as e:
        msg = str(e)

        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            print("❌ КВОТА ИСЧЕРПАНА (429 RESOURCE_EXHAUSTED)")
            return False

        print("❌ ДРУГАЯ ОШИБКА API:")
        print(msg)
        sys.exit(1)


if __name__ == "__main__":
    ok = check_quota()
    if not ok:
        sys.exit(0)  # ❗ ВАЖНО: НЕ РОНЯЕМ WORKFLOW
