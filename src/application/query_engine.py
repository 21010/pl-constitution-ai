from src.domain.interfaces import IVectorStore, ILLM
from src.domain.models import QueryResponse


class QueryEngine:
    def __init__(self, vector_store: IVectorStore, llm: ILLM):
        self.vector_store = vector_store
        self.llm = llm

    def _refine_query(self, question: str) -> str:
        """Przekształca pytanie użytkownika na zapytanie z terminologią prawniczą."""
        refinement_system_prompt = "Jesteś ekspertem od polskiego prawa. Przekształć pytanie użytkownika na 3-4 słowa kluczowe lub krótką frazę prawniczą, która pomoże znaleźć odpowiednie artykuły w Konstytucji RP. Zwróć TYLKO te słowa kluczowe, oddzielone przecinkami."

        try:
            refined = self.llm.generate_response(prompt=f"PYTANIE: {question}\nSŁOWA KLUCZOWE:", system_instruction=refinement_system_prompt)
            refined = refined.replace('"', "").replace("'", "").strip()
            print(f"Refinement: '{question}' -> '{refined}'")
            return refined
        except Exception as e:
            print(f"Błąd refinementu: {e}. Używam oryginalnego pytania.")
            return question

    def ask(self, question: str) -> QueryResponse:
        try:
            print(f"Otrzymano pytanie: {question}")

            # 1. Refinement - optymalizacja zapytania
            search_query = self._refine_query(question)

            # 2. Wyszukiwanie kontekstu w bazie
            context_chunks = self.vector_store.search(search_query, k=5)

            if not context_chunks:
                return QueryResponse(
                    answer="Nie znalazłem żadnych fragmentów Konstytucji pasujących do pytania w bazie danych.",
                    sources=[],
                    context_used=[],
                )

            # 3. Augumentacja promptu
            context_text = ""
            for i, c in enumerate(context_chunks):
                tags = c.metadata.get("tags", [])
                tags_str = f" [Tematy: {', '.join(tags)}]" if tags else ""
                context_text += f"--- FRAGMENT {i + 1} (Art. {c.metadata['article']}){tags_str} ---\n{c.content}\n\n"

            # Skonstruowany prompt
            prompt = f"""Na podstawie poniższego kontekstu z Konstytucji RP, odpowiedz na pytanie użytkownika.

KONTEKST:
{context_text}

PYTANIE:
{question}

ODPOWIEDŹ:"""

            # 4. Generowanie odpowiedzi
            answer = self.llm.generate_response(prompt)
            print(f"Odpowiedź: {answer}")

            # 5. Wyciaganie źródeł z kontekstu
            sources = sorted(list(set([f"Art. {c.metadata['article']}" for c in context_chunks])))

            return QueryResponse(answer=answer, sources=sources, context_used=context_chunks)
        except Exception as e:
            print(f"BŁĄD QueryEngine: {e}")
            raise e
