import chromadb
from chromadb.config import Settings
from typing import List
from src.domain.models import DocumentChunk
from src.domain.interfaces import IVectorStore, IEmbedder

class ChromaVectorStore(IVectorStore):
    def __init__(self, persist_directory: str, embedder: IEmbedder, collection_name: str = "constitution"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedder = embedder
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[DocumentChunk]):
        ids = [f"art_{doc.metadata['article']}" for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Łączymy treść z tagami dla lepszego wyszukiwania
        search_texts = [
            f"{doc.content}\nTagi: {', '.join(doc.metadata.get('tags', []))}" 
            for doc in documents
        ]
        
        # Używamy zoptymalizowanego kodowania wsadowego
        embeddings = self.embedder.embed_list(search_texts)
        
        print("Wysyłanie wektorów do ChromaDB...")
        self.collection.add(
            ids=ids,
            documents=[doc.content for doc in documents], # Zapisujemy czystą treść do wyświetlania
            metadatas=metadatas,
            embeddings=embeddings
        )

    def search(self, query_text: str, k: int = 7) -> List[DocumentChunk]:
        print(f"Szukanie w bazie wektorowej dla: '{query_text}'...")
        
        # Sprawdźmy ile mamy dokumentów w bazie
        count = self.collection.count()
        print(f"Aktualna liczba dokumentów w kolekcji: {count}")
        
        if count == 0:
            print("OSTRZEŻENIE: Baza jest pusta! Czy na pewno uruchomiłeś indeksowanie?")
            return []

        query_vector = self.embedder.embed_text(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )
        
        chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            print(f"Znaleziono {len(results['documents'][0])} pasujących fragmentów.")
            for i in range(len(results['documents'][0])):
                chunks.append(DocumentChunk(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i]
                ))
        else:
            print("Brak wyników wyszukiwania w ChromaDB.")
            
        return chunks
