"""
Tests for AsyncChatManager module.
"""

import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from openwebui_chat_client.modules.async_chat_manager import AsyncChatManager

pytestmark = pytest.mark.asyncio


class TestAsyncChatManager:
    """Test suite for AsyncChatManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base_client = MagicMock()
        self.mock_base_client.default_model_id = "test-model"
        self.mock_base_client.chat_id = None
        self.mock_base_client.chat_object_from_server = None
        self.mock_base_client._first_stream_request = True

        # Mock async methods
        self.mock_base_client._get_json_response = AsyncMock()
        self.mock_base_client._make_request = AsyncMock()
        self.mock_base_client._upload_file = AsyncMock()
        self.mock_base_client._get_task_model = AsyncMock()

        # Mock httpx client
        self.mock_base_client.client = MagicMock()
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}

        self.manager = AsyncChatManager(self.mock_base_client)

    def test_initialization(self):
        """Test AsyncChatManager initialization."""
        assert self.manager.base_client == self.mock_base_client

    async def test_list_chats_without_page(self):
        """Test listing chats without page parameter."""
        expected_chats = [{"id": "chat1", "title": "Test Chat"}]
        self.mock_base_client._get_json_response.return_value = expected_chats

        result = await self.manager.list_chats()

        assert result == expected_chats
        self.mock_base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/chats/list", params={}
        )

    async def test_list_chats_with_page(self):
        """Test listing chats with page parameter."""
        expected_chats = [{"id": "chat2", "title": "Test Chat 2"}]
        self.mock_base_client._get_json_response.return_value = expected_chats

        result = await self.manager.list_chats(page=2)

        assert result == expected_chats
        self.mock_base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/chats/list", params={"page": 2}
        )

    async def test_delete_all_chats_success(self):
        """Test successful deletion of all chats."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager.delete_all_chats()

        assert result is True
        self.mock_base_client._make_request.assert_called_once_with(
            "DELETE", "/api/v1/chats/", timeout=30
        )

    async def test_delete_all_chats_failure(self):
        """Test failed deletion of all chats."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager.delete_all_chats()

        assert result is False

    async def test_delete_all_chats_exception(self):
        """Test deletion with exception."""
        self.mock_base_client._make_request.side_effect = Exception("Network error")

        result = await self.manager.delete_all_chats()

        assert result is False

    async def test_find_or_create_chat_by_title_existing(self):
        """Test finding an existing chat by title."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Test Chat", "updated_at": 1000},
            {"id": "chat2", "title": "Test Chat", "updated_at": 2000},
        ]
        self.mock_base_client._make_request.return_value = mock_response

        # Mock load_chat_details
        with patch.object(
            self.manager, "_load_chat_details", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = ("chat2", {"chat": {"title": "Test Chat"}})

            chat_id, chat_object = await self.manager._find_or_create_chat_by_title(
                "Test Chat"
            )

            assert chat_id == "chat2"
            assert chat_object == {"chat": {"title": "Test Chat"}}
            mock_load.assert_called_once_with("chat2")

    async def test_find_or_create_chat_by_title_create_new(self):
        """Test creating a new chat when not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        self.mock_base_client._make_request.return_value = mock_response

        with patch.object(
            self.manager, "_create_new_chat", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = ("new_chat", {"chat": {"title": "New Chat"}})

            chat_id, chat_object = await self.manager._find_or_create_chat_by_title(
                "New Chat"
            )

            assert chat_id == "new_chat"
            mock_create.assert_called_once_with("New Chat")

    async def test_create_new_chat_success(self):
        """Test successful creation of a new chat."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new_chat_id"}
        self.mock_base_client._make_request.return_value = mock_response

        with patch.object(
            self.manager, "_load_chat_details", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = ("new_chat_id", {"chat": {"title": "New"}})

            chat_id, chat_object = await self.manager._create_new_chat("New")

            assert chat_id == "new_chat_id"
            self.mock_base_client._make_request.assert_called_once_with(
                "POST", "/api/v1/chats/new", json_data={"chat": {"title": "New"}}
            )

    async def test_create_new_chat_failure(self):
        """Test failed creation of a new chat."""
        self.mock_base_client._make_request.return_value = None

        chat_id, chat_object = await self.manager._create_new_chat("New")

        assert chat_id is None
        assert chat_object is None

    async def test_load_chat_details_success(self):
        """Test successful loading of chat details."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "chat1", "chat": {"title": "Test"}}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        self.mock_base_client.client = mock_client

        chat_id, chat_object = await self.manager._load_chat_details("chat1")

        assert chat_id == "chat1"
        assert chat_object == {"id": "chat1", "chat": {"title": "Test"}}
        assert self.mock_base_client.chat_id == "chat1"

    async def test_load_chat_details_with_retry(self):
        """Test loading chat details with retry on 401."""
        import httpx

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        mock_response_401.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=mock_response_401
        )

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"id": "chat1", "chat": {"title": "Test"}}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[mock_response_401, mock_response_200])
        self.mock_base_client.client = mock_client

        chat_id, chat_object = await self.manager._load_chat_details("chat1")

        assert chat_id == "chat1"
        assert mock_client.get.call_count == 2

    async def test_load_chat_details_timeout(self):
        """Test loading chat details with timeout."""
        import httpx

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        self.mock_base_client.client = mock_client

        chat_id, chat_object = await self.manager._load_chat_details("chat1")

        assert chat_id is None
        assert chat_object is None

    async def test_load_chat_details_http_error(self):
        """Test loading chat details with HTTP error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "500", request=MagicMock(), response=mock_response
            )
        )
        self.mock_base_client.client = mock_client

        chat_id, chat_object = await self.manager._load_chat_details("chat1")

        assert chat_id is None
        assert chat_object is None

    async def test_update_remote_chat_success(self):
        """Test successful remote chat update."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_base_client._make_request.return_value = mock_response

        chat_data = {"title": "Updated", "messages": []}
        result = await self.manager._update_remote_chat("chat1", chat_data)

        assert result is True
        self.mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/api/v1/chats/chat1",
            json_data={"chat": chat_data},
            timeout=30,
        )

    async def test_update_remote_chat_failure(self):
        """Test failed remote chat update."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._update_remote_chat("chat1", {"title": "Test"})

        assert result is False

    async def test_update_remote_chat_missing_params(self):
        """Test remote chat update with missing parameters."""
        result = await self.manager._update_remote_chat(None, {"title": "Test"})
        assert result is False

        result = await self.manager._update_remote_chat("chat1", None)
        assert result is False

    def test_build_linear_history_for_api(self):
        """Test building linear history for API calls."""
        chat_data = {
            "history": {
                "messages": {
                    "msg1": {
                        "id": "msg1",
                        "role": "user",
                        "content": "Hello",
                        "parentId": None,
                    },
                    "msg2": {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "Hi",
                        "parentId": "msg1",
                    },
                    "msg3": {
                        "id": "msg3",
                        "role": "user",
                        "content": "How are you?",
                        "parentId": "msg2",
                    },
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

    def test_is_placeholder_message(self):
        """Test placeholder message detection."""
        placeholder = {"content": "", "done": False}
        assert self.manager._is_placeholder_message(placeholder) is True

        not_placeholder = {"content": "Hello", "done": False}
        assert self.manager._is_placeholder_message(not_placeholder) is False

        done_message = {"content": "", "done": True}
        assert self.manager._is_placeholder_message(done_message) is False

    def test_count_available_placeholder_pairs(self):
        """Test counting available placeholder pairs."""
        chat_object = {
            "chat": {
                "history": {
                    "messages": {
                        "user1": {
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": True,
                            "childrenIds": ["asst1"],
                        },
                        "asst1": {
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": True,
                        },
                        "user2": {
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": False,
                            "childrenIds": ["asst2"],
                        },
                        "asst2": {
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": False,
                        },
                    }
                }
            }
        }

        count = self.manager._count_available_placeholder_pairs(chat_object)
        assert count == 1

    async def test_ensure_placeholder_messages_sufficient(self):
        """Test ensuring placeholder messages when sufficient."""
        chat_object = {
            "chat": {
                "history": {
                    "messages": {
                        f"user{i}": {
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": True,
                            "childrenIds": [f"asst{i}"],
                        }
                        for i in range(15)
                    }
                    | {
                        f"asst{i}": {
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": True,
                        }
                        for i in range(15)
                    },
                    "currentId": "asst14",
                }
            }
        }

        result = await self.manager._ensure_placeholder_messages(
            "chat1", chat_object, pool_size=30, min_available=10
        )

        assert result is True
        # Should not create new messages since we have 15 available (>= 10)

    async def test_ensure_placeholder_messages_create_new(self):
        """Test creating new placeholder messages."""
        chat_object = {
            "chat": {
                "history": {
                    "messages": {},
                    "currentId": None,
                }
            }
        }

        with patch.object(
            self.manager, "_update_remote_chat", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = True

            result = await self.manager._ensure_placeholder_messages(
                "chat1", chat_object, pool_size=5, min_available=5
            )

            assert result is True
            # Should create 5 pairs (10 messages total)
            assert len(chat_object["chat"]["history"]["messages"]) == 10
            mock_update.assert_called_once()

    def test_cleanup_unused_placeholder_messages(self):
        """Test cleanup of unused placeholder messages."""
        chat_object = {
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
                        "user2": {
                            "id": "user2",
                            "role": "user",
                            "_is_placeholder": True,
                            "_is_available": False,
                            "childrenIds": ["asst2"],
                        },
                        "asst2": {
                            "id": "asst2",
                            "role": "assistant",
                            "_is_placeholder": True,
                            "_is_available": False,
                        },
                    }
                }
            }
        }

        count = self.manager._cleanup_unused_placeholder_messages(chat_object)

        assert count == 1
        assert "user1" not in chat_object["chat"]["history"]["messages"]
        assert "asst1" not in chat_object["chat"]["history"]["messages"]
        assert "user2" in chat_object["chat"]["history"]["messages"]

    def test_get_next_available_message_pair(self):
        """Test getting next available message pair."""
        chat_object = {
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

        result = self.manager._get_next_available_message_pair(chat_object)

        assert result == ("user1", "asst1")
        # Should mark as unavailable
        assert (
            chat_object["chat"]["history"]["messages"]["user1"]["_is_available"]
            is False
        )
        assert (
            chat_object["chat"]["history"]["messages"]["asst1"]["_is_available"]
            is False
        )

    def test_get_next_available_message_pair_none_available(self):
        """Test getting message pair when none available."""
        chat_object = {"chat": {"history": {"messages": {}}}}

        result = self.manager._get_next_available_message_pair(chat_object)

        assert result is None

    async def test_stream_delta_update(self):
        """Test streaming delta update."""
        self.mock_base_client._make_request.return_value = MagicMock()

        await self.manager._stream_delta_update("chat1", "msg1", "Hello")

        self.mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/api/v1/chats/chat1/messages/msg1/event",
            json_data={"type": "chat:message:delta", "data": {"content": "Hello"}},
            timeout=3.0,
        )

    async def test_stream_delta_update_empty_content(self):
        """Test streaming delta update with empty content."""
        await self.manager._stream_delta_update("chat1", "msg1", "  ")

        # Should not make request for empty content
        self.mock_base_client._make_request.assert_not_called()

    async def test_stream_delta_update_exception(self):
        """Test streaming delta update with exception."""
        self.mock_base_client._make_request.side_effect = Exception("Network error")

        # Should not raise exception
        await self.manager._stream_delta_update("chat1", "msg1", "Hello")

    def test_encode_image_to_base64_success(self):
        """Test encoding image to base64."""
        import os
        import tempfile

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG header
            temp_path = f.name

        try:
            result = self.manager._encode_image_to_base64(temp_path)

            assert result is not None
            assert result.startswith("data:image/png;base64,")
        finally:
            os.unlink(temp_path)

    def test_encode_image_to_base64_file_not_found(self):
        """Test encoding non-existent image."""
        result = self.manager._encode_image_to_base64("/nonexistent/image.png")

        assert result is None

    def test_encode_image_to_base64_different_formats(self):
        """Test encoding different image formats."""
        import os
        import tempfile

        formats = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".gif", "image/gif"),
            (".webp", "image/webp"),
        ]

        for ext, media_type in formats:
            with tempfile.NamedTemporaryFile(mode="wb", suffix=ext, delete=False) as f:
                f.write(b"fake image data")
                temp_path = f.name

            try:
                result = self.manager._encode_image_to_base64(temp_path)
                assert result is not None
                assert result.startswith(f"data:{media_type};base64,")
            finally:
                os.unlink(temp_path)

    async def test_handle_rag_references_files(self):
        """Test handling RAG file references."""
        file_obj = {"id": "file1", "name": "test.pdf"}
        self.mock_base_client._upload_file.return_value = file_obj

        api_payload, storage_payload = await self.manager._handle_rag_references(
            rag_files=["test.pdf"]
        )

        assert len(api_payload) == 1
        assert api_payload[0] == {"type": "file", "id": "file1"}
        assert len(storage_payload) == 1
        assert storage_payload[0]["type"] == "file"

    async def test_handle_rag_references_collections(self):
        """Test handling RAG knowledge base collections."""
        kb_list = [{"id": "kb1", "name": "Test KB"}]
        kb_details = {
            "id": "kb1",
            "name": "Test KB",
            "files": [{"id": "f1"}, {"id": "f2"}],
        }

        self.mock_base_client._get_json_response.side_effect = [kb_list, kb_details]

        api_payload, storage_payload = await self.manager._handle_rag_references(
            rag_collections=["Test KB"]
        )

        assert len(api_payload) == 1
        assert api_payload[0]["type"] == "collection"
        assert api_payload[0]["id"] == "kb1"
        assert api_payload[0]["data"]["file_ids"] == ["f1", "f2"]

    async def test_handle_rag_references_both(self):
        """Test handling both files and collections."""
        file_obj = {"id": "file1", "name": "test.pdf"}
        self.mock_base_client._upload_file.return_value = file_obj

        kb_list = [{"id": "kb1", "name": "Test KB"}]
        kb_details = {"id": "kb1", "name": "Test KB", "files": [{"id": "f1"}]}
        self.mock_base_client._get_json_response.side_effect = [kb_list, kb_details]

        api_payload, storage_payload = await self.manager._handle_rag_references(
            rag_files=["test.pdf"], rag_collections=["Test KB"]
        )

        assert len(api_payload) == 2
        assert len(storage_payload) == 2

    async def test_get_follow_up_completions_success(self):
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
        self.mock_base_client._make_request.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = await self.manager._get_follow_up_completions(messages)

        assert result == ["Question 1?", "Question 2?"]

    async def test_get_follow_up_completions_no_task_model(self):
        """Test follow-up generation without task model."""
        self.mock_base_client._get_task_model.return_value = None

        result = await self.manager._get_follow_up_completions([])

        assert result is None

    async def test_get_follow_up_completions_plain_text(self):
        """Test follow-up generation with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Question 1?\nQuestion 2?"}}]
        }
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_follow_up_completions([])

        assert result == ["Question 1?", "Question 2?"]

    async def test_get_tags_success(self):
        """Test generating tags."""
        self.mock_base_client._get_task_model.return_value = "task-model"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"tags": ["python", "async"]}'}}]
        }
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_tags([])

        assert result == ["python", "async"]

    async def test_get_tags_plain_text(self):
        """Test generating tags with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "python, async, testing"}}]
        }
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_tags([])

        assert result == ["python", "async", "testing"]

    async def test_get_title_success(self):
        """Test generating title."""
        self.mock_base_client._get_task_model.return_value = "task-model"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"title": "Test Chat Title"}'}}]
        }
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_title([])

        assert result == "Test Chat Title"

    async def test_get_title_plain_text(self):
        """Test generating title with plain text response."""
        self.mock_base_client._get_task_model.return_value = "task-model"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "My Chat Title"}}]
        }
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_title([])

        assert result == "My Chat Title"

    async def test_set_chat_tags(self):
        """Test setting chat tags."""
        # Mock existing tags
        existing_response = MagicMock()
        existing_response.json.return_value = [{"name": "existing"}]

        self.mock_base_client._make_request.side_effect = [
            existing_response,
            MagicMock(),  # For new tag
        ]

        await self.manager._set_chat_tags("chat1", ["existing", "new"])

        # Should only create the new tag
        assert self.mock_base_client._make_request.call_count == 2

    async def test_set_chat_tags_empty(self):
        """Test setting empty tags."""
        await self.manager._set_chat_tags("chat1", [])

        self.mock_base_client._make_request.assert_not_called()

    async def test_rename_chat_success(self):
        """Test renaming chat."""
        self.mock_base_client._make_request.return_value = MagicMock()

        result = await self.manager._rename_chat("chat1", "New Title")

        assert result is True
        self.mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/api/v1/chats/chat1",
            json_data={"chat": {"title": "New Title"}},
        )

    async def test_rename_chat_failure(self):
        """Test failed chat rename."""
        self.mock_base_client._make_request.return_value = None

        result = await self.manager._rename_chat("chat1", "New Title")

        assert result is False

    async def test_get_folder_id_by_name_found(self):
        """Test getting folder ID by name."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "folder1", "name": "Test Folder"},
            {"id": "folder2", "name": "Other Folder"},
        ]
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_folder_id_by_name("Test Folder")

        assert result == "folder1"

    async def test_get_folder_id_by_name_not_found(self):
        """Test getting folder ID when not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._get_folder_id_by_name("Nonexistent")

        assert result is None

    async def test_create_folder_success(self):
        """Test creating a folder."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new_folder"}
        self.mock_base_client._make_request.return_value = mock_response

        result = await self.manager._create_folder("New Folder")

        assert result == "new_folder"

    async def test_create_folder_fallback(self):
        """Test creating folder with fallback to lookup."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        self.mock_base_client._make_request.return_value = mock_response

        with patch.object(
            self.manager, "_get_folder_id_by_name", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = "folder_id"

            result = await self.manager._create_folder("New Folder")

            assert result == "folder_id"

    async def test_move_chat_to_folder(self):
        """Test moving chat to folder."""
        self.mock_base_client._make_request.return_value = MagicMock()

        await self.manager._move_chat_to_folder("chat1", "folder1")

        self.mock_base_client._make_request.assert_called_once_with(
            "POST",
            "/api/v1/chats/chat1/folder",
            json_data={"folder_id": "folder1"},
        )

    async def test_ensure_folder_existing(self):
        """Test ensuring folder when it exists."""
        with patch.object(
            self.manager, "_get_folder_id_by_name", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = "folder1"

            with patch.object(
                self.manager, "_move_chat_to_folder", new_callable=AsyncMock
            ) as mock_move:
                await self.manager._ensure_folder("chat1", "Test Folder")

                mock_move.assert_called_once_with("chat1", "folder1")

    async def test_ensure_folder_create_new(self):
        """Test ensuring folder when it doesn't exist."""
        with patch.object(
            self.manager, "_get_folder_id_by_name", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            with patch.object(
                self.manager, "_create_folder", new_callable=AsyncMock
            ) as mock_create:
                mock_create.return_value = "new_folder"

                with patch.object(
                    self.manager, "_move_chat_to_folder", new_callable=AsyncMock
                ) as mock_move:
                    await self.manager._ensure_folder("chat1", "New Folder")

                    mock_create.assert_called_once_with("New Folder")
                    mock_move.assert_called_once_with("chat1", "new_folder")

    async def test_chat_basic(self):
        """Test basic chat functionality."""
        with patch.object(
            self.manager, "_find_or_create_chat_by_title", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = ("chat1", {"chat": {"history": {"messages": {}}}})

            with patch.object(self.manager, "_ask", new_callable=AsyncMock) as mock_ask:
                mock_ask.return_value = {"response": "Hello!", "chat_id": "chat1"}

                result = await self.manager.chat("Hi", "Test Chat")

                assert result == {"response": "Hello!", "chat_id": "chat1"}
                mock_find.assert_called_once_with("Test Chat")
                mock_ask.assert_called_once()

    async def test_chat_with_custom_model(self):
        """Test chat with custom model."""
        with patch.object(
            self.manager, "_find_or_create_chat_by_title", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = ("chat1", {"chat": {"history": {"messages": {}}}})

            with patch.object(self.manager, "_ask", new_callable=AsyncMock) as mock_ask:
                await self.manager.chat("Hi", "Test", model_id="custom-model")

                # Check that custom model was passed
                call_args = mock_ask.call_args
                assert call_args[0][3] == "custom-model"

    async def test_chat_failure_no_chat(self):
        """Test chat when chat creation fails."""
        with patch.object(
            self.manager, "_find_or_create_chat_by_title", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = (None, None)

            result = await self.manager.chat("Hi", "Test")

            assert result is None
