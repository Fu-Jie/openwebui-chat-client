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
        mock_response.json.return_value = {"id": "new_folder"}
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager.create_folder("New Folder")
        
        assert result == "new_folder"

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
        assert result[1]["model"] == "gpt-4"

    def test_count_available_placeholder_pairs(self):
        """Test counting available placeholder pairs."""
        count = self.manager._count_available_placeholder_pairs()
        
        # Should return 0 when no chat object is set
        assert count == 0

    def test_cleanup_unused_placeholder_messages(self):
        """Test cleanup of unused placeholder messages."""
        # Set up chat object with placeholders
        self.mock_base_client.chat_object_from_server = {
            "chat": {
                "history": {
                    "messages": {
                        "user1": {
                            "id": "user1",
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": True,
                            "childrenIds": ["asst1"],
                        },
                        "asst1": {
                            "id": "asst1",
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": True,
                        },
                    }
                }
            }
        }
        
        count = self.manager._cleanup_unused_placeholder_messages()
        
        assert count == 1

    def test_get_next_available_message_pair(self):
        """Test getting next available message pair."""
        # Set up chat object with available pair
        self.mock_base_client.chat_object_from_server = {
            "chat": {
                "history": {
                    "messages": {
                        "user1": {
                            "id": "user1",
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": True,
                            "childrenIds": ["asst1"],
                        },
                        "asst1": {
                            "id": "asst1",
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": True,
                        },
                    }
                }
            }
        }
        
        result = self.manager._get_next_available_message_pair()
        
        assert result == ("user1", "asst1")

    def test_get_next_available_message_pair_none_available(self):
        """Test getting message pair when none available."""
        self.mock_base_client.chat_object_from_server = {
            "chat": {"history": {"messages": {}}}
        }
        
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
        assert api_payload[0] == {"type": "file", "id": "file1"}
        assert len(storage_payload) == 1

    def test_handle_rag_references_collections(self):
        """Test handling RAG knowledge base collections."""
        kb_list = [{"id": "kb1", "name": "Test KB"}]
        kb_details = {
            "id": "kb1",
            "name": "Test KB",
            "files": [{"id": "f1"}, {"id": "f2"}],
        }
        
        mock_response1 = MagicMock()
        mock_response1.json.return_value = kb_list
        mock_response2 = MagicMock()
        mock_response2.json.return_value = kb_details
        
        self.mock_base_client.session.get.side_effect = [mock_response1, mock_response2]
        
        api_payload, storage_payload = self.manager._handle_rag_references(
            rag_files=None, rag_collections=["Test KB"]
        )
        
        assert len(api_payload) == 1
        assert api_payload[0]["type"] == "collection"

    def test_handle_rag_references_both(self):
        """Test handling both files and collections."""
        file_obj = {"id": "file1", "name": "test.pdf"}
        self.mock_base_client._upload_file.return_value = file_obj
        
        kb_list = [{"id": "kb1", "name": "Test KB"}]
        kb_details = {"id": "kb1", "name": "Test KB", "files": [{"id": "f1"}]}
        
        mock_response1 = MagicMock()
        mock_response1.json.return_value = kb_list
        mock_response2 = MagicMock()
        mock_response2.json.return_value = kb_details
        
        self.mock_base_client.session.get.side_effect = [mock_response1, mock_response2]
        
        api_payload, storage_payload = self.manager._handle_rag_references(
            rag_files=["test.pdf"], rag_collections=["Test KB"]
        )
        
        assert len(api_payload) == 2
        assert len(storage_payload) == 2

    def test_get_follow_up_completions_success(self):
        """Test generating follow-up suggestions."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"follow_ups": ["Question 1?", "Question 2?"]}'
                    }
                }
            ]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.manager._get_follow_up_completions(messages)
        
        assert result == ["Question 1?", "Question 2?"]

    def test_get_follow_up_completions_no_task_model(self):
        """Test follow-up generation without task model."""
        self.mock_base_client._get_task_model.return_value = None
        
        result = self.manager._get_follow_up_completions([])
        
        assert result is None

    def test_get_follow_up_completions_plain_text(self):
        """Test follow-up generation with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Question 1?\nQuestion 2?"}}]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._get_follow_up_completions([])
        
        assert result == ["Question 1?", "Question 2?"]

    def test_get_tags_success(self):
        """Test generating tags."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"tags": ["python", "async"]}'}}]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._get_tags([])
        
        assert result == ["python", "async"]

    def test_get_tags_plain_text(self):
        """Test generating tags with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "python, async, testing"}}]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._get_tags([])
        
        assert result == ["python", "async", "testing"]

    def test_get_title_success(self):
        """Test generating title."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"title": "Test Chat Title"}'}}]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._get_title([])
        
        assert result == "Test Chat Title"

    def test_get_title_plain_text(self):
        """Test generating title with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "My Chat Title"}}]
        }
        self.mock_base_client.session.post.return_value = mock_response
        
        result = self.manager._get_title([])
        
        assert result == "My Chat Title"

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
