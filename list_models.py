import os
from google import genai
from dotenv import load_dotenv


def list_available_models():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("BŁĄD: Nie znaleziono klucza GEMINI_API_KEY w pliku .env")
        return

    client = genai.Client(api_key=api_key)

    print("Pobieranie listy dostępnych modeli...")
    try:
        models = client.models.list()

        print(f"{'Model Name':<50}")
        print("-" * 50)

        for model in models:
            print(f"{model.name}")

    except Exception as e:
        print(f"BŁĄD podczas pobierania modeli: {e}")


if __name__ == "__main__":
    list_available_models()
