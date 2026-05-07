from abc import ABC, abstractmethod
from typing import List, Optional
from .models import DocumentChunk


class IEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_list(self, texts: List[str]) -> List[List[float]]:
        pass


class IVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[DocumentChunk]):
        pass

    @abstractmethod
    def search(self, query_text: str, k: int = 3) -> List[DocumentChunk]:
        pass


class ILLM(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass


class ITagGenerator(ABC):
    @abstractmethod
    def generate_tags(self, text: str) -> List[str]:
        pass


class IDocumentLoader(ABC):
    @abstractmethod
    def load_documents(self) -> List[DocumentChunk]:
        pass
