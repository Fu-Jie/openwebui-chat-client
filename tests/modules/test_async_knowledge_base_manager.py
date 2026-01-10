"""
Tests for AsyncKnowledgeBaseManager module.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from openwebui_chat_client.modules.async_knowledge_base_manager import (
    AsyncKnowledgeBaseManager,
)

pytestmark = pytest.mark.asyncio


class TestAsyncKnowledgeBaseManager:
    """Test cases for AsyncKnowledgeBaseManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client._make_request = AsyncMock()
        self.base_client._get_json_response = AsyncMock()
        self.manager = AsyncKnowledgeBaseManager(self.base_client)

    def test_initialization(self):
        """Test AsyncKnowledgeBaseManager initialization"""
        assert self.manager.base_client == self.base_client

    async def test_get_knowledge_base_by_name_found(self):
        """Test getting knowledge base by name when found"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "Test KB", "description": "Test"},
            {"id": "kb2", "name": "Other KB", "description": "Other"},
        ]
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.get_knowledge_base_by_name("Test KB")

        assert result is not None
        assert result["id"] == "kb1"
        assert result["name"] == "Test KB"
        self.base_client._make_request.assert_called_once_with(
            "GET", "/api/v1/knowledge/"
        )

    async def test_get_knowledge_base_by_name_not_found(self):
        """Test getting knowledge base by name when not found"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1", "name": "Test KB"},
            {"id": "kb2", "name": "Other KB"},
        ]
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.get_knowledge_base_by_name("Nonexistent KB")

        assert result is None

    async def test_get_knowledge_base_by_name_empty_list(self):
        """Test getting knowledge base by name with empty list"""
        mock_response = Mock()
        mock_response.json.return_value = []
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.get_knowledge_base_by_name("Any KB")

        assert result is None

    async def test_get_knowledge_base_by_name_no_response(self):
        """Test getting knowledge base by name when request fails"""
        self.base_client._make_request.return_value = None

        result = await self.manager.get_knowledge_base_by_name("Test KB")

        assert result is None

    async def test_get_knowledge_base_by_name_missing_name_field(self):
        """Test getting knowledge base when items missing name field"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "kb1"},  # Missing name field
            {"id": "kb2", "name": "Test KB"},
        ]
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.get_knowledge_base_by_name("Test KB")

        assert result is not None
        assert result["id"] == "kb2"

    async def test_get_knowledge_base_details_success(self):
        """Test getting knowledge base details successfully"""
        expected_details = {
            "id": "kb123",
            "name": "Test KB",
            "description": "Test Description",
            "data": {"files": []},
        }
        self.base_client._get_json_response.return_value = expected_details

        result = await self.manager.get_knowledge_base_details("kb123")

        assert result == expected_details
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/knowledge/kb123"
        )

    async def test_get_knowledge_base_details_not_found(self):
        """Test getting knowledge base details when not found"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager.get_knowledge_base_details("nonexistent")

        assert result is None

    async def test_get_knowledge_base_details_empty_id(self):
        """Test getting knowledge base details with empty ID"""
        expected_details = {"error": "not found"}
        self.base_client._get_json_response.return_value = expected_details

        result = await self.manager.get_knowledge_base_details("")

        assert result == expected_details
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/knowledge/"
        )
