import unittest
import os
import shutil
from unittest.mock import MagicMock
from src.application.indexer import IndexerService
from src.domain.models import DocumentChunk


class TestIndexerService(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_processed"
        self.mock_loader = MagicMock()
        self.mock_vector_store = MagicMock()
        self.mock_tag_generator = MagicMock()
        self.indexer_service = IndexerService(
            loader=self.mock_loader, vector_store=self.mock_vector_store, tag_generator=self.mock_tag_generator, processed_dir=self.test_dir
        )

    def tearDown(self):
        # Clean up test directory (with basic error handling for Windows file locks)
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                print(f"Ostrzeżenie: Nie udało się usunąć folderu testowego {self.test_dir} (może być używany).")

    def test_indexer_service_workflow(self):
        # Setup
        chunks = [DocumentChunk(content="Art 1 content", metadata={"article": "1", "chapter": "I"})]
        self.mock_loader.load_documents.return_value = chunks
        self.mock_tag_generator.generate_tags.return_value = ["tag1", "tag2"]

        # Execute
        # Suppress prints for cleaner test output if desired, but here we just run it
        self.indexer_service.run()

        # Assert
        self.mock_loader.load_documents.assert_called_once()
        self.mock_tag_generator.generate_tags.assert_called_once_with("Art 1 content")

        # Verify tags were added to metadata (as a set to handle non-deterministic order)
        self.assertEqual(set(chunks[0].metadata["tags"]), {"tag1", "tag2"})

        # Verify documents were added to vector store
        self.mock_vector_store.add_documents.assert_called_once_with(chunks)


if __name__ == "__main__":
    unittest.main()
