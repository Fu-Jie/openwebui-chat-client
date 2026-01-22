"""
Comprehensive tests for BaseManager class.
Tests all utility methods for pagination, filtering, access control, batch operations, etc.
"""

import unittest
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any, List
import json

from openwebui_chat_client.core.base_manager import BaseManager
from openwebui_chat_client.core.base_client import BaseClient


class TestBaseManager(unittest.TestCase):
    """Test suite for BaseManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock base client
        self.mock_base_client = MagicMock(spec=BaseClient)
        self.mock_base_client.base_url = "http://localhost:3003"
        self.mock_base_client.session = MagicMock()
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}

        # Create BaseManager instance
        self.manager = BaseManager(self.mock_base_client)

    # ==================== Core Properties Tests ====================

    def test_session_property(self):
        """Test session property access."""
        self.assertEqual(self.manager.session, self.mock_base_client.session)

    def test_base_url_property(self):
        """Test base_url property access."""
        self.assertEqual(self.manager.base_url, "http://localhost:3003")

    def test_json_headers_property(self):
        """Test json_headers property access."""
        self.assertEqual(
            self.manager.json_headers, {"Content-Type": "application/json"}
        )

    # ==================== Pagination Tests ====================

    def test_build_pagination_params_default(self):
        """Test default pagination parameters."""
        params = self.manager._build_pagination_params()

        # When no parameters provided, should return limit only (skip defaults to 0 when page is used)
        self.assertEqual(params.get("limit"), 30)  # DEFAULT_PAGE_SIZE
        # skip is not included when no page/skip parameter is provided

    def test_build_pagination_params_with_page(self):
        """Test pagination with page number."""
        params = self.manager._build_pagination_params(page=2)

        self.assertEqual(params["skip"], 30)  # (2-1) * 30
        self.assertEqual(params["limit"], 30)

    def test_build_pagination_params_with_page_and_page_size(self):
        """Test pagination with custom page size."""
        params = self.manager._build_pagination_params(page=3, page_size=50)

        self.assertEqual(params["skip"], 100)  # (3-1) * 50
        self.assertEqual(params["limit"], 50)

    def test_build_pagination_params_with_skip_and_limit(self):
        """Test pagination with explicit skip and limit."""
        params = self.manager._build_pagination_params(skip=20, limit=10)

        self.assertEqual(params["skip"], 20)
        self.assertEqual(params["limit"], 10)

    def test_build_pagination_params_skip_priority(self):
        """Test that explicit skip takes priority over page."""
        params = self.manager._build_pagination_params(page=2, skip=15, page_size=10)

        self.assertEqual(params["skip"], 15)  # skip has priority

    def test_build_pagination_params_limit_priority(self):
        """Test that explicit limit takes priority."""
        params = self.manager._build_pagination_params(page_size=50, limit=25)

        self.assertEqual(params["limit"], 25)  # limit has priority

    def test_build_pagination_params_max_limit(self):
        """Test that limit is capped at MAX_PAGE_SIZE."""
        params = self.manager._build_pagination_params(limit=200)

        self.assertEqual(params["limit"], 100)  # MAX_PAGE_SIZE

    def test_build_pagination_params_negative_values(self):
        """Test that negative values are handled correctly."""
        params = self.manager._build_pagination_params(page=-1, skip=-5)

        self.assertEqual(params["skip"], 0)  # max(0, skip)
        self.assertEqual(params["limit"], 30)

    # ==================== Filtering Tests ====================

    def test_build_filter_params_empty(self):
        """Test empty filter parameters."""
        params = self.manager._build_filter_params()

        self.assertEqual(params, {})

    def test_build_filter_params_with_query(self):
        """Test filter with search query."""
        params = self.manager._build_filter_params(query="test search")

        self.assertEqual(params["query"], "test search")

    def test_build_filter_params_with_view_option(self):
        """Test filter with view option."""
        params = self.manager._build_filter_params(view_option="archived")

        self.assertEqual(params["view_option"], "archived")

    def test_build_filter_params_with_ordering(self):
        """Test filter with ordering."""
        params = self.manager._build_filter_params(
            order_by="created_at", direction="desc"
        )

        self.assertEqual(params["order_by"], "created_at")
        self.assertEqual(params["direction"], "desc")

    def test_build_filter_params_with_additional_filters(self):
        """Test filter with additional custom parameters."""
        params = self.manager._build_filter_params(
            query="test", custom_field="value", another_field=123
        )

        self.assertEqual(params["query"], "test")
        self.assertEqual(params["custom_field"], "value")
        self.assertEqual(params["another_field"], 123)

    def test_build_filter_params_complete(self):
        """Test filter with all parameters."""
        params = self.manager._build_filter_params(
            query="search term",
            view_option="active",
            order_by="updated_at",
            direction="asc",
            status="published",
            tags=["tag1", "tag2"],
        )

        self.assertEqual(len(params), 6)
        self.assertEqual(params["query"], "search term")
        self.assertEqual(params["status"], "published")

    # ==================== Response Parsing Tests ====================

    def test_parse_list_response_simple_list(self):
        """Test parsing simple list response."""
        response = [{"id": 1}, {"id": 2}, {"id": 3}]

        items, total = self.manager._parse_list_response(response)

        self.assertEqual(items, response)
        self.assertEqual(total, 3)

    def test_parse_list_response_with_data_field(self):
        """Test parsing response with 'data' field."""
        response = {"data": [{"id": 1}, {"id": 2}], "total": 100}

        items, total = self.manager._parse_list_response(response)

        self.assertEqual(items, [{"id": 1}, {"id": 2}])
        self.assertEqual(total, 100)

    def test_parse_list_response_with_items_field(self):
        """Test parsing response with 'items' field."""
        response = {"items": [{"id": 1}, {"id": 2}, {"id": 3}], "total": 50}

        items, total = self.manager._parse_list_response(response)

        self.assertEqual(items, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(total, 50)

    def test_parse_list_response_dict_without_total(self):
        """Test parsing dict response without total field."""
        response = {"data": [{"id": 1}, {"id": 2}]}

        items, total = self.manager._parse_list_response(response)

        self.assertEqual(items, [{"id": 1}, {"id": 2}])
        self.assertEqual(total, 2)  # Inferred from items length

    def test_parse_list_response_empty_list(self):
        """Test parsing empty list."""
        items, total = self.manager._parse_list_response([])

        self.assertEqual(items, [])
        self.assertEqual(total, 0)

    def test_parse_list_response_invalid_type(self):
        """Test parsing invalid response type."""
        items, total = self.manager._parse_list_response("invalid")

        self.assertEqual(items, [])
        self.assertIsNone(total)

    # ==================== Access Control Tests ====================

    def test_build_access_control_public(self):
        """Test building public access control."""
        result = self.manager._build_access_control("public")

        self.assertIsNone(result)

    def test_build_access_control_private(self):
        """Test building private access control."""
        result = self.manager._build_access_control(
            "private", group_ids=["group1", "group2"], user_ids=["user1"]
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["read"]["group_ids"], ["group1", "group2"])
        self.assertEqual(result["read"]["user_ids"], ["user1"])
        self.assertEqual(result["write"]["group_ids"], ["group1", "group2"])
        self.assertEqual(result["write"]["user_ids"], ["user1"])

    def test_build_access_control_empty_lists(self):
        """Test access control with empty lists."""
        result = self.manager._build_access_control("private")

        self.assertEqual(result["read"]["group_ids"], [])
        self.assertEqual(result["read"]["user_ids"], [])

    def test_check_write_access_admin(self):
        """Test that admin has write access to everything."""
        resource = {"user_id": "other_user"}

        has_access = self.manager._check_write_access(
            resource, user_id="current_user", user_role="admin"
        )

        self.assertTrue(has_access)

    def test_check_write_access_owner(self):
        """Test that owner has write access."""
        resource = {"user_id": "current_user"}

        has_access = self.manager._check_write_access(
            resource, user_id="current_user", user_role="user"
        )

        self.assertTrue(has_access)

    def test_check_write_access_in_user_list(self):
        """Test write access via user_ids list."""
        resource = {
            "user_id": "owner",
            "access_control": {
                "write": {"user_ids": ["current_user"], "group_ids": []}
            },
        }

        has_access = self.manager._check_write_access(
            resource, user_id="current_user", user_role="user"
        )

        self.assertTrue(has_access)

    def test_check_write_access_denied(self):
        """Test write access denied."""
        resource = {
            "user_id": "owner",
            "access_control": {"write": {"user_ids": ["other_user"], "group_ids": []}},
        }

        has_access = self.manager._check_write_access(
            resource, user_id="current_user", user_role="user"
        )

        self.assertFalse(has_access)

    def test_check_write_access_no_access_control(self):
        """Test access check when no access_control field."""
        resource = {"user_id": "owner"}

        has_access = self.manager._check_write_access(
            resource, user_id="current_user", user_role="user"
        )

        self.assertFalse(has_access)

    # ==================== Batch Operations Tests ====================

    def test_batch_operation_all_success(self):
        """Test batch operation with all successful items."""
        items = ["item1", "item2", "item3"]

        def mock_operation(item):
            return {"id": item, "status": "success"}

        results = self.manager._batch_operation(items, mock_operation, max_workers=2)

        self.assertEqual(len(results["success"]), 3)
        self.assertEqual(len(results["failed"]), 0)

    def test_batch_operation_with_failures(self):
        """Test batch operation with some failures."""
        items = ["item1", "item2", "item3"]

        def mock_operation(item):
            if item == "item2":
                raise ValueError(f"Failed to process {item}")
            return {"id": item}

        results = self.manager._batch_operation(
            items, mock_operation, continue_on_error=True
        )

        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 1)
        self.assertEqual(results["failed"][0]["item"], "item2")

    def test_batch_operation_return_none(self):
        """Test batch operation when operation returns None."""
        items = ["item1", "item2"]

        def mock_operation(item):
            if item == "item1":
                return None
            return {"id": item}

        results = self.manager._batch_operation(items, mock_operation)

        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failed"]), 1)
        self.assertIn("Operation returned None", results["failed"][0]["error"])

    def test_batch_operation_stop_on_error(self):
        """Test batch operation stops on first error."""
        items = ["item1", "item2", "item3"]

        def mock_operation(item):
            if item == "item2":
                raise ValueError("Error")
            return {"id": item}

        results = self.manager._batch_operation(
            items, mock_operation, continue_on_error=False
        )

        # Should have at least one failure and may have stopped early
        self.assertGreater(len(results["failed"]), 0)

    def test_batch_operation_empty_list(self):
        """Test batch operation with empty list."""
        results = self.manager._batch_operation([], lambda x: x)

        self.assertEqual(len(results["success"]), 0)
        self.assertEqual(len(results["failed"]), 0)

    # ==================== Validation Tests ====================

    def test_validate_required_fields_all_present(self):
        """Test validation when all required fields are present."""
        data = {"name": "Test", "id": "123", "type": "demo"}
        required = ["name", "id", "type"]

        result = self.manager._validate_required_fields(data, required, "Test context")

        self.assertTrue(result)

    def test_validate_required_fields_missing_field(self):
        """Test validation when required field is missing."""
        data = {"name": "Test", "type": "demo"}
        required = ["name", "id", "type"]

        with self.assertLogs(level="ERROR"):
            result = self.manager._validate_required_fields(
                data, required, "Test context"
            )

        self.assertFalse(result)

    def test_validate_required_fields_empty_value(self):
        """Test validation when required field is empty."""
        data = {"name": "", "id": "123", "type": "demo"}
        required = ["name", "id", "type"]

        with self.assertLogs(level="ERROR"):
            result = self.manager._validate_required_fields(
                data, required, "Test context"
            )

        self.assertFalse(result)

    def test_validate_required_fields_none_value(self):
        """Test validation when required field is None."""
        data = {"name": "Test", "id": None, "type": "demo"}
        required = ["name", "id", "type"]

        with self.assertLogs(level="ERROR"):
            result = self.manager._validate_required_fields(
                data, required, "Test context"
            )

        self.assertFalse(result)

    def test_validate_enum_value_valid(self):
        """Test enum validation with valid value."""
        result = self.manager._validate_enum_value(
            "active", ["active", "inactive", "pending"], "status"
        )

        self.assertTrue(result)

    def test_validate_enum_value_invalid(self):
        """Test enum validation with invalid value."""
        with self.assertLogs(level="ERROR"):
            result = self.manager._validate_enum_value(
                "invalid", ["active", "inactive", "pending"], "status"
            )

        self.assertFalse(result)

    def test_validate_enum_value_case_sensitive(self):
        """Test that enum validation is case-sensitive."""
        with self.assertLogs(level="ERROR"):
            result = self.manager._validate_enum_value(
                "Active", ["active", "inactive"], "status"
            )

        self.assertFalse(result)

    # ==================== URL Building Tests ====================

    def test_build_url_simple(self):
        """Test building simple URL without parameters."""
        url = self.manager._build_url("/api/chats")

        self.assertEqual(url, "http://localhost:3003/api/chats")

    def test_build_url_with_trailing_slash(self):
        """Test URL building handles trailing slashes."""
        url = self.manager._build_url("/api/chats/")

        self.assertEqual(url, "http://localhost:3003/api/chats/")

    def test_build_url_with_path_params(self):
        """Test URL building with path parameters."""
        url = self.manager._build_url(
            "/api/chats/{chat_id}/messages/{message_id}",
            {"chat_id": "abc123", "message_id": "msg456"},
        )

        self.assertEqual(url, "http://localhost:3003/api/chats/abc123/messages/msg456")

    def test_build_url_with_special_chars(self):
        """Test URL building encodes special characters."""
        url = self.manager._build_url(
            "/api/files/{filename}", {"filename": "my file.pdf"}
        )

        self.assertIn("my%20file.pdf", url)

    def test_encode_path_param_simple(self):
        """Test simple path parameter encoding."""
        encoded = self.manager._encode_path_param("simple")

        self.assertEqual(encoded, "simple")

    def test_encode_path_param_with_spaces(self):
        """Test encoding parameter with spaces."""
        encoded = self.manager._encode_path_param("hello world")

        self.assertEqual(encoded, "hello%20world")

    def test_encode_path_param_with_special_chars(self):
        """Test encoding parameter with special characters."""
        encoded = self.manager._encode_path_param("test@email.com")

        self.assertIn("%40", encoded)

    def test_encode_path_param_numeric(self):
        """Test encoding numeric parameter."""
        encoded = self.manager._encode_path_param(123)

        self.assertEqual(encoded, "123")

    # ==================== Logging Tests ====================

    def test_format_context_empty(self):
        """Test formatting empty context."""
        result = self.manager._format_context({})

        self.assertEqual(result, "")

    def test_format_context_single_item(self):
        """Test formatting context with single item."""
        result = self.manager._format_context({"user_id": "123"})

        self.assertEqual(result, "[user_id=123]")

    def test_format_context_multiple_items(self):
        """Test formatting context with multiple items."""
        result = self.manager._format_context(
            {"user_id": "123", "chat_id": "abc", "model": "gpt-4"}
        )

        self.assertIn("user_id=123", result)
        self.assertIn("chat_id=abc", result)
        self.assertIn("model=gpt-4", result)
        self.assertTrue(result.startswith("["))
        self.assertTrue(result.endswith("]"))

    def test_log_operation_start(self):
        """Test logging operation start."""
        with self.assertLogs(self.manager.logger, level="INFO") as cm:
            self.manager._log_operation_start(
                "Creating chat", user_id="123", model="gpt-4"
            )

        self.assertTrue(any("🔄" in msg for msg in cm.output))
        self.assertTrue(any("Creating chat" in msg for msg in cm.output))

    def test_log_operation_success(self):
        """Test logging operation success."""
        with self.assertLogs(self.manager.logger, level="INFO") as cm:
            self.manager._log_operation_success(
                "Chat created", result="chat_123", user_id="123"
            )

        self.assertTrue(any("✅" in msg for msg in cm.output))
        self.assertTrue(any("Chat created" in msg for msg in cm.output))

    def test_log_operation_failure(self):
        """Test logging operation failure."""
        error = ValueError("Test error")

        with self.assertLogs(self.manager.logger, level="ERROR") as cm:
            self.manager._log_operation_failure("Chat creation", error, user_id="123")

        self.assertTrue(any("❌" in msg for msg in cm.output))
        self.assertTrue(any("Chat creation" in msg for msg in cm.output))
        self.assertTrue(any("Test error" in msg for msg in cm.output))

    # ==================== HTTP Request Tests ====================

    def test_make_request_delegates_to_base_client(self):
        """Test that _make_request delegates to base client."""
        mock_response = MagicMock()
        self.mock_base_client._make_request.return_value = mock_response

        result = self.manager._make_request("POST", "/api/test", json={"key": "value"})

        self.mock_base_client._make_request.assert_called_once_with(
            "POST", "/api/test", json={"key": "value"}
        )
        self.assertEqual(result, mock_response)

    def test_get_json_response_success(self):
        """Test getting JSON response successfully."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        self.mock_base_client._make_request.return_value = mock_response

        result = self.manager._get_json_response("GET", "/api/test")

        self.assertEqual(result, {"data": "test"})

    def test_get_json_response_parse_error(self):
        """Test handling JSON parse error."""
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        self.mock_base_client._make_request.return_value = mock_response

        with self.assertLogs(self.manager.logger, level="ERROR"):
            result = self.manager._get_json_response("GET", "/api/test")

        self.assertIsNone(result)

    def test_get_json_response_no_response(self):
        """Test handling when request returns None."""
        self.mock_base_client._make_request.return_value = None

        result = self.manager._get_json_response("GET", "/api/test")

        self.assertIsNone(result)


