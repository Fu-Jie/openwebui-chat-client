"""
Archive functionality tests for OpenWebUIClient.

This test file covers:
- archive_chat() method
- archive_chats_by_age() method with various parameters
- Error handling for archive operations
"""

import unittest
from unittest.mock import MagicMock, patch

from openwebui_chat_client import OpenWebUIClient


class TestArchiveChat(unittest.TestCase):
    """Test basic archive_chat functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = OpenWebUIClient(
            base_url="http://test.com",
            token="test-token",
            default_model_id="test-model",
            skip_model_refresh=True,
        )
        self.client._chat_manager = MagicMock()

    def test_archive_chat_success(self):
        """Test successful chat archiving."""
        self.client._chat_manager.archive_chat = MagicMock(return_value=True)

        result = self.client.archive_chat("chat-id")

        self.assertTrue(result)
        self.client._chat_manager.archive_chat.assert_called_once_with("chat-id")

    def test_archive_chat_failure(self):
        """Test failed chat archiving."""
        self.client._chat_manager.archive_chat = MagicMock(return_value=False)

        result = self.client.archive_chat("chat-id")

        self.assertFalse(result)


class TestArchiveChatsByAge(unittest.TestCase):
    """Test archive_chats_by_age functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = OpenWebUIClient(
            base_url="http://test.com",
            token="test-token",
            default_model_id="test-model",
            skip_model_refresh=True,
        )
        self.client._chat_manager = MagicMock()

    def test_archive_chats_by_age_basic(self):
        """Test archive_chats_by_age with default parameters."""
        mock_chats = [
            {"id": "chat1", "updated_at": 1000000, "folder_id": None},
            {"id": "chat2", "updated_at": 2000000, "folder_id": None},
            {"id": "chat3", "updated_at": 3000000, "folder_id": None},
        ]
        self.client._chat_manager.list_chats = MagicMock(return_value=mock_chats)
        self.client._get_chat_details = MagicMock(
            side_effect=lambda chat_id: next(
                (c for c in mock_chats if c["id"] == chat_id), None
            )
        )
        self.client._chat_manager.archive_chat = MagicMock(return_value=True)

        with patch("time.time", return_value=4000000):
            result = self.client.archive_chats_by_age(days_since_update=30)

        self.assertIsNotNone(result)
        self.assertIn("total_checked", result)
        self.assertIn("total_archived", result)
        self.assertIn("total_failed", result)

    def test_archive_chats_by_age_custom_days(self):
        """Test archive_chats_by_age with custom days."""
        mock_chats = [{"id": "chat1", "updated_at": 1000000, "folder_id": None}]
        self.client._chat_manager.list_chats = MagicMock(return_value=mock_chats)
        self.client._get_chat_details = MagicMock(return_value=mock_chats[0])
        self.client._chat_manager.archive_chat = MagicMock(return_value=True)

        with patch("time.time", return_value=10000000):
            result = self.client.archive_chats_by_age(days_since_update=60)

        self.assertIsNotNone(result)
        self.assertIn("total_checked", result)

    def test_archive_chats_by_age_dry_run(self):
        """Test archive_chats_by_age in dry run mode."""
        mock_chats = [
            {"id": "chat1", "updated_at": 1000000, "folder_id": None},
            {"id": "chat2", "updated_at": 2000000, "folder_id": None},
        ]
        self.client._chat_manager.list_chats = MagicMock(return_value=mock_chats)
        self.client._get_chat_details = MagicMock(
            side_effect=lambda chat_id: next(
                (c for c in mock_chats if c["id"] == chat_id), None
            )
        )

        with patch("time.time", return_value=4000000):
            result = self.client.archive_chats_by_age(
                days_since_update=30, dry_run=True
            )

        self.assertIsNotNone(result)
        # In dry run, archive_chat should not be called
        self.client._chat_manager.archive_chat.assert_not_called()

    def test_archive_chats_by_age_no_chats(self):
        """Test archive_chats_by_age when no chats exist."""
        self.client._chat_manager.list_chats = MagicMock(return_value=[])

        result = self.client.archive_chats_by_age(days_since_update=30)

        self.assertIsNotNone(result)
        self.assertEqual(result["total_archived"], 0)

    def test_archive_chats_by_age_list_fails(self):
        """Test archive_chats_by_age when list_chats fails."""
        self.client._chat_manager.list_chats = MagicMock(return_value=None)

        result = self.client.archive_chats_by_age(days_since_update=30)

        self.assertIsNotNone(result)
        self.assertIn("errors", result)
        self.assertTrue(len(result["errors"]) > 0)

    def test_archive_chats_by_age_with_folder(self):
        """Test archive_chats_by_age with folder filter."""
        mock_chats = [{"id": "chat1", "updated_at": 1000000}]
        self.client.get_folder_id_by_name = MagicMock(return_value="folder-id")
        self.client.get_chats_by_folder = MagicMock(return_value=mock_chats)
        self.client._chat_manager.archive_chat = MagicMock(return_value=True)

        with patch("time.time", return_value=4000000):
            result = self.client.archive_chats_by_age(
                days_since_update=30, folder_name="TestFolder"
            )

        self.assertIsNotNone(result)
        self.client.get_folder_id_by_name.assert_called_once_with("TestFolder")

    def test_archive_chats_by_age_folder_not_found(self):
        """Test archive_chats_by_age when folder doesn't exist."""
        self.client.get_folder_id_by_name = MagicMock(return_value=None)

        result = self.client.archive_chats_by_age(
            days_since_update=30, folder_name="NonExistent"
        )

        self.assertIsNotNone(result)
        self.assertIn("errors", result)
        self.assertTrue(len(result["errors"]) > 0)

    def test_archive_chats_by_age_partial_failure(self):
        """Test archive_chats_by_age with some archive failures."""
        mock_chats = [
            {"id": "chat1", "updated_at": 1000000, "folder_id": None},
            {"id": "chat2", "updated_at": 2000000, "folder_id": None},
        ]
        self.client._chat_manager.list_chats = MagicMock(return_value=mock_chats)
        self.client._get_chat_details = MagicMock(
            side_effect=lambda chat_id: next(
                (c for c in mock_chats if c["id"] == chat_id), None
            )
        )
        self.client._chat_manager.archive_chat = MagicMock(
            side_effect=[True, False]  # First succeeds, second fails
        )

        with patch("time.time", return_value=4000000):
            result = self.client.archive_chats_by_age(days_since_update=30)

        self.assertIsNotNone(result)
        # At least one should be archived
        self.assertGreaterEqual(result["total_archived"], 1)
        # Total checked should be 2
        self.assertEqual(result["total_checked"], 2)


if __name__ == "__main__":
    unittest.main()
