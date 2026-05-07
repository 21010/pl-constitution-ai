import os
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.domain.interfaces import ILLM

load_dotenv()


class GeminiLLM(ILLM):
    """
    Implementacja LLM wykorzystująca najnowsze API Google Gemini (google-genai).
    """

    def __init__(self, model_id: str = "gemini-1.5-flash", api_key: str | None = None):
        self.model_id = model_id
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.system_instruction = "Jesteś ekspertem od Konstytucji RP. Odpowiadaj WYŁĄCZNIE na podstawie podanego kontekstu. Zawsze podawaj numer artykułu. Jeśli nie znajdziesz odpowiedzi — powiedz 'Nie znalazłem odpowiedzi w Konstytucji.'"

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        try:
            if not self.api_key:
                raise ValueError("Brak GEMINI_API_KEY w pliku .env")

            # Używamy przekazanej instrukcji lub domyślnej
            final_instruction = system_instruction or self.system_instruction

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=final_instruction, temperature=0.1),
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            return f"Błąd Gemini API: {str(e)}"
