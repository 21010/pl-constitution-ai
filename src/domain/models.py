from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    content: str = Field(..., description="Tekst artykułu")
    metadata: dict = Field(
        default_factory=dict, description="Metadane fragmentu dokumentu zawierające np. tytuł rozdziału, numer artykułu itp."
    )


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Odpowiedź na pytanie użytkownika")
    sources: list[str] = Field(default_factory=list, description="Lista źródeł (np. artykułów) wykorzystanych do udzielenia odpowiedzi")
    context_used: list[DocumentChunk] = Field(default_factory=list, description="Fragmenty dokumentów użyte do generowania odpowiedzi")
