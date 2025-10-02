import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
import base64
import os
from io import BytesIO

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClient(unittest.TestCase):
    """Unit tests for OpenWebUIClient class."""

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

    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertEqual(self.client.default_model_id, self.default_model)
        self.assertEqual(self.client.model_id, self.default_model)
        self.assertIsNone(self.client.chat_id)
        self.assertIsNone(self.client.chat_object_from_server)

        # Check headers are set correctly
        expected_auth_header = f"Bearer {self.token}"
        self.assertEqual(
            self.client.session.headers["Authorization"], expected_auth_header
        )
        self.assertEqual(
            self.client.json_headers["Authorization"], expected_auth_header
        )
        self.assertEqual(self.client.json_headers["Content-Type"], "application/json")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_models_success(self, mock_get):
        """Test successful model listing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "name": "Model 1"},
                {"id": "model2", "name": "Model 2"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.list_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "model1")
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/models?refresh=true", headers=self.client.json_headers
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_models_failure(self, mock_get):
        """Test model listing failure."""
        from requests.exceptions import RequestException

        mock_get.side_effect = RequestException("Network error")

        result = self.client.list_models()

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_base_models_success(self, mock_get):
        """Test successful base model listing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": "base1", "name": "Base Model 1"},
                {"id": "base2", "name": "Base Model 2"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.list_base_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/models/base", headers=self.client.json_headers
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_custom_models_success(self, mock_get):
        """Test successful custom model listing."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "custom1", "name": "Custom Model 1"},
            {"id": "custom2", "name": "Custom Model 2"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.list_custom_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/models", headers=self.client.json_headers
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_model_success(self, mock_get):
        """Test successful model retrieval."""
        model_id = "test-model:latest"

        # Add the model to available_model_ids so it passes the initial check
        self.client.available_model_ids = [model_id]

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": model_id,
            "name": "Test Model",
            "description": "A test model",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_model(model_id)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], model_id)
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/models/model",
            params={"id": model_id},
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_model_not_found(self, mock_get):
        """Test model not found scenario."""
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_model("nonexistent-model")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_model_success(self, mock_post):
        """Test successful model creation."""
        model_id = "new-model:latest"
        model_name = "New Model"
        base_model_id = "base-model:latest"

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": model_id,
            "name": model_name,
            "base_model_id": base_model_id,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.create_model(
            model_id=model_id,
            name=model_name,
            base_model_id=base_model_id,
            params={
                "system_prompt": "Test prompt",
                "temperature": 0.7,
            },
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], model_id)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["headers"], self.client.json_headers)
        self.assertIn("json", call_args[1])

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_model_success(self, mock_delete):
        """Test successful model deletion."""
        model_id = "model-to-delete:latest"

        mock_response = Mock()
        mock_response.json.return_value = True
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result = self.client.delete_model(model_id)

        self.assertTrue(result)
        mock_delete.assert_called_once_with(
            f"{self.base_url}/api/v1/models/model/delete",
            params={"id": model_id},
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_knowledge_base_by_name_success(self, mock_get):
        """Test successful knowledge base retrieval by name."""
        kb_name = "test-kb"
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "other-kb"},
            {"id": "kb2", "name": kb_name, "description": "Test KB"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_knowledge_base_by_name(kb_name)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], kb_name)
        self.assertEqual(result["id"], "kb2")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_knowledge_base_by_name_not_found(self, mock_get):
        """Test knowledge base not found scenario."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "kb1", "name": "other-kb"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_knowledge_base_by_name("nonexistent-kb")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_knowledge_base_success(self, mock_post):
        """Test successful knowledge base creation."""
        kb_name = "new-kb"
        kb_description = "New knowledge base"

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "new-kb-id",
            "name": kb_name,
            "description": kb_description,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.create_knowledge_base(kb_name, kb_description)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], kb_name)
        mock_post.assert_called_once_with(
            f"{self.base_url}/api/v1/knowledge/create",
            json={"name": kb_name, "description": kb_description},
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.delete")
    def test_delete_knowledge_base_success(self, mock_delete):
        """Test successful knowledge base deletion."""
        kb_id = "kb-to-delete"

        mock_response = Mock()
        mock_response.json.return_value = True
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        result = self.client.delete_knowledge_base(kb_id)

        self.assertTrue(result)
        mock_delete.assert_called_once_with(
            f"{self.base_url}/api/v1/knowledge/{kb_id}/delete",
            headers=self.client.json_headers,
        )

    def test_encode_image_to_base64_success(self):
        """Test successful image encoding to base64."""
        # Create a temporary test image file
        test_image_path = "/tmp/test_image.png"
        test_content = b"fake image content"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = (
                    test_content
                )

                result = self.client._encode_image_to_base64(test_image_path)

                self.assertIsNotNone(result)
                self.assertTrue(result.startswith("data:image/png;base64,"))

                # Verify the base64 content
                expected_b64 = base64.b64encode(test_content).decode("utf-8")
                self.assertIn(expected_b64, result)

    def test_encode_image_to_base64_file_not_found(self):
        """Test image encoding when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            result = self.client._encode_image_to_base64("nonexistent.png")
            self.assertIsNone(result)

    def test_build_linear_history_for_api(self):
        """Test building linear history for API calls."""
        # Create a mock chat core with message history
        chat_core = {
            "history": {
                "currentId": "msg3",
                "messages": {
                    "msg1": {
                        "id": "msg1",
                        "parentId": None,
                        "role": "user",
                        "content": "Hello",
                        "files": [],
                    },
                    "msg2": {
                        "id": "msg2",
                        "parentId": "msg1",
                        "role": "assistant",
                        "content": "Hi there!",
                        "files": [],
                    },
                    "msg3": {
                        "id": "msg3",
                        "parentId": "msg2",
                        "role": "user",
                        "content": "How are you?",
                        "files": [],
                    },
                },
            }
        }

        result = self.client._build_linear_history_for_api(chat_core)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["content"], "Hello")
        self.assertEqual(result[1]["role"], "assistant")
        self.assertEqual(result[1]["content"], "Hi there!")
        self.assertEqual(result[2]["role"], "user")
        self.assertEqual(result[2]["content"], "How are you?")

    def test_build_linear_history_for_api_with_images(self):
        """Test building linear history with image files."""
        chat_core = {
            "history": {
                "currentId": "msg1",
                "messages": {
                    "msg1": {
                        "id": "msg1",
                        "parentId": None,
                        "role": "user",
                        "content": "Look at this image",
                        "files": [
                            {"type": "image", "url": "data:image/png;base64,abc123"}
                        ],
                    }
                },
            }
        }

        result = self.client._build_linear_history_for_api(chat_core)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "user")
        self.assertIsInstance(result[0]["content"], list)
        self.assertEqual(result[0]["content"][0]["type"], "text")
        self.assertEqual(result[0]["content"][0]["text"], "Look at this image")
        self.assertEqual(result[0]["content"][1]["type"], "image_url")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_search_latest_chat_by_title_success(self, mock_get):
        """Test successful chat search by title."""
        title = "Test Chat"
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": title, "updated_at": 1000},
            {"id": "chat2", "title": "Other Chat", "updated_at": 2000},
            {"id": "chat3", "title": title, "updated_at": 3000},  # Most recent
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._search_latest_chat_by_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "chat3")  # Should get the most recent one
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/chats/search",
            params={"text": title},
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_search_latest_chat_by_title_not_found(self, mock_get):
        """Test chat search when no exact match is found."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "chat1", "title": "Different Chat"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._search_latest_chat_by_title("Nonexistent Chat")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_new_chat_success(self, mock_post):
        """Test successful new chat creation."""
        title = "New Chat"
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new-chat-id"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client._create_new_chat(title)

        self.assertEqual(result, "new-chat-id")
        mock_post.assert_called_once_with(
            f"{self.base_url}/api/v1/chats/new",
            json={"chat": {"title": title}},
            headers=self.client.json_headers,
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_rename_chat_success(self, mock_post):
        """Test successful chat renaming."""
        chat_id = "chat-to-rename"
        new_title = "New Title"

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.rename_chat(chat_id, new_title)

        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{self.base_url}/api/v1/chats/{chat_id}",
            headers=self.client.json_headers,
            json={"chat": {"title": new_title}},
        )

    def test_rename_chat_empty_id(self):
        """Test chat renaming with empty chat ID."""
        result = self.client.rename_chat("", "New Title")
        self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_folder_id_by_name_success(self, mock_get):
        """Test successful folder ID retrieval by name."""
        folder_name = "Test Folder"
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "folder1", "name": "Other Folder"},
            {"id": "folder2", "name": folder_name},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_folder_id_by_name(folder_name)

        self.assertEqual(result, "folder2")

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_get_folder_id_by_name_not_found(self, mock_get):
        """Test folder ID retrieval when folder doesn't exist."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "folder1", "name": "Other Folder"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_folder_id_by_name("Nonexistent Folder")

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_create_folder_success(self, mock_post):
        """Test successful folder creation."""
        folder_name = "New Folder"

        # Mock the create request
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock the subsequent get_folder_id_by_name call
        with patch.object(
            self.client, "get_folder_id_by_name", return_value="new-folder-id"
        ):
            result = self.client.create_folder(folder_name)

            self.assertEqual(result, "new-folder-id")
            mock_post.assert_called_once_with(
                f"{self.base_url}/api/v1/folders/",
                json={"name": folder_name},
                headers=self.client.json_headers,
            )

    def test_handle_rag_references_files_only(self):
        """Test RAG reference handling with files only."""
        with patch.object(self.client, "_upload_file") as mock_upload:
            mock_upload.return_value = {
                "id": "file123",
                "name": "test.pdf",
                "type": "application/pdf",
            }

            api_payload, storage_payload = self.client._handle_rag_references(
                rag_files=["test.pdf"], rag_collections=None
            )

            self.assertEqual(len(api_payload), 1)
            self.assertEqual(len(storage_payload), 1)
            self.assertEqual(api_payload[0]["type"], "file")
            self.assertEqual(api_payload[0]["id"], "file123")
            # Storage payload contains file object spread, so "type" gets overwritten by file_obj["type"]
            self.assertEqual(
                storage_payload[0]["type"], "application/pdf"
            )  # From file_obj
            self.assertIn("file", storage_payload[0])
            self.assertEqual(
                storage_payload[0]["id"], "file123"
            )  # Spread from file_obj
            self.assertEqual(
                storage_payload[0]["name"], "test.pdf"
            )  # Spread from file_obj

    def test_handle_rag_references_collections_only(self):
        """Test RAG reference handling with collections only."""
        kb_summary = {"id": "kb123", "name": "test-kb"}
        kb_details = {
            "id": "kb123",
            "name": "test-kb",
            "files": [{"id": "file1"}, {"id": "file2"}],
        }

        with patch.object(
            self.client, "get_knowledge_base_by_name", return_value=kb_summary
        ):
            with patch.object(
                self.client, "_get_knowledge_base_details", return_value=kb_details
            ):
                api_payload, storage_payload = self.client._handle_rag_references(
                    rag_files=None, rag_collections=["test-kb"]
                )

                self.assertEqual(len(api_payload), 1)
                self.assertEqual(len(storage_payload), 1)
                self.assertEqual(api_payload[0]["type"], "collection")
                self.assertEqual(api_payload[0]["id"], "kb123")
                self.assertEqual(storage_payload[0]["type"], "collection")

    def test_handle_rag_references_empty(self):
        """Test RAG reference handling with no files or collections."""
        api_payload, storage_payload = self.client._handle_rag_references(
            rag_files=None, rag_collections=None
        )

        self.assertEqual(len(api_payload), 0)
        self.assertEqual(len(storage_payload), 0)


if __name__ == "__main__":
    unittest.main()