class TestBaseManagerIntegration(unittest.TestCase):
    """Integration tests for BaseManager with realistic scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_base_client = MagicMock(spec=BaseClient)
        self.mock_base_client.base_url = "http://localhost:3003"
        self.manager = BaseManager(self.mock_base_client)

    def test_paginated_list_scenario(self):
        """Test realistic paginated list scenario."""
        # Simulate fetching page 2 with 50 items per page
        pagination = self.manager._build_pagination_params(page=2, page_size=50)

        filters = self.manager._build_filter_params(
            query="test", order_by="created_at", direction="desc"
        )

        # Verify params are correct for API call
        self.assertEqual(pagination["skip"], 50)
        self.assertEqual(pagination["limit"], 50)
        self.assertEqual(filters["query"], "test")
        self.assertEqual(filters["order_by"], "created_at")

    def test_access_control_workflow(self):
        """Test complete access control workflow."""
        # Create private resource with specific access
        access_control = self.manager._build_access_control(
            "private", group_ids=["team1"], user_ids=["user1", "user2"]
        )

        resource = {
            "id": "resource123",
            "user_id": "owner",
            "access_control": access_control,
        }

        # Owner should have access
        self.assertTrue(self.manager._check_write_access(resource, "owner", "user"))

        # User in list should have access
        self.assertTrue(self.manager._check_write_access(resource, "user1", "user"))

        # Other user should not have access
        self.assertFalse(self.manager._check_write_access(resource, "user3", "user"))

        # Admin should always have access
        self.assertTrue(self.manager._check_write_access(resource, "user3", "admin"))

    def test_batch_validation_workflow(self):
        """Test batch operation with validation."""
        items = [
            {"name": "Item 1", "type": "valid"},
            {"name": "Item 2"},  # Missing 'type'
            {"name": "Item 3", "type": "valid"},
        ]

        def validate_and_process(item):
            if not self.manager._validate_required_fields(
                item, ["name", "type"], "Item validation"
            ):
                return None
            return {"id": item["name"], "status": "processed"}

        with self.assertLogs(level="ERROR"):
            results = self.manager._batch_operation(items, validate_and_process)

        # Should have 2 successes and 1 failure
        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 1)


if __name__ == "__main__":
    unittest.main()
