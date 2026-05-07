import chromadb
import numpy as np
from typing import Any
from src.domain.models import DocumentChunk
from src.domain.interfaces import IVectorStore, IEmbedder


class ChromaVectorStore(IVectorStore):
    def __init__(self, persist_directory: str, embedder: IEmbedder, collection_name: str = "constitution"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedder = embedder
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    def add_documents(self, documents: list[DocumentChunk]):
        ids = [f"art_{doc.metadata['article']}" for doc in documents]

        # Konwertujemy metadane na format akceptowany przez ChromaDB (płaskie słowniki)
        metadatas: list[Any] = []
        for doc in documents:
            clean_meta: dict[str, Any] = {}
            for k, v in doc.metadata.items():
                if isinstance(v, list):
                    clean_meta[k] = ", ".join(map(str, v))
                else:
                    clean_meta[k] = v
            metadatas.append(clean_meta)

        # Łączymy treść z tagami dla lepszego wyszukiwania
        search_texts = [f"{doc.content}\nTagi: {', '.join(doc.metadata.get('tags', []))}" for doc in documents]

        # Używamy zoptymalizowanego kodowania wsadowego
        embeddings_list = self.embedder.embed_list(search_texts)
        embeddings = np.array(embeddings_list, dtype=np.float32)

        print("Wysyłanie wektorów do ChromaDB...")
        self.collection.add(
            ids=ids,
            documents=[doc.content for doc in documents],  # Zapisujemy czystą treść do wyświetlania
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(self, query_text: str, k: int = 7) -> list[DocumentChunk]:
        print(f"Szukanie w bazie wektorowej dla: '{query_text}'...")

        # Sprawdźmy ile mamy dokumentów w bazie
        count = self.collection.count()
        print(f"Aktualna liczba dokumentów w kolekcji: {count}")

        if count == 0:
            print("OSTRZEŻENIE: Baza jest pusta! Czy na pewno uruchomiłeś indeksowanie?")
            return []

        query_vector = self.embedder.embed_text(query_text)
        query_embeddings = [np.array(query_vector, dtype=np.float32)]

        results = self.collection.query(query_embeddings=query_embeddings, n_results=k)

        chunks = []
        if results["documents"] and len(results["documents"][0]) > 0:
            print(f"Znaleziono {len(results['documents'][0])} pasujących fragmentów.")
            for i in range(len(results["documents"][0])):
                doc_content = results["documents"][0][i]
                doc_metadata = {}

                if results["metadatas"] and len(results["metadatas"][0]) > i:
                    doc_metadata = dict(results["metadatas"][0][i])

                chunks.append(DocumentChunk(content=doc_content, metadata=doc_metadata))
        else:
            print("Brak wyników wyszukiwania w ChromaDB.")

        return chunks
