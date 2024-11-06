import unittest
from unittest.mock import Mock, patch
import torch
import pandas as pd

from data_pipeline.dags.create_embedding import (get_embedding, embed_to_str, embed)

class EmbeddingTests(unittest.TestCase):

    @patch("torch.cuda.empty_cache")
    def test_get_embedding_valid_text(self, mock_empty_cache):
        # Mock tokenizer, model, and device
        tokenizer = Mock()
        tokenizer.return_value = {"input_ids": torch.tensor([[1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1]])}
        model = Mock()
        model.return_value = Mock(last_hidden_state=torch.rand(1, 512, 768))
        device = torch.device("cpu")

        embedding = get_embedding("test text", tokenizer, model, device)
        self.assertIsNotNone(embedding)
        self.assertEqual(embedding.shape, (1, 768))  # Expected shape after mean pooling

    @patch("torch.cuda.empty_cache")
    def test_get_embedding_handles_exception(self, mock_empty_cache):
        tokenizer = Mock(side_effect=Exception("Tokenization error"))
        model = Mock()
        device = torch.device("cpu")

        embedding = get_embedding("test text", tokenizer, model, device)
        self.assertIsNone(embedding)  # Should return None if an exception is raised

    def test_embed_to_str_valid_embedding(self):
        # Mock embedding tensor
        embedding = torch.tensor([[1, 2, 3], [4, 5, 6]])
        embedding_str = embed_to_str(embedding)
        
        # Check the formatted output
        expected_output = "[[1, 2, 3],[4, 5, 6]]"
        self.assertEqual(embedding_str, expected_output)

    def test_embed_to_str_none_embedding(self):
        embedding_str = embed_to_str(None)
        self.assertEqual(embedding_str, "[]")

    @patch("torch.cuda.empty_cache")
    @patch("tqdm.tqdm", lambda x, desc: x)
    @patch("pandas.DataFrame.to_csv")
    def test_embed_batch_size_exception(self, mock_to_csv, mock_empty_cache):
        tokenizer = Mock()
        model = Mock()
        device = torch.device("cpu")
        data = pd.DataFrame({"input": ["sample text 1", "sample text 2"]})

        with self.assertRaises(Exception) as context:
            embed(data, tokenizer, model, device, batch_size=0)
        self.assertEqual(str(context.exception), "Batch size must be an integer greater than 0")

    @patch("torch.cuda.empty_cache")
    @patch("tqdm.tqdm", lambda x, desc: x)
    @patch("pandas.DataFrame.to_csv")
    def test_embed_handle_exception_during_embedding(self, mock_to_csv, mock_empty_cache):
        tokenizer = Mock(side_effect=Exception("Tokenization error"))
        model = Mock()
        device = torch.device("cpu")
        data = pd.DataFrame({"input": ["sample text 1", "sample text 2"]})

        with self.assertRaises(Exception) as context:
            embed(data, tokenizer, model, device, csv_filename="test_embeddings.csv", batch_size=1)
        self.assertIn("Mismatched lengths", str(context.exception))

if __name__ == "__main__":
    unittest.main()