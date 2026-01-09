"""
Tests for AsyncModelManager module.
"""

import json
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from openwebui_chat_client.modules.async_model_manager import AsyncModelManager


pytestmark = pytest.mark.asyncio


class TestAsyncModelManager:
    """Test cases for AsyncModelManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client._make_request = AsyncMock()
        self.base_client._get_json_response = AsyncMock()
        self.manager = AsyncModelManager(self.base_client)

    def test_initialization(self):
        """Test AsyncModelManager initialization"""
        assert self.manager.base_client == self.base_client
        assert self.manager.available_model_ids == []

    async def test_initialize(self):
        """Test async initialization"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"id": "model1"}, {"id": "model2"}]
        }
        self.base_client._make_request.return_value = mock_response

        await self.manager.initialize()

        assert "model1" in self.manager.available_model_ids
        assert "model2" in self.manager.available_model_ids

    async def test_refresh_available_models(self):
        """Test refreshing available models"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"id": "gpt-4"}, {"id": "claude-3"}]
        }
        self.base_client._make_request.return_value = mock_response

        await self.manager._refresh_available_models()

        assert self.manager.available_model_ids == ["gpt-4", "claude-3"]

    async def test_list_models_success(self):
        """Test listing models successfully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "name": "Model 1"},
                {"id": "model2", "name": "Model 2"},
            ]
        }
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.list_models()

        assert result is not None
        assert len(result) == 2
        assert result[0]["id"] == "model1"
        self.base_client._make_request.assert_called_once_with(
            "GET", "/api/models?refresh=true"
        )

    async def test_list_models_json_decode_error(self):
        """Test list models with JSON decode error"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "", 0)
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.list_models()

        assert result is None

    async def test_list_models_no_response(self):
        """Test list models when request fails"""
        self.base_client._make_request.return_value = None

        result = await self.manager.list_models()

        assert result is None

    async def test_list_base_models_success(self):
        """Test listing base models"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"id": "base1"}, {"id": "base2"}]
        }
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.list_base_models()

        assert result is not None
        assert len(result) == 2
        self.base_client._make_request.assert_called_once_with("GET", "/api/models/base")

    async def test_list_base_models_json_error(self):
        """Test list base models with JSON error"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "", 0)
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.list_base_models()

        assert result is None

    async def test_list_custom_models(self):
        """Test listing custom models"""
        expected_models = [{"id": "custom1"}, {"id": "custom2"}]
        self.base_client._get_json_response.return_value = expected_models

        result = await self.manager.list_custom_models()

        assert result == expected_models
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/models"
        )

    async def test_list_groups(self):
        """Test listing groups"""
        expected_groups = [{"id": "group1", "name": "Group 1"}]
        self.base_client._get_json_response.return_value = expected_groups

        result = await self.manager.list_groups()

        assert result == expected_groups
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/groups/"
        )

    async def test_get_model_empty_id(self):
        """Test get model with empty ID"""
        result = await self.manager.get_model("")

        assert result is None
        self.base_client._make_request.assert_not_called()

    async def test_get_model_success(self):
        """Test getting model successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "model1", "name": "Model 1"}
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.get_model("model1")

        assert result is not None
        assert result["id"] == "model1"

    async def test_get_model_401_create_success(self):
        """Test get model with 401 triggers create"""
        # First call returns 401
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        # Second call (after create) returns 200
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"id": "model1", "name": "Model 1"}

        # Create returns success
        mock_create_response = Mock()
        mock_create_response.json.return_value = {"id": "model1"}

        self.base_client._make_request.side_effect = [
            mock_response_401,
            mock_create_response,
            mock_response_200,
            mock_response_200,  # For refresh
        ]

        result = await self.manager.get_model("model1")

        assert result is not None
        assert result["id"] == "model1"

    async def test_get_model_401_create_fails(self):
        """Test get model with 401 and create fails"""
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        self.base_client._make_request.side_effect = [
            mock_response_401,
            None,  # Create fails
        ]

        result = await self.manager.get_model("model1")

        assert result is None

    async def test_create_model_minimal(self):
        """Test creating model with minimal parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new-model", "name": "New Model"}
        
        # Mock for create and refresh
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": [{"id": "new-model"}]}
        
        self.base_client._make_request.side_effect = [
            mock_response,  # create
            mock_list_response,  # refresh
        ]

        result = await self.manager.create_model(
            model_id="new-model", name="New Model"
        )

        assert result is not None
        assert result["id"] == "new-model"

    async def test_create_model_full_parameters(self):
        """Test creating model with all parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "full-model"}
        
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": []}
        
        self.base_client._make_request.side_effect = [
            mock_response,
            mock_list_response,
        ]

        result = await self.manager.create_model(
            model_id="full-model",
            name="Full Model",
            base_model_id="base-model",
            description="Test description",
            params={"temperature": 0.7},
            permission_type="public",
            profile_image_url="/image.png",
            suggestion_prompts=["prompt1"],
            tags=["tag1"],
            capabilities={"vision": True},
            is_active=True,
        )

        assert result is not None

    async def test_create_model_private_permission(self):
        """Test creating model with private permission"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "private-model"}
        
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": []}
        
        self.base_client._make_request.side_effect = [
            mock_response,
            mock_list_response,
        ]

        result = await self.manager.create_model(
            model_id="private-model",
            name="Private Model",
            permission_type="private",
            user_ids=["user1", "user2"],
        )

        assert result is not None

    async def test_create_model_group_permission_success(self):
        """Test creating model with group permission"""
        # Mock list_groups
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"}
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"id": "group-model"}
        
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": []}
        
        self.base_client._make_request.side_effect = [
            mock_response,
            mock_list_response,
        ]

        result = await self.manager.create_model(
            model_id="group-model",
            name="Group Model",
            permission_type="group",
            group_identifiers=["group1"],
        )

        assert result is not None

    async def test_create_model_group_permission_no_groups(self):
        """Test creating model with group permission but no groups provided"""
        result = await self.manager.create_model(
            model_id="fail-model",
            name="Fail Model",
            permission_type="group",
            group_identifiers=None,
        )

        assert result is None

    async def test_create_model_request_fails(self):
        """Test create model when request fails"""
        self.base_client._make_request.return_value = None

        result = await self.manager.create_model(
            model_id="fail-model", name="Fail Model"
        )

        assert result is None

    async def test_update_model_not_found(self):
        """Test updating non-existent model"""
        self.base_client._make_request.return_value = None

        result = await self.manager.update_model("nonexistent", name="New Name")

        assert result is None

    async def test_update_model_name(self):
        """Test updating model name"""
        # Mock get_model
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": "model1",
            "name": "Old Name",
            "meta": {},
        }

        # Mock update
        mock_update_response = Mock()
        mock_update_response.json.return_value = {
            "id": "model1",
            "name": "New Name",
        }

        self.base_client._make_request.side_effect = [
            mock_get_response,
            mock_update_response,
        ]

        result = await self.manager.update_model("model1", name="New Name")

        assert result is not None
        assert result["name"] == "New Name"

    async def test_update_model_all_fields(self):
        """Test updating all model fields"""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": "model1",
            "name": "Old",
            "meta": {"description": "old desc"},
        }

        mock_update_response = Mock()
        mock_update_response.json.return_value = {"id": "model1"}

        self.base_client._make_request.side_effect = [
            mock_get_response,
            mock_update_response,
        ]

        result = await self.manager.update_model(
            "model1",
            name="New Name",
            base_model_id="new-base",
            description="New description",
            params={"temp": 0.8},
            profile_image_url="/new.png",
            suggestion_prompts=["new prompt"],
            tags=["new-tag"],
            capabilities={"vision": False},
            is_active=False,
        )

        assert result is not None

    async def test_update_model_permission_to_private(self):
        """Test updating model permission to private"""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "model1", "meta": {}}

        mock_update_response = Mock()
        mock_update_response.json.return_value = {"id": "model1"}

        self.base_client._make_request.side_effect = [
            mock_get_response,
            mock_update_response,
        ]

        result = await self.manager.update_model(
            "model1", permission_type="private", user_ids=["user1"]
        )

        assert result is not None

    async def test_update_model_permission_invalid(self):
        """Test updating model with invalid permission"""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "model1", "meta": {}}

        self.base_client._make_request.return_value = mock_get_response

        result = await self.manager.update_model(
            "model1", permission_type="group", group_identifiers=None
        )

        assert result is None

    async def test_delete_model_success(self):
        """Test deleting model successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": []}
        
        self.base_client._make_request.side_effect = [
            mock_response,
            mock_list_response,
        ]

        result = await self.manager.delete_model("model1")

        assert result is True

    async def test_delete_model_405_fallback(self):
        """Test delete model with 405 fallback to POST"""
        mock_response_405 = Mock()
        mock_response_405.status_code = 405

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.raise_for_status = Mock()
        
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"data": []}

        self.base_client._make_request.side_effect = [
            mock_response_405,
            mock_response_200,
            mock_list_response,
        ]

        result = await self.manager.delete_model("model1")

        assert result is True

    async def test_delete_model_http_error(self):
        """Test delete model with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=Mock(), response=Mock()
        )
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.delete_model("model1")

        assert result is False

    async def test_delete_model_unexpected_error(self):
        """Test delete model with unexpected error"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = ValueError("Unexpected")
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.delete_model("model1")

        assert result is False

    async def test_delete_model_no_response(self):
        """Test delete model when request fails"""
        self.base_client._make_request.return_value = None

        result = await self.manager.delete_model("model1")

        assert result is False

    async def test_batch_update_model_permissions(self):
        """Test batch updating model permissions"""
        models = [{"id": "model1"}, {"id": "model2"}]

        # Mock get_model for each update
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "model1", "meta": {}}

        mock_update_response = Mock()
        mock_update_response.json.return_value = {"id": "model1"}

        self.base_client._make_request.side_effect = [
            mock_get_response,
            mock_update_response,
            mock_get_response,
            mock_update_response,
        ]

        result = await self.manager.batch_update_model_permissions(
            models, permission_type="private", user_ids=["user1"]
        )

        assert "model1" in result
        assert "model2" in result
        assert result["model1"]["success"] is True
        assert result["model2"]["success"] is True

    async def test_batch_update_model_permissions_partial_failure(self):
        """Test batch update with some failures"""
        models = [{"id": "model1"}, {"id": "model2"}]

        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "model1", "meta": {}}

        self.base_client._make_request.side_effect = [
            mock_get_response,
            Mock(json=lambda: {"id": "model1"}),
            None,  # Second model fails
        ]

        result = await self.manager.batch_update_model_permissions(
            models, permission_type="public"
        )

        assert result["model1"]["success"] is True
        assert result["model2"]["success"] is False

    async def test_batch_update_empty_model_id(self):
        """Test batch update with empty model ID"""
        models = [{"id": ""}, {"id": "model2"}]

        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"id": "model2", "meta": {}}

        mock_update_response = Mock()
        mock_update_response.json.return_value = {"id": "model2"}

        self.base_client._make_request.side_effect = [
            mock_get_response,
            mock_update_response,
        ]

        result = await self.manager.batch_update_model_permissions(
            models, permission_type="public"
        )

        assert "model2" in result
        assert "" not in result

    async def test_build_access_control_public(self):
        """Test building access control for public permission"""
        result = await self.manager._build_access_control("public", None, None)

        assert result is None

    async def test_build_access_control_private(self):
        """Test building access control for private permission"""
        result = await self.manager._build_access_control(
            "private", None, ["user1", "user2"]
        )

        assert result is not None
        assert result["read"]["user_ids"] == ["user1", "user2"]
        assert result["write"]["user_ids"] == ["user1", "user2"]

    async def test_build_access_control_group_success(self):
        """Test building access control for group permission"""
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"}
        ]

        result = await self.manager._build_access_control(
            "group", ["group1"], ["user1"]
        )

        assert result is not None
        assert result["read"]["group_ids"] == ["group1"]
        assert result["read"]["user_ids"] == ["user1"]

    async def test_build_access_control_group_no_identifiers(self):
        """Test building access control for group without identifiers"""
        result = await self.manager._build_access_control("group", None, None)

        assert result is False

    async def test_build_access_control_invalid_type(self):
        """Test building access control with invalid type"""
        result = await self.manager._build_access_control("invalid", None, None)

        assert result is False

    async def test_resolve_group_ids_by_id(self):
        """Test resolving group IDs when given IDs"""
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"},
            {"id": "group2", "name": "Group 2"},
        ]

        result = await self.manager._resolve_group_ids(["group1", "group2"])

        assert result == ["group1", "group2"]

    async def test_resolve_group_ids_by_name(self):
        """Test resolving group IDs when given names"""
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"},
            {"id": "group2", "name": "Group 2"},
        ]

        result = await self.manager._resolve_group_ids(["Group 1", "Group 2"])

        assert result == ["group1", "group2"]

    async def test_resolve_group_ids_mixed(self):
        """Test resolving group IDs with mixed IDs and names"""
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"},
            {"id": "group2", "name": "Group 2"},
        ]

        result = await self.manager._resolve_group_ids(["group1", "Group 2"])

        assert result == ["group1", "group2"]

    async def test_resolve_group_ids_not_found(self):
        """Test resolving group IDs when group not found"""
        self.base_client._get_json_response.return_value = [
            {"id": "group1", "name": "Group 1"}
        ]

        result = await self.manager._resolve_group_ids(["nonexistent"])

        assert result is False

    async def test_resolve_group_ids_no_groups(self):
        """Test resolving group IDs when list_groups fails"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager._resolve_group_ids(["group1"])

        assert result is False
