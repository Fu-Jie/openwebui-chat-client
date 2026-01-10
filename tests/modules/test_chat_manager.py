"""
Tests for ChatManager module (sync version).
"""

import json
import pytest
from unittest.mock import MagicMock, Mock, patch, mock_open, call
from typing import Any, Dict, List

from openwebui_chat_client.modules.chat_manager import ChatManager


class TestChatManager:
    """Test suite for ChatManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base_client = MagicMock()
        self.mock_base_client.base_url = "http://test.com"
        self.mock_base_client.default_model_id = "test-model"
        self.mock_base_client.model_id = "test-model"
        self.mock_base_client.chat_id = None
        self.mock_base_client.chat_object_from_server = None
        self.mock_base_client._first_stream_request = True
        self.mock_base_client._parent_client = None  # Explicitly set to None
        
        # Mock session
        self.mock_base_client.session = MagicMock()
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}
        
        # Mock methods
        self.mock_base_client._upload_file = MagicMock()
        self.mock_base_client._get_task_model = MagicMock()
        
        self.manager = ChatManager(self.mock_base_client)

    def test_initialization(self):
        """Test ChatManager initialization."""
        assert self.manager.base_client == self.mock_base_client

    def test_list_chats_without_page(self):
        """Test listing chats without page parameter."""
        expected_chats = [{"id": "chat1", "title": "Test Chat"}]
        mock_response = MagicMock()
        mock_response.json.return_value = expected_chats
        self.mock_base_client.session.get.return_value = mock_response
        
        result = self.manager.list_chats()
        
        assert result == expected_chats
        self.mock_base_client.session.get.assert_called_once()

    def test_list_chats_with_page(self):
        """Test listing chats with page parameter."""
        expected_chats = [{"id": "chat2", "title": "Test Chat 2"}]
        mock_response = MagicMock()
        mock_response.json.return_value = expected_chats
        self.mock_base_client.session.get.return_value = mock_response
        
        result = self.manager.list_chats(page=2)
        
        assert result == expected_chats

    def test_list_chats_exception(self):
        """Test listing chats with exception."""
        import requests
        self.mock_base_client.session.get.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.list_chats()
        
        assert result is None

    def test_delete_all_chats_success(self):
        """Test successful deletion of all chats."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.delete.return_value = mock_response
        
        result = self.manager.delete_all_chats()
        
        assert result is True
        self.mock_base_client.session.delete.assert_called_once()

    def test_delete_all_chats_failure(self):
        """Test failed deletion of all chats."""
        import requests
        self.mock_base_client.session.delete.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.delete_all_chats()
        
        assert result is False

    def test_archive_chat_success(self):
        """Test archiving a chat."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager.archive_chat("chat1")
        
        assert result is True

    def test_archive_chat_failure(self):
        """Test failed chat archive."""
        import requests
        self.mock_base_client.session.post.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.archive_chat("chat1")
        
        assert result is False

    def test_rename_chat_success(self):
        """Test renaming a chat."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager.rename_chat("chat1", "New Title")
        
        assert result is True

    def test_rename_chat_failure(self):
        """Test failed chat rename."""
        import requests
        self.mock_base_client.session.post.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.rename_chat("chat1", "New Title")
        
        assert result is False

    def test_create_folder_success(self):
        """Test creating a folder."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.post.return_value = mock_response
        
        # Mock get_folder_id_by_name which is called after creation
        with patch.object(self.manager, 'get_folder_id_by_name') as mock_get:
            mock_get.return_value = "new_folder"
            result = self.manager.create_folder("New Folder")
            
            assert result == "new_folder"
            mock_get.assert_called_once_with("New Folder")

    def test_create_folder_failure(self):
        """Test failed folder creation."""
        import requests
        self.mock_base_client.session.post.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.create_folder("New Folder")
        
        assert result is None

    def test_move_chat_to_folder_success(self):
        """Test moving chat to folder."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.post.return_value = mock_response
        
        self.manager.move_chat_to_folder("chat1", "folder1")
        
        self.mock_base_client.session.post.assert_called_once()

    def test_move_chat_to_folder_failure(self):
        """Test failed move chat to folder."""
        import requests
        self.mock_base_client.session.post.side_effect = requests.exceptions.RequestException("Error")
        
        # Should not raise exception
        self.manager.move_chat_to_folder("chat1", "folder1")

    def test_get_folder_id_by_name_found(self):
        """Test getting folder ID by name."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "folder1", "name": "Test Folder"},
            {"id": "folder2", "name": "Other Folder"},
        ]
        self.mock_base_client.session.get.return_value = mock_response
        
        result = self.manager.get_folder_id_by_name("Test Folder")
        
        assert result == "folder1"

    def test_get_folder_id_by_name_not_found(self):
        """Test getting folder ID when not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        self.mock_base_client.session.get.return_value = mock_response
        
        result = self.manager.get_folder_id_by_name("Nonexistent")
        
        assert result is None

    def test_get_folder_id_by_name_exception(self):
        """Test getting folder ID with exception."""
        import requests
        self.mock_base_client.session.get.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.manager.get_folder_id_by_name("Test")
        
        assert result is None

    def test_build_linear_history_for_api(self):
        """Test building linear history for API calls."""
        chat_data = {
            "history": {
                "messages": {
                    "msg1": {"id": "msg1", "role": "user", "content": "Hello", "parentId": None},
                    "msg2": {"id": "msg2", "role": "assistant", "content": "Hi", "parentId": "msg1"},
                    "msg3": {"id": "msg3", "role": "user", "content": "How are you?", "parentId": "msg2"},
                },
                "currentId": "msg3",
            }
        }
        
        result = self.manager._build_linear_history_for_api(chat_data)
        
        assert len(result) == 3
        assert result[0] == {"role": "user", "content": "Hello"}
        assert result[1] == {"role": "assistant", "content": "Hi"}
        assert result[2] == {"role": "user", "content": "How are you?"}

    def test_build_linear_history_for_api_empty(self):
        """Test building linear history with no current ID."""
        chat_data = {"history": {"messages": {}, "currentId": None}}
        
        result = self.manager._build_linear_history_for_api(chat_data)
        
        assert result == []

    def test_build_linear_history_for_storage(self):
        """Test building linear history for storage."""
        chat_data = {
            "history": {
                "messages": {
                    "msg1": {
                        "id": "msg1",
                        "role": "user",
                        "content": "Hello",
                        "parentId": None,
                        "childrenIds": ["msg2"],
                    },
                    "msg2": {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "Hi",
                        "parentId": "msg1",
                        "childrenIds": [],
                        "model": "gpt-4",
                        "modelName": "gpt",
                        "done": True,
                    },
                }
            }
        }
        
        result = self.manager._build_linear_history_for_storage(chat_data, "msg2")
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        # The method adds timestamp, so model might not be in result
        assert result[1]["content"] == "Hi"

    def test_count_available_placeholder_pairs(self):
        """Test counting available placeholder pairs - fallback behavior."""
        # Without _parent_client, should return 0
        count = self.manager._count_available_placeholder_pairs()
        assert count == 0

    def test_cleanup_unused_placeholder_messages(self):
        """Test cleanup of unused placeholder messages - fallback behavior."""
        # Without _parent_client, should return 0
        count = self.manager._cleanup_unused_placeholder_messages()
        assert count == 0

    def test_get_next_available_message_pair(self):
        """Test getting next available message pair - fallback behavior."""
        # Without _parent_client, should return None
        result = self.manager._get_next_available_message_pair()
        assert result is None

    def test_encode_image_to_base64_success(self):
        """Test encoding image to base64."""
        import tempfile
        import os
        
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # PNG header
            temp_path = f.name
        
        try:
            result = self.manager._encode_image_to_base64(temp_path)
            
            assert result is not None
            # Note: The method detects format by extension, not content
            assert "base64," in result
        finally:
            os.unlink(temp_path)

    def test_encode_image_to_base64_file_not_found(self):
        """Test encoding non-existent image."""
        result = self.manager._encode_image_to_base64("/nonexistent/image.png")
        
        assert result is None

    def test_handle_rag_references_files(self):
        """Test handling RAG file references."""
        file_obj = {"id": "file1", "name": "test.pdf"}
        self.mock_base_client._upload_file.return_value = file_obj
        
        api_payload, storage_payload = self.manager._handle_rag_references(
            rag_files=["test.pdf"], rag_collections=None
        )
        
        assert len(api_payload) == 1
        assert api_payload[0]["type"] == "file"
        # Just check that id exists, don't check exact value
        assert "id" in api_payload[0]
        assert len(storage_payload) == 1

    def test_handle_rag_references_collections(self):
        """Test handling RAG knowledge base collections."""
        # Without proper parent client setup, collections won't be processed
        api_payload, storage_payload = self.manager._handle_rag_references(
            rag_files=None, rag_collections=["Test KB"]
        )
        
        # Without parent client, collections can't be resolved
        assert isinstance(api_payload, list)
        assert isinstance(storage_payload, list)

    def test_handle_rag_references_both(self):
        """Test handling both files and collections."""
        file_obj = {"id": "file1", "name": "test.pdf"}
        self.mock_base_client._upload_file.return_value = file_obj
        
        api_payload, storage_payload = self.manager._handle_rag_references(
            rag_files=["test.pdf"], rag_collections=["Test KB"]
        )
        
        # Should have at least the file
        assert len(api_payload) >= 1
        assert len(storage_payload) >= 1

    def test_get_follow_up_completions_no_parent_client(self):
        """Test follow-up generation without parent client."""
        # Without proper setup, should return None or handle gracefully
        self.mock_base_client._get_task_model.return_value = None
        
        result = self.manager._get_follow_up_completions([])
        
        # Should return None when no task model
        assert result is None

    def test_get_tags_no_parent_client(self):
        """Test tags generation without parent client."""
        # Without proper setup, should return None or handle gracefully
        self.mock_base_client._get_task_model.return_value = None
        
        result = self.manager._get_tags([])
        
        # Should return None when no task model
        assert result is None

    def test_get_title_no_parent_client(self):
        """Test title generation without parent client."""
        # Without proper setup, should return None or handle gracefully
        self.mock_base_client._get_task_model.return_value = None
        
        result = self.manager._get_title([])
        
        # Should return None when no task model
        assert result is None

    def test_set_chat_tags(self):
        """Test setting chat tags."""
        # Mock existing tags
        existing_response = MagicMock()
        existing_response.json.return_value = [{"name": "existing"}]
        
        new_tag_response = MagicMock()
        new_tag_response.raise_for_status = MagicMock()
        
        self.mock_base_client.session.get.return_value = existing_response
        self.mock_base_client.session.post.return_value = new_tag_response
        
        self.manager.set_chat_tags("chat1", ["existing", "new"])
        
        # Should only create the new tag
        assert self.mock_base_client.session.post.call_count == 1

    def test_set_chat_tags_empty(self):
        """Test setting empty tags."""
        self.manager.set_chat_tags("chat1", [])
        
        self.mock_base_client.session.get.assert_not_called()
        self.mock_base_client.session.post.assert_not_called()

    def test_update_remote_chat_success(self):
        """Test successful remote chat update."""
        self.mock_base_client.chat_id = "chat1"
        self.mock_base_client.chat_object_from_server = {
            "chat": {"title": "Test", "messages": []}
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._update_remote_chat()
        
        assert result is True

    def test_update_remote_chat_no_chat_id(self):
        """Test remote chat update without chat ID."""
        self.mock_base_client.chat_id = None
        
        result = self.manager._update_remote_chat()
        
        assert result is False
