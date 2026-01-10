"""
Tests for AsyncPromptsManager module.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from openwebui_chat_client.modules.async_prompts_manager import AsyncPromptsManager

pytestmark = pytest.mark.asyncio


class TestAsyncPromptsManager:
    """Test cases for AsyncPromptsManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client._get_json_response = AsyncMock()
        self.manager = AsyncPromptsManager(self.base_client)

    def test_initialization(self):
        """Test AsyncPromptsManager initialization"""
        assert self.manager.base_client == self.base_client

    async def test_get_prompts_success(self):
        """Test getting prompts successfully"""
        expected_prompts = [
            {"id": "prompt1", "title": "Prompt 1", "content": "Content 1"},
            {"id": "prompt2", "title": "Prompt 2", "content": "Content 2"},
        ]
        self.base_client._get_json_response.return_value = expected_prompts

        result = await self.manager.get_prompts()

        assert result == expected_prompts
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/prompts/"
        )

    async def test_get_prompts_empty_list(self):
        """Test getting prompts returns empty list"""
        self.base_client._get_json_response.return_value = []

        result = await self.manager.get_prompts()

        assert result == []

    async def test_get_prompts_none_response(self):
        """Test getting prompts when request fails"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager.get_prompts()

        assert result is None
