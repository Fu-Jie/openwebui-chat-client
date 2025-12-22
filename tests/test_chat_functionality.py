import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
import uuid
from io import BytesIO

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientChatFunctionality(unittest.TestCase):
    """Unit tests for OpenWebUIClient chat-related functionality."""

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

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "_ask")
    def test_chat_success(self, mock_ask, mock_find_create, mock_post):
        """Test successful chat operation."""
        # Setup mocks
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}, "models": ["test-model"]}
        }
        mock_ask.return_value = ("Test response", "msg-id-123", None)

        result = self.client.chat(question="Hello, world!", chat_title="Test Chat")

        self.assertIsNotNone(result)
        self.assertEqual(result["response"], "Test response")
        self.assertEqual(result["chat_id"], "test-chat-id")
        self.assertEqual(result["message_id"], "msg-id-123")
        mock_find_create.assert_called_once_with("Test Chat")
        mock_ask.assert_called_once()

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_chat_no_chat_id(self, mock_find_create):
        """Test chat operation when chat_id is None."""
        self.client.chat_id = None

        result = self.client.chat(question="Hello, world!", chat_title="Test Chat")

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "_ask")
    @patch.object(OpenWebUIClient, "set_chat_tags")
    def test_chat_with_tags(self, mock_set_tags, mock_ask, mock_find_create):
        """Test chat operation with tags."""
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}, "models": ["test-model"]}
        }
        mock_ask.return_value = ("Test response", "msg-id-123", None)

        result = self.client.chat(
            question="Hello, world!", chat_title="Test Chat", tags=["tag1", "tag2"]
        )

        self.assertIsNotNone(result)
        mock_set_tags.assert_called_once_with("test-chat-id", ["tag1", "tag2"])

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "get_folder_id_by_name")
    @patch.object(OpenWebUIClient, "create_folder")
    @patch.object(OpenWebUIClient, "move_chat_to_folder")
    @patch.object(OpenWebUIClient, "_ask")
    def test_chat_with_folder(
        self, mock_ask, mock_move, mock_create_folder, mock_get_folder, mock_find_create
    ):
        """Test chat operation with folder management."""
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "folder_id": "old-folder",
            "chat": {"history": {"messages": {}}, "models": ["test-model"]},
        }
        mock_get_folder.return_value = "new-folder-id"
        mock_ask.return_value = ("Test response", "msg-id-123", None)

        result = self.client.chat(
            question="Hello, world!", chat_title="Test Chat", folder_name="Test Folder"
        )

        self.assertIsNotNone(result)
        mock_get_folder.assert_called_once_with("Test Folder")
        mock_move.assert_called_once_with("test-chat-id", "new-folder-id")

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "_get_single_model_response_in_parallel")
    @patch.object(OpenWebUIClient, "_update_remote_chat")
    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    @patch("openwebui_chat_client.openwebui_chat_client.as_completed")
    def test_parallel_chat_success(
        self,
        mock_as_completed,
        mock_executor,
        mock_update,
        mock_get_response,
        mock_find_create,
    ):
        """Test successful parallel chat operation."""
        # Setup
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {
                "history": {"messages": {}, "currentId": None},
                "models": ["model1", "model2"],
            }
        }

        # Mock executor and futures
        mock_future1 = Mock()
        mock_future1.result.return_value = ("Response 1", [], None)  # content, sources, follow_ups
        mock_future2 = Mock()
        mock_future2.result.return_value = ("Response 2", [], None)  # content, sources, follow_ups

        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
        mock_executor_instance.__exit__ = Mock(return_value=None)
        mock_executor.return_value = mock_executor_instance

        # Mock as_completed to return futures in order
        mock_as_completed.return_value = [mock_future1, mock_future2]
        mock_update.return_value = True
        
        # Configure the mocked method to return appropriate values for each model
        mock_get_response.side_effect = [
            ("Response 1", [], None),  # For model1
            ("Response 2", [], None),  # For model2
        ]

        result = self.client.parallel_chat(
            question="Hello, world!",
            chat_title="Test Chat",
            model_ids=["model1", "model2"],
        )

        self.assertIsNotNone(result)
        self.assertIn("responses", result)
        self.assertEqual(len(result["responses"]), 2)
        self.assertIn("model1", result["responses"])
        self.assertIn("model2", result["responses"])

    def test_parallel_chat_empty_model_ids(self):
        """Test parallel chat with empty model IDs."""
        result = self.client.parallel_chat(
            question="Hello, world!", chat_title="Test Chat", model_ids=[]
        )

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    @patch.object(OpenWebUIClient, "_ask_stream")
    @patch.object(OpenWebUIClient, "set_chat_tags")
    def test_stream_chat_success(
        self, mock_set_tags, mock_ask_stream, mock_find_create
    ):
        """Test successful streaming chat operation."""
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}, "models": ["test-model"]}
        }

        # Mock the generator and return value
        def mock_stream_generator():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"
            return "Full response", [], None  # Return 3 values: content, sources, follow_ups

        mock_ask_stream.return_value = mock_stream_generator()

        # Collect all yielded chunks and final return
        chunks = []
        final_result = None

        stream_gen = self.client.stream_chat(
            question="Hello, world!", chat_title="Test Chat", tags=["stream", "test"]
        )

        try:
            while True:
                chunk = next(stream_gen)
                chunks.append(chunk)
        except StopIteration as e:
            final_result = e.value

        self.assertEqual(chunks, ["chunk1", "chunk2", "chunk3"])
        self.assertIsInstance(final_result, dict)
        self.assertEqual(final_result.get("response"), "Full response")
        self.assertEqual(final_result.get("sources"), [])
        self.assertIsNone(final_result.get("follow_ups"))
        mock_set_tags.assert_called_once_with("test-chat-id", ["stream", "test"])

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_stream_chat_no_chat_id(self, mock_find_create):
        """Test streaming chat when chat_id is None."""
        self.client.chat_id = None

        stream_gen = self.client.stream_chat(
            question="Hello, world!", chat_title="Test Chat"
        )

        # Should yield nothing and end immediately
        chunks = list(stream_gen)
        self.assertEqual(len(chunks), 0)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_success(self, mock_post):
        """Test successful model completion request."""
        chat_id = "test-chat-id"
        messages = [{"role": "user", "content": "Hello"}]

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}],
            "sources": [{"title": "Source 1", "url": "http://example.com"}],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        content, sources = self.client._get_model_completion(chat_id, messages)

        self.assertEqual(content, "Hello! How can I help you?")
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["title"], "Source 1")

        mock_post.assert_called_once_with(
            f"{self.base_url}/api/chat/completions",
            json={"model": self.default_model, "messages": messages, "stream": False,
                    "parent_message": {}
                    },    
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_with_rag(self, mock_post):
        """Test model completion with RAG payload."""
        chat_id = "test-chat-id"
        messages = [{"role": "user", "content": "Hello"}]
        rag_payload = [{"type": "file", "id": "file123"}]

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response with RAG"}}],
            "sources": [],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        content, sources = self.client._get_model_completion(
            chat_id, messages, rag_payload
        )

        self.assertEqual(content, "Response with RAG")

        # Check that the payload included files
        call_args = mock_post.call_args
        self.assertIn("files", call_args[1]["json"])
        self.assertEqual(call_args[1]["json"]["files"], rag_payload)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_with_tools(self, mock_post):
        """Test model completion with tool IDs."""
        chat_id = "test-chat-id"
        messages = [{"role": "user", "content": "Hello"}]
        tool_ids = ["tool1", "tool2"]

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response with tools"}}],
            "sources": [],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        content, sources = self.client._get_model_completion(
            chat_id, messages, tool_ids=tool_ids
        )

        self.assertEqual(content, "Response with tools")

        # Check that the payload included tool_ids
        call_args = mock_post.call_args
        self.assertIn("tool_ids", call_args[1]["json"])
        self.assertEqual(call_args[1]["json"]["tool_ids"], tool_ids)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_http_error(self, mock_post):
        """Test model completion with HTTP error."""
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.text = "Internal Server Error"
        mock_post.side_effect = HTTPError(response=mock_response)

        with self.assertRaises(HTTPError):
            self.client._get_model_completion("chat_id", [])

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_malformed_response(self, mock_post):
        """Test model completion with malformed response."""
        mock_response = Mock()
        mock_response.json.return_value = {"malformed": "response"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        content, sources = self.client._get_model_completion("chat_id", [])

        self.assertIsNone(content)
        self.assertEqual(sources, [])

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_get_model_completion_stream_success(self, mock_post):
        """Test successful streaming model completion."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        # Mock the streaming lines
        stream_lines = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n',
            b'data: {"choices": [{"delta": {"content": " there"}}]}\n',
            b'data: {"choices": [{"delta": {"content": "!"}}]}\n',
            b'data: {"sources": [{"title": "Test Source"}]}\n',
            b"data: [DONE]\n",
        ]

        mock_response.iter_lines.return_value = stream_lines
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_post.return_value = mock_response

        # Get the generator
        stream_gen = self.client._get_model_completion_stream("chat_id", [])

        # Collect chunks and final sources
        chunks = []
        sources = None
        try:
            while True:
                chunk = next(stream_gen)
                chunks.append(chunk)
        except StopIteration as e:
            sources = e.value

        self.assertEqual(chunks, ["Hello", " there", "!"])
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["title"], "Test Source")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_upload_file_success(self, mock_post):
        """Test successful file upload."""
        file_path = "/tmp/test.pdf"
        file_content = b"test file content"

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "file123",
            "name": "test.pdf",
            "type": "application/pdf",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = file_content
                mock_open.return_value.__enter__.return_value = mock_file

                result = self.client._upload_file(file_path)

                self.assertIsNotNone(result)
                self.assertEqual(result["id"], "file123")
                self.assertEqual(result["name"], "test.pdf")

    def test_upload_file_not_found(self):
        """Test file upload when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            result = self.client._upload_file("/nonexistent/file.pdf")

            self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_set_chat_tags_success(self, mock_get, mock_post):
        """Test successful chat tag setting."""
        chat_id = "test-chat-id"
        tags = ["tag1", "tag2", "existing-tag"]

        # Mock getting existing tags
        mock_get_response = Mock()
        mock_get_response.json.return_value = [{"name": "existing-tag"}]
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response

        # Mock posting new tags
        mock_post_response = Mock()
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        self.client.set_chat_tags(chat_id, tags)

        # Should call get once to fetch existing tags
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/chats/{chat_id}/tags",
            headers=self.client.json_headers,
        )

        # Should call post twice for the two new tags (not the existing one)
        self.assertEqual(mock_post.call_count, 2)

        # Check the calls were made with correct tag names
        post_calls = mock_post.call_args_list
        posted_tags = [call[1]["json"]["name"] for call in post_calls]
        self.assertIn("tag1", posted_tags)
        self.assertIn("tag2", posted_tags)
        self.assertNotIn("existing-tag", posted_tags)

    def test_set_chat_tags_empty_list(self):
        """Test setting empty tag list (should do nothing)."""
        with patch(
            "openwebui_chat_client.openwebui_chat_client.requests.Session.get"
        ) as mock_get:
            self.client.set_chat_tags("chat_id", [])
            mock_get.assert_not_called()

    @patch.object(OpenWebUIClient, "_load_chat_details")
    @patch.object(OpenWebUIClient, "_update_remote_chat")
    def test_switch_chat_model_success(self, mock_update, mock_load):
        """Test successful chat model switching."""
        chat_id = "test-chat-id"
        new_model = "new-model:latest"

        # Mock loading chat details
        mock_load.return_value = True
        self.client.chat_object_from_server = {"chat": {"models": ["old-model:latest"]}}

        # Mock updating remote chat
        mock_update.return_value = True

        result = self.client.switch_chat_model(chat_id, new_model)

        self.assertTrue(result)
        self.assertEqual(self.client.model_id, new_model)
        self.assertEqual(
            self.client.chat_object_from_server["chat"]["models"], [new_model]
        )
        mock_load.assert_called_once_with(chat_id)
        mock_update.assert_called_once()

    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_switch_chat_model_same_model(self, mock_load):
        """Test switching to the same model (should return True without updating)."""
        chat_id = "test-chat-id"
        current_model = "current-model:latest"

        mock_load.return_value = True
        self.client.chat_object_from_server = {"chat": {"models": [current_model]}}

        result = self.client.switch_chat_model(chat_id, current_model)

        self.assertTrue(result)

    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_switch_chat_model_load_failure(self, mock_load):
        """Test chat model switching when loading chat details fails."""
        mock_load.return_value = False

        result = self.client.switch_chat_model("chat_id", "new-model")

        self.assertFalse(result)

    def test_switch_chat_model_invalid_model_ids(self):
        """Test chat model switching with invalid model IDs."""
        # Test with non-string, non-list input
        result1 = self.client.switch_chat_model("chat_id", 123)
        self.assertFalse(result1)

        # Test with empty list
        result2 = self.client.switch_chat_model("chat_id", [])
        self.assertFalse(result2)


if __name__ == "__main__":
    unittest.main()
