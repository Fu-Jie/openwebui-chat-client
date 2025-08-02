import unittest
from unittest.mock import patch, MagicMock, call
from openwebui_chat_client import OpenWebUIClient
import uuid

class TestMetadataFeatures(unittest.TestCase):

    def setUp(self):
        # Mock HTTP requests during client initialization
        self.client = OpenWebUIClient(base_url="http://localhost:8080", token="test_token", default_model_id="llama3", skip_model_refresh=True)
        
        # Mock successful chat creation and loading
        self.mock_chat_id = str(uuid.uuid4())
        self.mock_chat_object = {
            "id": self.mock_chat_id,
            "title": "Test Chat",
            "chat": {
                "id": self.mock_chat_id,
                "title": "Test Chat",
                "models": ["llama3"],
                "history": {
                    "messages": {},
                    "currentId": None,
                },
                "messages": [],
            }
        }

    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_task_model')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_title')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_tags')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._ask')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._find_or_create_chat_by_title')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient.set_chat_tags')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient.rename_chat')
    def test_chat_with_auto_metadata(self, mock_rename_chat, mock_set_chat_tags, mock_find_create, mock_ask, mock_get_tags, mock_get_title, mock_get_task_model):
        # Setup mocks
        self.client.chat_id = self.mock_chat_id
        self.client.chat_object_from_server = self.mock_chat_object
        mock_find_create.return_value = None
        mock_ask.return_value = ("Hello there!", "msg_id_123", ["Follow up?"])
        mock_get_tags.return_value = ["test", "ai"]
        mock_get_title.return_value = "AI Test Conversation"
        mock_get_task_model.return_value = "task-model"

        # Call chat with auto features enabled
        result = self.client.chat(
            question="Hi",
            chat_title="Test Chat",
            enable_auto_tagging=True,
            enable_auto_titling=True
        )

        # Assertions
        mock_get_tags.assert_called_once()
        mock_get_title.assert_called_once()
        mock_set_chat_tags.assert_called_with(self.mock_chat_id, ["test", "ai"])
        mock_rename_chat.assert_called_with(self.mock_chat_id, "AI Test Conversation")

        self.assertIsNotNone(result)
        self.assertEqual(result.get("suggested_tags"), ["test", "ai"])
        self.assertEqual(result.get("suggested_title"), "AI Test Conversation")

    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_task_model')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._load_chat_details')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_title')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._get_tags')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient.set_chat_tags')
    @patch('openwebui_chat_client.openwebui_chat_client.OpenWebUIClient.rename_chat')
    def test_update_chat_metadata(self, mock_rename_chat, mock_set_chat_tags, mock_get_tags, mock_get_title, mock_load_details, mock_get_task_model):
        # Setup mocks
        mock_load_details.return_value = True
        self.client.chat_object_from_server = self.mock_chat_object
        mock_get_tags.return_value = ["updated", "metadata"]
        mock_get_title.return_value = "Updated Title"
        mock_get_task_model.return_value = "task-model"

        # Call the function
        result = self.client.update_chat_metadata(
            chat_id=self.mock_chat_id,
            regenerate_tags=True,
            regenerate_title=True
        )

        # Assertions
        mock_load_details.assert_called_with(self.mock_chat_id)
        mock_get_tags.assert_called_once()
        mock_get_title.assert_called_once()
        mock_set_chat_tags.assert_called_with(self.mock_chat_id, ["updated", "metadata"])
        mock_rename_chat.assert_called_with(self.mock_chat_id, "Updated Title")

        self.assertIsNotNone(result)
        self.assertEqual(result.get("suggested_tags"), ["updated", "metadata"])
        self.assertEqual(result.get("suggested_title"), "Updated Title")

if __name__ == '__main__':
    unittest.main()
