import os
from dotenv import load_dotenv
from google import genai


def test_gemini_connection():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ BŁĄD: Nie znaleziono klucza GEMINI_API_KEY w pliku .env")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3.1-flash-lite-preview"

    print(f"Testing connection to {model_id} via new google-genai SDK...")
    try:
        response = client.models.generate_content(model=model_id, contents="Cześć, wymień dwa pierwsze artykuły Konstytucji RP.")
        print("✅ SUKCES: Połączenie z Gemini działa!")
        print(f"Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ BŁĄD: {e}")


if __name__ == "__main__":
    test_gemini_connection()
