"""
Tests for AsyncNotesManager module.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from openwebui_chat_client.modules.async_notes_manager import AsyncNotesManager


pytestmark = pytest.mark.asyncio


class TestAsyncNotesManager:
    """Test cases for AsyncNotesManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client._get_json_response = AsyncMock()
        self.manager = AsyncNotesManager(self.base_client)

    def test_initialization(self):
        """Test AsyncNotesManager initialization"""
        assert self.manager.base_client == self.base_client

    async def test_get_notes_success(self):
        """Test getting notes successfully"""
        expected_notes = [
            {"id": "note1", "title": "Note 1", "content": "Content 1"},
            {"id": "note2", "title": "Note 2", "content": "Content 2"},
        ]
        self.base_client._get_json_response.return_value = expected_notes

        result = await self.manager.get_notes()

        assert result == expected_notes
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/notes/"
        )

    async def test_get_notes_empty_list(self):
        """Test getting notes returns empty list"""
        self.base_client._get_json_response.return_value = []

        result = await self.manager.get_notes()

        assert result == []

    async def test_get_notes_none_response(self):
        """Test getting notes when request fails"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager.get_notes()

        assert result is None
