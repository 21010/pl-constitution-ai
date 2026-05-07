import os
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.domain.interfaces import ITagGenerator

load_dotenv()


class TagList(BaseModel):
    tags: list[str] = Field(
        default_factory=list, min_items=3, max_items=5, description="Hasła powiązane z artykułem, najlepiej 3-5, ale minimum 3."
    )


class TagGenerator(ITagGenerator):
    """
    Generuje tagi przy użyciu Gemini Structured Output.
    """

    def __init__(self, model_id: str = "gemini-3.1-flash-lite-preview", api_key: str | None = None):
        self.model_id = model_id
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)

    def generate_tags(self, text: str, max_retries: int = 3) -> list[str]:
        prompt = f"""Przeanalizuj poniższy artykuł z Konstytucji RP i wyodrębnij od 3 do 5 kluczowych tematów (tagów).
Użyj konkretnych, polskich terminów prawnych lub ustrojowych.
Pomiń ogólne słowa jak 'prawo' czy 'konstytucja'.
Uwzględnij wszystkie występujące w artykule podmioty i zagadnienia.

ARTYKUŁ:
{text}"""

        for attempt in range(max_retries):
            try:
                if not self.api_key:
                    raise ValueError("Brak GEMINI_API_KEY w pliku .env")

                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=TagList, temperature=0.1),
                )

                if isinstance(response.parsed, TagList):
                    return [t.lower().strip() for t in response.parsed.tags[:5]]
                return ["konstytucja", "prawo", "ustrój"]

            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    wait_time = (attempt + 1) * 3
                    print(f"\n[Retry {attempt + 1}] API przeciążone. Czekam {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Ostrzeżenie: Błąd Gemini API podczas tagowania: {e}")
                    break

        return ["konstytucja", "prawo", "ustrój"]
