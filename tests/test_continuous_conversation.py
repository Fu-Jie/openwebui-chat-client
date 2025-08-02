import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Generator

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestContinuousConversation(unittest.TestCase):
    """Unit tests for continuous conversation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:3000"
        self.token = "test-token"
        self.default_model = "test-model:latest"
        
        # Create client with skip_model_refresh to prevent HTTP requests during initialization
        self.client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        self.client._auto_cleanup_enabled = False

    def test_continuous_chat_single_round(self):
        """Test continuous chat with only one round.""" 
        # Mock the chat manager's chat method
        with patch.object(self.client._chat_manager, 'chat') as mock_chat:
            mock_chat.return_value = {
                "response": "Test response",
                "chat_id": "test-chat-id",
                "message_id": "msg-id-123",
                "follow_ups": []
            }

            result = self.client.continuous_chat(
                initial_question="Hello",
                num_questions=1,
                chat_title="Test Continuous Chat"
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["total_rounds"], 1)
            self.assertEqual(len(result["conversation_history"]), 1)
            self.assertEqual(result["conversation_history"][0]["question"], "Hello")
            self.assertEqual(result["conversation_history"][0]["response"], "Test response")
            self.assertEqual(result["chat_id"], "test-chat-id")
            mock_chat.assert_called_once()

    def test_continuous_chat_multiple_rounds(self):
        """Test continuous chat with multiple rounds using follow-ups."""
        # Mock the chat manager's chat method
        with patch.object(self.client._chat_manager, 'chat') as mock_chat:
            # Setup mock to return different responses for each call
            mock_chat.side_effect = [
                {
                    "response": "First response",
                    "chat_id": "test-chat-id",
                    "message_id": "msg-id-1",
                    "follow_ups": ["What about this?", "Can you elaborate?"]
                },
                {
                    "response": "Second response", 
                    "chat_id": "test-chat-id",
                    "message_id": "msg-id-2",
                    "follow_ups": ["Another question?"]
                },
                {
                    "response": "Third response",
                    "chat_id": "test-chat-id", 
                    "message_id": "msg-id-3",
                    "follow_ups": []
                }
            ]

            with patch('random.choice') as mock_choice:
                # Mock random.choice to return predictable follow-ups
                mock_choice.side_effect = ["What about this?", "Another question?"]
                
                result = self.client.continuous_chat(
                    initial_question="Hello",
                    num_questions=3,
                    chat_title="Test Continuous Chat"
                )

            self.assertIsNotNone(result)
            self.assertEqual(result["total_rounds"], 3)
            self.assertEqual(len(result["conversation_history"]), 3)
            
            # Check first round
            self.assertEqual(result["conversation_history"][0]["question"], "Hello")
            self.assertEqual(result["conversation_history"][0]["response"], "First response")
            
            # Check second round (using follow-up)
            self.assertEqual(result["conversation_history"][1]["question"], "What about this?")
            self.assertEqual(result["conversation_history"][1]["response"], "Second response")
            
            # Check third round (using follow-up)
            self.assertEqual(result["conversation_history"][2]["question"], "Another question?")
            self.assertEqual(result["conversation_history"][2]["response"], "Third response")
            
            self.assertEqual(mock_chat.call_count, 3)

    def test_continuous_chat_no_follow_ups(self):
        """Test continuous chat when no follow-ups are provided."""
        # Mock the chat manager's chat method
        with patch.object(self.client._chat_manager, 'chat') as mock_chat:
            # Setup mock to return responses without follow-ups
            mock_chat.side_effect = [
                {
                    "response": "First response",
                    "chat_id": "test-chat-id",
                    "message_id": "msg-id-1",
                    "follow_ups": []  # No follow-ups
                },
                {
                    "response": "Second response", 
                    "chat_id": "test-chat-id",
                    "message_id": "msg-id-2",
                    "follow_ups": []
                }
            ]

            with patch('random.choice') as mock_choice:
                # Mock random.choice to return a generic follow-up
                mock_choice.return_value = "Can you explain that in more detail?"
                
                result = self.client.continuous_chat(
                    initial_question="Hello",
                    num_questions=2,
                    chat_title="Test Continuous Chat"
                )

            self.assertIsNotNone(result)
            self.assertEqual(result["total_rounds"], 2)
            
            # Check that generic follow-up was used
            self.assertEqual(result["conversation_history"][1]["question"], "Can you explain that in more detail?")
            self.assertEqual(mock_chat.call_count, 2)

    def test_continuous_chat_failure(self):
        """Test continuous chat when a round fails."""
        # Mock the chat manager's chat method
        with patch.object(self.client._chat_manager, 'chat') as mock_chat:
            # First round succeeds, second round fails by returning None
            mock_chat.side_effect = [
                {
                    "response": "First response",
                    "chat_id": "test-chat-id",
                    "message_id": "msg-id-1", 
                    "follow_ups": ["Follow up question"]
                },
                None  # Second round fails
            ]

            with patch('random.choice') as mock_choice:
                mock_choice.return_value = "Follow up question"
                
                result = self.client.continuous_chat(
                    initial_question="Hello",
                    num_questions=3,
                    chat_title="Test Continuous Chat"
                )

            self.assertIsNotNone(result)
            self.assertEqual(result["total_rounds"], 1)  # Only first round succeeded
            self.assertEqual(len(result["conversation_history"]), 1)
            self.assertEqual(mock_chat.call_count, 2)  # Two attempts were made

    def test_continuous_chat_invalid_num_questions(self):
        """Test continuous chat with invalid number of questions."""
        result = self.client.continuous_chat(
            initial_question="Hello",
            num_questions=0,
            chat_title="Test Continuous Chat"
        )

        self.assertIsNone(result)

    def test_continuous_parallel_chat_success(self):
        """Test continuous parallel chat with multiple models."""
        # Mock the chat manager's parallel_chat method
        with patch.object(self.client._chat_manager, 'parallel_chat') as mock_parallel_chat:
            # Mock parallel_chat to return different responses for each call
            mock_parallel_chat.side_effect = [
                {
                    "chat_id": "test-chat-id",
                    "responses": {
                        "model1": {
                            "content": "Model 1 response",
                            "sources": [],
                            "follow_ups": ["Question 1", "Question 2"]
                        },
                        "model2": {
                            "content": "Model 2 response",
                            "sources": [],
                            "follow_ups": ["Question 3"]
                        }
                    }
                },
                {
                    "chat_id": "test-chat-id",
                    "responses": {
                        "model1": {
                            "content": "Model 1 second response",
                            "sources": [],
                            "follow_ups": []
                        },
                        "model2": {
                            "content": "Model 2 second response",
                            "sources": [],
                            "follow_ups": []
                        }
                    }
                }
            ]

            with patch('random.choice') as mock_choice:
                mock_choice.return_value = "Question 1"
                
                result = self.client.continuous_parallel_chat(
                    initial_question="Hello",
                    num_questions=2,
                    chat_title="Test Continuous Parallel Chat",
                    model_ids=["model1", "model2"]
                )

            self.assertIsNotNone(result)
            self.assertEqual(result["total_rounds"], 2)
            self.assertEqual(len(result["conversation_history"]), 2)
            self.assertIn("model_ids", result)
            self.assertEqual(result["model_ids"], ["model1", "model2"])
            
            # Check that follow-ups were collected from all models
            self.assertEqual(result["conversation_history"][0]["follow_ups"], ["Question 1", "Question 2", "Question 3"])
            self.assertEqual(mock_parallel_chat.call_count, 2)

    def test_continuous_parallel_chat_empty_model_ids(self):
        """Test continuous parallel chat with empty model IDs."""
        result = self.client.continuous_parallel_chat(
            initial_question="Hello",
            num_questions=2,
            chat_title="Test Chat",
            model_ids=[]
        )

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "_ask_stream")
    def test_continuous_stream_chat_success(self, mock_ask_stream, mock_find_create):
        """Test continuous stream chat functionality."""
        # Setup mocks
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}, "models": ["test-model"]}
        }
        
        # Mock streaming generators
        def first_stream():
            yield "Hello"
            yield " world"
            yield "!"
            
        def second_stream():
            yield "Second"
            yield " response"

        mock_ask_stream.side_effect = [
            ("Hello world!", [], ["Follow up question"]),  # First round
            ("Second response", [], [])  # Second round
        ]

        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "Follow up question"
            
            # Collect streaming results
            streaming_results = []
            final_result = None
            
            for chunk in self.client.continuous_stream_chat(
                initial_question="Hello",
                num_questions=2,
                chat_title="Test Continuous Stream Chat"
            ):
                streaming_results.append(chunk)
                if chunk.get("type") == "conversation_complete":
                    final_result = chunk["summary"]

        self.assertIsNotNone(final_result)
        self.assertTrue(len(streaming_results) > 0)
        
        # Check for expected chunk types
        chunk_types = [chunk.get("type") for chunk in streaming_results]
        self.assertIn("round_start", chunk_types)
        self.assertIn("round_complete", chunk_types)
        self.assertIn("conversation_complete", chunk_types)
        
        self.assertEqual(mock_ask_stream.call_count, 2)
        mock_find_create.assert_called_once_with("Test Continuous Stream Chat")

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")  
    @patch.object(OpenWebUIClient, "_ask")
    def test_continuous_chat_with_all_parameters(self, mock_ask, mock_find_create):
        """Test continuous chat with all optional parameters."""
        # Setup mocks
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}, "models": ["custom-model"]}
        }
        mock_ask.return_value = ("Hi there", "msg-id-123", None)

        result = self.client.continuous_chat(
            initial_question="Hello",
            num_questions=1,
            chat_title="Test Chat",
            model_id="custom-model",
            folder_name="Test Folder",
            image_paths=["test.png"],
            tags=["test", "continuous"],
            rag_files=["doc.pdf"],
            rag_collections=["knowledge"],
            tool_ids=["tool1", "tool2"],
            enable_auto_tagging=True,
            enable_auto_titling=True
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["total_rounds"], 1)
        mock_find_create.assert_called_once_with("Test Chat")
        mock_ask.assert_called_once()


if __name__ == "__main__":
    unittest.main()