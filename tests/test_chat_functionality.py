import unittest
from unittest.mock import Mock, patch

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
        self.client._base_client._test_mode = True
        self.client._auto_cleanup_enabled = False

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.chat")
    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_chat_success(self, mock_find_create, mock_chat_manager_chat):
        """Test successful chat operation."""
        # Setup mocks
        self.client.chat_id = "test-chat-id"
        from openwebui_chat_client.models import ChatResponse
        mock_chat_manager_chat.return_value = ChatResponse(
            content="Test response",
            chat_id="test-chat-id",
            message_id="msg-id-123"
        )

        result = self.client.chat(question="Hello, world!", chat_title="Test Chat")

        self.assertIsNotNone(result)
        self.assertEqual(result.content, "Test response")
        self.assertEqual(result.chat_id, "test-chat-id")
        self.assertEqual(result.message_id, "msg-id-123")
        mock_chat_manager_chat.assert_called_once()

    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_chat_no_chat_id(self, mock_find_create):
        """Test chat operation when chat_id is None."""
        self.client.chat_id = None

        result = self.client.chat(question="Hello, world!", chat_title="Test Chat")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.chat")
    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_chat_with_tags(self, mock_find_create, mock_chat_manager_chat):
        """Test chat operation with tags."""
        self.client.chat_id = "test-chat-id"
        from openwebui_chat_client.models import ChatResponse
        mock_chat_manager_chat.return_value = ChatResponse(
            content="Test response",
            chat_id="test-chat-id",
            message_id="msg-id-123"
        )

        result = self.client.chat(
            question="Hello, world!", chat_title="Test Chat", tags=["tag1", "tag2"]
        )

        self.assertIsNotNone(result)
        mock_chat_manager_chat.assert_called_once()
        # Verify tags were passed in kwargs
        args, kwargs = mock_chat_manager_chat.call_args
        self.assertEqual(kwargs.get("tags"), ["tag1", "tag2"])

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.chat")
    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_chat_with_folder(self, mock_find_create, mock_chat_manager_chat):
        """Test chat operation with folder management."""
        self.client.chat_id = "test-chat-id"
        from openwebui_chat_client.models import ChatResponse
        mock_chat_manager_chat.return_value = ChatResponse(
            content="Test response",
            chat_id="test-chat-id",
            message_id="msg-id-123"
        )

        result = self.client.chat(
            question="Hello, world!", chat_title="Test Chat", folder_name="Test Folder"
        )

        self.assertIsNotNone(result)
        mock_chat_manager_chat.assert_called_once()
        # Verify folder_name was passed in kwargs
        args, kwargs = mock_chat_manager_chat.call_args
        self.assertEqual(kwargs.get("folder_name"), "Test Folder")

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.parallel_chat")
    def test_parallel_chat_success(self, mock_parallel):
        """Test successful parallel chat operation."""
        from openwebui_chat_client.models import ParallelChatResponse, ChatResponse
        
        mock_response = ParallelChatResponse(
            responses={
                "model1": ChatResponse(content="Response 1", chat_id="test-chat-id", message_id="msg1"),
                "model2": ChatResponse(content="Response 2", chat_id="test-chat-id", message_id="msg2")
            },
            chat_id="test-chat-id",
            message_ids={"model1": "msg1", "model2": "msg2"}
        )
        mock_parallel.return_value = mock_response

        result = self.client.parallel_chat(
            question="Hello, world!",
            chat_title="Test Chat",
            model_ids=["model1", "model2"],
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(result.responses), 2)
        self.assertEqual(result.responses["model1"].content, "Response 1")

    def test_parallel_chat_empty_model_ids(self):
        """Test parallel chat with empty model IDs."""
        result = self.client.parallel_chat(
            question="Hello, world!", chat_title="Test Chat", model_ids=[]
        )

        self.assertIsNone(result)

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.stream_chat")
    @patch.object(OpenWebUIClient, "_find_or_create_chat_by_title")
    def test_stream_chat_success(
        self, mock_find_create, mock_chat_manager_stream
    ):
        """Test successful streaming chat operation."""
        self.client.chat_id = "test-chat-id"

        # Mock the generator
        def mock_stream_generator():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"

        mock_chat_manager_stream.return_value = mock_stream_generator()

        # Collect all yielded chunks
        chunks = []
        stream_gen = self.client.stream_chat(
            question="Hello, world!", chat_title="Test Chat", tags=["stream", "test"]
        )

        for chunk in stream_gen:
            chunks.append(chunk)

        self.assertEqual(chunks, ["chunk1", "chunk2", "chunk3"])
        mock_chat_manager_stream.assert_called_once()

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
            json={
                "model": self.default_model,
                "messages": messages,
                "stream": False,
                "parent_message": {},
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
            "filename": "test.pdf",
            "user_id": "test-user-id",
            "meta": {"name": "test.pdf", "type": "application/pdf"},
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
                self.assertEqual(result["filename"], "test.pdf")

    def test_upload_file_not_found(self):
        """Test file upload when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            result = self.client._upload_file("/nonexistent/file.pdf")

            self.assertIsNone(result)

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.set_chat_tags")
    def test_set_chat_tags_success(self, mock_set_tags):
        """Test successful chat tag setting."""
        chat_id = "test-chat-id"
        tags = ["tag1", "tag2", "existing-tag"]
        mock_set_tags.return_value = True

        self.client.set_chat_tags(chat_id, tags)

        mock_set_tags.assert_called_once_with(chat_id, tags)

    def test_set_chat_tags_empty_list(self):
        """Test setting empty tag list (should do nothing)."""
        with patch(
            "openwebui_chat_client.openwebui_chat_client.requests.Session.get"
        ) as mock_get:
            self.client.set_chat_tags("chat_id", [])
            mock_get.assert_not_called()

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.switch_chat_model")
    def test_switch_chat_model_success(self, mock_switch):
        """Test successful chat model switching."""
        chat_id = "test-chat-id"
        new_model = "new-model:latest"
        mock_switch.return_value = True

        result = self.client.switch_chat_model(chat_id, new_model)

        self.assertTrue(result)
        mock_switch.assert_called_once_with(chat_id, new_model)

    @patch("openwebui_chat_client.modules.chat.manager.ChatManager.switch_chat_model")
    def test_switch_chat_model_same_model(self, mock_switch):
        """Test switching to the same model."""
        chat_id = "test-chat-id"
        current_model = "current-model:latest"
        mock_switch.return_value = True

        result = self.client.switch_chat_model(chat_id, current_model)

        self.assertTrue(result)
        mock_switch.assert_called_once_with(chat_id, current_model)

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
