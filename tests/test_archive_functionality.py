import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from openwebui_chat_client import OpenWebUIClient


class TestArchiveFunctionality(unittest.TestCase):
    """Test archive functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = OpenWebUIClient(
            base_url="http://localhost:3000",
            token="test-token",
            default_model_id="test-model",
            skip_model_refresh=True
        )

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.get')
    def test_list_chats_success(self, mock_get):
        """Test successful chat list retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Test Chat 1", "updated_at": 1000000},
            {"id": "chat2", "title": "Test Chat 2", "updated_at": 2000000}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test
        result = self.client.list_chats()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "chat1")
        mock_get.assert_called_once_with(
            "http://localhost:3000/api/v1/chats/list",
            params={},
            headers=self.client.json_headers
        )

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.get')
    def test_list_chats_with_pagination(self, mock_get):
        """Test chat list retrieval with pagination."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test
        result = self.client.list_chats(page=2)

        # Assert
        mock_get.assert_called_once_with(
            "http://localhost:3000/api/v1/chats/list",
            params={"page": 2},
            headers=self.client.json_headers
        )

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.get')
    def test_list_chats_failure(self, mock_get):
        """Test chat list retrieval failure."""
        # Mock failure
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Test
        result = self.client.list_chats()

        # Assert
        self.assertIsNone(result)

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.get')
    def test_get_chats_by_folder_success(self, mock_get):
        """Test successful retrieval of chats by folder."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Test Chat 1", "folder_id": "folder1"},
            {"id": "chat2", "title": "Test Chat 2", "folder_id": "folder1"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test
        result = self.client.get_chats_by_folder("folder1")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        mock_get.assert_called_once_with(
            "http://localhost:3000/api/v1/chats/folder/folder1",
            headers=self.client.json_headers
        )

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.get')
    def test_get_chats_by_folder_failure(self, mock_get):
        """Test retrieval of chats by folder failure."""
        # Mock failure
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Test
        result = self.client.get_chats_by_folder("folder1")

        # Assert
        self.assertIsNone(result)

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.post')
    def test_archive_chat_success(self, mock_post):
        """Test successful chat archiving."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test
        result = self.client.archive_chat("chat1")

        # Assert
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            "http://localhost:3000/api/v1/chats/chat1/archive",
            headers=self.client.json_headers
        )

    @patch('openwebui_chat_client.openwebui_chat_client.requests.Session.post')
    def test_archive_chat_failure(self, mock_post):
        """Test chat archiving failure."""
        # Mock failure
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        # Test
        result = self.client.archive_chat("chat1")

        # Assert
        self.assertFalse(result)

    @patch.object(OpenWebUIClient, 'list_chats')
    @patch.object(OpenWebUIClient, '_get_chat_details')
    @patch.object(OpenWebUIClient, 'archive_chat')
    def test_archive_chats_by_age_no_folder(self, mock_archive, mock_details, mock_list):
        """Test archiving chats by age without folder filter."""
        # Setup mocks
        current_time = int(time.time())
        old_time = current_time - (40 * 24 * 60 * 60)  # 40 days old
        
        mock_list.return_value = [
            {"id": "chat1", "title": "Old Chat 1"},
            {"id": "chat2", "title": "Recent Chat"}
        ]
        
        mock_details.side_effect = [
            {"id": "chat1", "title": "Old Chat 1", "updated_at": old_time, "folder_id": None},
            {"id": "chat2", "title": "Recent Chat", "updated_at": current_time, "folder_id": None}
        ]
        
        mock_archive.return_value = True

        # Test
        result = self.client.archive_chats_by_age(days_since_update=30)

        # Assert
        self.assertEqual(result["total_checked"], 2)
        self.assertEqual(result["total_archived"], 1)
        self.assertEqual(result["total_failed"], 0)
        self.assertEqual(len(result["archived_chats"]), 1)
        self.assertEqual(result["archived_chats"][0]["id"], "chat1")
        
        # Verify archive was called only for old chat
        mock_archive.assert_called_once_with("chat1")

    @patch.object(OpenWebUIClient, 'get_folder_id_by_name')
    @patch.object(OpenWebUIClient, 'get_chats_by_folder')
    @patch.object(OpenWebUIClient, 'archive_chat')
    def test_archive_chats_by_age_with_folder(self, mock_archive, mock_folder_chats, mock_folder_id):
        """Test archiving chats by age with folder filter."""
        # Setup mocks
        current_time = int(time.time())
        old_time = current_time - (40 * 24 * 60 * 60)  # 40 days old
        
        mock_folder_id.return_value = "folder1"
        mock_folder_chats.return_value = [
            {"id": "chat1", "title": "Old Chat in Folder", "updated_at": old_time, "folder_id": "folder1"},
            {"id": "chat2", "title": "Recent Chat in Folder", "updated_at": current_time, "folder_id": "folder1"}
        ]
        mock_archive.return_value = True

        # Test
        result = self.client.archive_chats_by_age(days_since_update=30, folder_name="TestFolder")

        # Assert
        self.assertEqual(result["total_checked"], 2)
        self.assertEqual(result["total_archived"], 1)
        self.assertEqual(result["total_failed"], 0)
        mock_folder_id.assert_called_once_with("TestFolder")
        mock_folder_chats.assert_called_once_with("folder1")
        mock_archive.assert_called_once_with("chat1")

    @patch.object(OpenWebUIClient, 'get_folder_id_by_name')
    def test_archive_chats_by_age_folder_not_found(self, mock_folder_id):
        """Test archiving chats when folder is not found."""
        # Setup mocks
        mock_folder_id.return_value = None

        # Test
        result = self.client.archive_chats_by_age(folder_name="NonexistentFolder")

        # Assert
        self.assertEqual(result["total_checked"], 0)
        self.assertEqual(result["total_archived"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Folder 'NonexistentFolder' not found", result["errors"][0])

    @patch.object(OpenWebUIClient, 'list_chats')
    def test_archive_chats_by_age_list_failure(self, mock_list):
        """Test archiving chats when list_chats fails."""
        # Setup mocks
        mock_list.return_value = None

        # Test
        result = self.client.archive_chats_by_age()

        # Assert
        self.assertEqual(result["total_checked"], 0)
        self.assertEqual(result["total_archived"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Failed to get chat list", result["errors"][0])

    @patch.object(OpenWebUIClient, 'list_chats')
    @patch.object(OpenWebUIClient, '_get_chat_details')
    @patch.object(OpenWebUIClient, 'archive_chat')
    def test_archive_chats_by_age_archive_failure(self, mock_archive, mock_details, mock_list):
        """Test archiving chats when archive operation fails."""
        # Setup mocks
        current_time = int(time.time())
        old_time = current_time - (40 * 24 * 60 * 60)  # 40 days old
        
        mock_list.return_value = [{"id": "chat1", "title": "Old Chat"}]
        mock_details.return_value = {
            "id": "chat1", 
            "title": "Old Chat", 
            "updated_at": old_time, 
            "folder_id": None
        }
        mock_archive.return_value = False

        # Test
        result = self.client.archive_chats_by_age(days_since_update=30)

        # Assert
        self.assertEqual(result["total_checked"], 1)
        self.assertEqual(result["total_archived"], 0)
        self.assertEqual(result["total_failed"], 1)
        self.assertEqual(len(result["failed_chats"]), 1)
        self.assertEqual(result["failed_chats"][0]["id"], "chat1")


if __name__ == '__main__':
    unittest.main()