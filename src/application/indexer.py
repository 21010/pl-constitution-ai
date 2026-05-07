import json
import os
from src.domain.interfaces import IVectorStore, IDocumentLoader, ITagGenerator
from tqdm import tqdm


class IndexerService:
    def __init__(
        self, loader: IDocumentLoader, vector_store: IVectorStore, tag_generator: ITagGenerator, processed_dir: str = "data/processed"
    ):
        self.loader = loader
        self.vector_store = vector_store
        self.tag_generator = tag_generator
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)

    def run(self):
        print("\n=== START PROCESU INDEKSOWANIA ===")
        try:
            # 1. Ładowanie dokumentów
            chunks = self.loader.load_documents()
            if not chunks:
                print("BŁĄD: Loader nie zwrócił żadnych danych.")
                return

            print(f"Pobrano {len(chunks)} artykułów. Rozpoczynam tagowanie (może to zająć kilka minut)...")

            # 2. Wzbogacanie metadanych o tagi
            for chunk in tqdm(chunks, desc="Tagowanie"):
                ai_tags = self.tag_generator.generate_tags(chunk.content)
                chunk.metadata["tags"] = list(set(ai_tags))

            # 3. Opcjonalny zapis do JSON
            self._save_checkpoint(chunks)

            # 4. Zapis do bazy wektorowej
            print(f"Zapisywanie {len(chunks)} wektorów w bazie danych...")
            self.vector_store.add_documents(chunks)

            print(f"SUKCES: Zaindeksowano {len(chunks)} artykułów.")
            print("=== KONIEC PROCESU INDEKSOWANIA ===\n")
        except Exception as e:
            print(f"KRYTYCZNY BŁĄD INDEKSOWANIA: {e}")

    def _save_checkpoint(self, chunks):
        """Pomocnicza metoda do zapisu stanu."""
        try:
            processed_path = os.path.join(self.processed_dir, "constitution_chunks.json")
            with open(processed_path, "w", encoding="utf-8") as f:
                json_data = [chunk.model_dump() for chunk in chunks]
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"Zapisano kopię zapasową w pliku JSON: {processed_path}")
        except Exception as e:
            print(f"Ostrzeżenie: Nie udało się zapisać kopii JSON: {e}")
