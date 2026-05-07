import unittest
from unittest.mock import MagicMock
from src.application.query_engine import QueryEngine
from src.domain.models import DocumentChunk

class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        self.mock_vector_store = MagicMock()
        self.mock_llm = MagicMock()
        self.query_engine = QueryEngine(vector_store=self.mock_vector_store, llm=self.mock_llm)

    def test_query_engine_refines_and_searches(self):
        # Setup
        question = "Kto rządzi?"
        refined_query = "władza wykonawcza, prezydent, premier"
        self.mock_llm.generate_response.side_effect = [refined_query, "Prezydent i Premier."]
        
        self.mock_vector_store.search.return_value = [
            DocumentChunk(content="Treść Art. 1", metadata={"article": "1", "tags": ["władza"]})
        ]
        
        # Execute
        response = self.query_engine.ask(question)
        
        # Assert
        self.assertEqual(response.answer, "Prezydent i Premier.")
        self.assertEqual(response.sources, ["Art. 1"])
        
        # Check if refinement was called
        self.assertEqual(self.mock_llm.generate_response.call_count, 2)
        
        # First call should be refinement with system_instruction
        _, kwargs = self.mock_llm.generate_response.call_args_list[0]
        self.assertIn("system_instruction", kwargs)
        self.assertIn("Przekształć pytanie", kwargs["system_instruction"])
        
        # Search should use refined query
        self.mock_vector_store.search.assert_called_once_with(refined_query, k=5)

    def test_query_engine_no_results(self):
        # Setup
        self.mock_llm.generate_response.return_value = "keywords"
        self.mock_vector_store.search.return_value = []
        
        # Execute
        response = self.query_engine.ask("Coś czego nie ma")
        
        # Assert
        self.assertIn("Nie znalazłem", response.answer)
        self.assertEqual(response.sources, [])

if __name__ == '__main__':
    unittest.main()
