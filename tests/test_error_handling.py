import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from requests.exceptions import RequestException, HTTPError, ConnectionError

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientErrorHandling(unittest.TestCase):
    """Unit tests for OpenWebUIClient error handling and edge cases."""

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

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_models_network_error(self, mock_get):
        """Test model listing with network error."""
        mock_get.side_effect = ConnectionError("Connection failed")

        result = self.client.list_models()

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_models_json_decode_error(self, mock_get):
        """Test model listing with JSON decode error."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        result = self.client.list_models()

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_models_malformed_response(self, mock_get):
        """Test model listing with malformed response structure."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"wrong_key": "wrong_value"}
        mock_get.return_value = mock_response

        result = self.client.list_models()

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_model_http_error(self, mock_post):
        """Test model creation with HTTP error."""
        mock_response = Mock()
        mock_response.text = "Bad Request"
        mock_post.side_effect = HTTPError(response=mock_response)

        result = self.client.create_model(
            model_id="test-model", name="Test Model", base_model_id="base-model"
        )

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_model_http_error(self, mock_delete):
        """Test model deletion with HTTP error."""
        mock_delete.side_effect = HTTPError("Not found")

        result = self.client.delete_model("nonexistent-model")

        self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_model_json_decode_error(self, mock_delete):
        """Test model deletion with JSON decode error in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        result = self.client.delete_model("test-model")

        # Should still return True since request was successful (200)
        self.assertTrue(result)

    @patch.object(OpenWebUIClient, "get_model")
    def test_update_model_not_found(self, mock_get_model):
        """Test updating a model that doesn't exist."""
        mock_get_model.return_value = None

        result = self.client.update_model("nonexistent-model", name="New Name")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_knowledge_base_by_name_http_error(self, mock_get):
        """Test knowledge base retrieval with HTTP error."""
        mock_get.side_effect = HTTPError("Server error")

        result = self.client.get_knowledge_base_by_name("test-kb")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_knowledge_base_http_error(self, mock_post):
        """Test knowledge base creation with HTTP error."""
        mock_post.side_effect = HTTPError("Server error")

        result = self.client.create_knowledge_base("test-kb", "Test description")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_knowledge_base_http_error(self, mock_delete):
        """Test knowledge base deletion with HTTP error."""
        mock_delete.side_effect = HTTPError("Server error")

        result = self.client.delete_knowledge_base("test-kb-id")

        self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_knowledge_base_unexpected_response(self, mock_delete):
        """Test knowledge base deletion with unexpected response."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "response"}
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        result = self.client.delete_knowledge_base("test-kb-id")

        self.assertFalse(result)

    def test_encode_image_to_base64_invalid_extension(self):
        """Test image encoding with invalid file extension."""
        test_image_path = "/tmp/test_file.xyz"  # Unsupported extension
        test_content = b"fake content"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = (
                    test_content
                )

                result = self.client._encode_image_to_base64(test_image_path)

                # Should still work but use default MIME type
                self.assertIsNotNone(result)
                self.assertTrue(
                    result.startswith("data:application/octet-stream;base64,")
                )

    def test_encode_image_to_base64_read_error(self):
        """Test image encoding with file read error."""
        test_image_path = "/tmp/test_image.png"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                result = self.client._encode_image_to_base64(test_image_path)

                self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_upload_file_http_error(self, mock_post):
        """Test file upload with HTTP error."""
        file_path = "/tmp/test.pdf"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True):
                mock_post.side_effect = HTTPError("Upload failed")

                result = self.client._upload_file(file_path)

                self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_upload_file_malformed_response(self, mock_post):
        """Test file upload with malformed response."""
        file_path = "/tmp/test.pdf"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True):
                mock_response = Mock()
                mock_response.json.return_value = {"no_id_field": "invalid"}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                result = self.client._upload_file(file_path)

                self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_search_latest_chat_by_title_http_error(self, mock_get):
        """Test chat search with HTTP error."""
        mock_get.side_effect = HTTPError("Server error")

        result = self.client._search_latest_chat_by_title("Test Chat")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_new_chat_http_error(self, mock_post):
        """Test chat creation with HTTP error."""
        mock_post.side_effect = HTTPError("Server error")

        result = self.client._create_new_chat("Test Chat")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_new_chat_malformed_response(self, mock_post):
        """Test chat creation with malformed response."""
        mock_response = Mock()
        mock_response.json.return_value = {"no_id_field": "invalid"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client._create_new_chat("Test Chat")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_rename_chat_http_error(self, mock_post):
        """Test chat renaming with HTTP error."""
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.text = "Server error"
        error = HTTPError("Server error")
        error.response = mock_response
        mock_post.side_effect = error

        result = self.client.rename_chat("chat-id", "New Title")

        self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_folder_id_by_name_http_error(self, mock_get):
        """Test folder ID retrieval with HTTP error."""
        mock_get.side_effect = HTTPError("Server error")

        result = self.client.get_folder_id_by_name("Test Folder")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_folder_http_error(self, mock_post):
        """Test folder creation with HTTP error."""
        mock_post.side_effect = HTTPError("Server error")

        result = self.client.create_folder("Test Folder")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_move_chat_to_folder_http_error(self, mock_post):
        """Test moving chat to folder with HTTP error."""
        self.client.chat_object_from_server = {"folder_id": "old-folder"}
        mock_post.side_effect = HTTPError("Server error")

        # Should not raise exception, just log error
        self.client.move_chat_to_folder("chat-id", "new-folder-id")

        # Folder ID should not be updated
        self.assertEqual(self.client.chat_object_from_server["folder_id"], "old-folder")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_set_chat_tags_get_existing_tags_error(self, mock_post, mock_get):
        """Test setting chat tags when getting existing tags fails."""
        chat_id = "test-chat-id"
        tags = ["tag1", "tag2"]

        # Mock getting existing tags fails
        mock_get.side_effect = HTTPError("Server error")

        # Mock posting new tags succeeds
        mock_post_response = Mock()
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        # Should not raise exception and should attempt to add all tags
        self.client.set_chat_tags(chat_id, tags)

        # Should still try to post both tags since it couldn't fetch existing ones
        self.assertEqual(mock_post.call_count, 2)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_set_chat_tags_post_tag_error(self, mock_post, mock_get):
        """Test setting chat tags when posting a tag fails."""
        chat_id = "test-chat-id"
        tags = ["tag1", "tag2"]

        # Mock getting existing tags succeeds
        mock_get_response = Mock()
        mock_get_response.json.return_value = []
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response

        # Mock posting - first succeeds, second fails
        mock_post_success = Mock()
        mock_post_success.raise_for_status.return_value = None
        mock_post_error = Mock()
        mock_post_error.raise_for_status.side_effect = HTTPError("Server error")
        mock_post.side_effect = [mock_post_success, mock_post_error]

        # Should not raise exception, just log error for failed tag
        self.client.set_chat_tags(chat_id, tags)

        self.assertEqual(mock_post.call_count, 2)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_update_remote_chat_http_error(self, mock_post):
        """Test updating remote chat with HTTP error."""
        self.client.chat_id = "test-chat-id"
        self.client.chat_object_from_server = {"chat": {"title": "Test"}}

        mock_post.side_effect = HTTPError("Server error")

        result = self.client._update_remote_chat()

        self.assertFalse(result)

    def test_build_linear_history_for_api_empty_history(self):
        """Test building linear history with empty history."""
        chat_core = {"history": {"currentId": None, "messages": {}}}

        result = self.client._build_linear_history_for_api(chat_core)

        self.assertEqual(len(result), 0)

    def test_build_linear_history_for_api_missing_message(self):
        """Test building linear history with missing message reference."""
        chat_core = {"history": {"currentId": "missing-msg", "messages": {}}}

        result = self.client._build_linear_history_for_api(chat_core)

        self.assertEqual(len(result), 0)

    def test_build_linear_history_for_storage_empty_history(self):
        """Test building linear history for storage with empty history."""
        chat_core = {"history": {"messages": {}}}

        result = self.client._build_linear_history_for_storage(
            chat_core, "nonexistent-id"
        )

        self.assertEqual(len(result), 0)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_load_chat_details_http_error(self, mock_get):
        """Test loading chat details with HTTP error."""
        mock_get.side_effect = HTTPError("Server error")

        result = self.client._load_chat_details("chat-id")

        self.assertFalse(result)  # Method now returns bool, False on error
        self.assertIsNone(self.client.chat_id)
        self.assertIsNone(self.client.chat_object_from_server)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_load_chat_details_empty_response(self, mock_get):
        """Test loading chat details with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._load_chat_details("chat-id")

        self.assertFalse(result)  # Method now returns bool, False on empty response

    def test_chat_model_switching_edge_cases(self):
        """Test various edge cases in model switching."""
        # Test with single string
        self.client.chat_object_from_server = {"chat": {"models": ["old-model"]}}

        with patch.object(self.client, "_load_chat_details", return_value=True):
            with patch.object(self.client, "_update_remote_chat", return_value=True):
                result = self.client.switch_chat_model("chat-id", "new-model")
                self.assertTrue(result)
                self.assertEqual(
                    self.client.chat_object_from_server["chat"]["models"], ["new-model"]
                )

    def test_handle_rag_references_file_upload_failure(self):
        """Test RAG reference handling when file upload fails."""
        with patch.object(self.client, "_upload_file", return_value=None):
            api_payload, storage_payload = self.client._handle_rag_references(
                rag_files=["failing-file.pdf"], rag_collections=None
            )

            # Should have empty payloads since upload failed
            self.assertEqual(len(api_payload), 0)
            self.assertEqual(len(storage_payload), 0)


if __name__ == "__main__":
    unittest.main()
