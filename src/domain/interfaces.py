from abc import ABC, abstractmethod
from .models import DocumentChunk


class IEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def embed_list(self, texts: list[str]) -> list[list[float]]:
        pass


class IVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: list[DocumentChunk]):
        pass

    @abstractmethod
    def search(self, query_text: str, k: int = 3) -> list[DocumentChunk]:
        pass


class ILLM(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_instruction: str | None = None) -> str:
        pass


class ITagGenerator(ABC):
    @abstractmethod
    def generate_tags(self, text: str) -> list[str]:
        pass


class IDocumentLoader(ABC):
    @abstractmethod
    def load_documents(self) -> list[DocumentChunk]:
        pass
