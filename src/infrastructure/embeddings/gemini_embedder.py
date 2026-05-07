import os
import time
from google import genai
from google.genai import types
from src.domain.interfaces import IEmbedder
from dotenv import load_dotenv

load_dotenv()


class GeminiEmbedder(IEmbedder):
    """
    Implementacja IEmbedder wykorzystująca Google Gemini do generowania wektorów osadzania tekstu.
    Obsługuje dynamiczne określanie wymiaru modelu oraz prostą logikę ponawiania przy błędach związanych z limitami API.
    """

    def __init__(self, model_name: str = "text-embedding-004", api_key: str | None = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Brak GEMINI_API_KEY w środowisku lub pliku .env")

        self.client = genai.Client(api_key=self.api_key)
        self._dimension: int | None = None

    def _get_dimension(self, sample_text: str = "test") -> int:
        """Dynamicznie określa wymiar modelu przy pierwszym użyciu."""
        if self._dimension is None:
            res = self.client.models.embed_content(model=self.model_name, contents=sample_text)
            if res and res.embeddings and res.embeddings[0].values is not None:
                self._dimension = len(res.embeddings[0].values)
            else:
                self._dimension = 768

        return self._dimension

    def _clean_text(self, text: str) -> str:
        """Usuwa zbędne białe znaki."""
        return " ".join(text.split())

    def embed_text(self, text: str) -> list[float]:
        clean_text = self._clean_text(text)
        dim = self._get_dimension(clean_text)

        try:
            result = self.client.models.embed_content(
                model=self.model_name, contents=clean_text, config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )

            if result and result.embeddings:
                values = result.embeddings[0].values
                if values is not None:
                    return values
            return [0.0] * dim
        except Exception as e:
            print(f"Błąd Gemini Embedding (single): {e}")
            return [0.0] * dim

    def embed_list(self, texts: list[str]) -> list[list[float]]:
        """Koduje listę tekstów indywidualnie (SDK Gemini nie wspiera prostego batchingu w embed_content)."""
        if not texts:
            return []

        print(f"Generowanie wektorów dla {len(texts)} fragmentów...")
        dim = self._get_dimension(texts[0])
        all_embeddings = []

        for i, text in enumerate(texts):
            clean_text = self._clean_text(text)

            # Próba z ponawianiem (retry logic)
            success = False
            for attempt in range(3):
                try:
                    result = self.client.models.embed_content(
                        model=self.model_name, contents=clean_text, config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                    )

                    if result and result.embeddings:
                        values = result.embeddings[0].values
                        if values is not None:
                            all_embeddings.append(values)
                            success = True
                            break
                except Exception as e:
                    if "429" in str(e) and attempt < 2:
                        time.sleep(1)  # Krótkie czekanie przy RPM
                        continue
                    print(f"Błąd przy fragmencie {i}: {e}")
                    break

            if not success:
                all_embeddings.append([0.0] * dim)

            if (i + 1) % 50 == 0:
                print(f"  Postęp: {i + 1}/{len(texts)}...")

        return all_embeddings
