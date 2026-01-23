"""
Base Manager for OpenWebUI Chat Client.
Provides unified dependency injection pattern for all service managers.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

import requests

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class BaseManager:
    """
    Base class for all service managers.

    Provides:
    - Unified dependency injection pattern
    - Standardized pagination and filtering
    - Common HTTP request utilities
    - Access control helpers
    - Batch operation support
    - Data validation utilities
    - Enhanced logging
    """

    # Pagination constants (aligned with Open WebUI official)
    DEFAULT_PAGE_SIZE = 30
    MAX_PAGE_SIZE = 100

    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the base manager.

        Args:
            base_client: The base client instance providing core functionality
        """
        self.base_client = base_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized {self.__class__.__name__}")

    @property
    def session(self):
        """Access to HTTP session from base client."""
        return self.base_client.session

    @property
    def base_url(self) -> str:
        """Access to base URL from base client."""
        return self.base_client.base_url

    @property
    def json_headers(self):
        """Access to JSON headers from base client."""
        return self.base_client.json_headers

    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Optional[Any]:
        """
        Make an HTTP request through the base client.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object or None on failure
        """
        return self.base_client._make_request(method, endpoint, **kwargs)

    def _get_json_response(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request and return JSON response.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments

        Returns:
            Parsed JSON response or None on failure
        """
        response = self._make_request(method, endpoint, **kwargs)
        if not response:
            return None

        try:
            return response.json()
        except (ValueError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return None

    # ==================== Pagination & Filtering ====================

    def _build_pagination_params(
        self,
        page: Optional[int] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, int]:
        """
        Build standardized pagination parameters (aligned with Open WebUI).

        Args:
            page: Page number (1-indexed)
            skip: Number of items to skip
            limit: Maximum items to return
            page_size: Items per page (alternative to limit)

        Returns:
            Dictionary with skip and limit parameters
        """
        params = {}

        # Priority: explicit skip > page-based calculation
        if skip is not None:
            params["skip"] = max(0, skip)
        elif page is not None:
            page = max(1, page)
            page_size = page_size or self.DEFAULT_PAGE_SIZE
            params["skip"] = (page - 1) * page_size

        # Priority: explicit limit > page_size > default
        if limit is not None:
            params["limit"] = min(limit, self.MAX_PAGE_SIZE)
        elif page_size is not None:
            params["limit"] = min(page_size, self.MAX_PAGE_SIZE)
        else:
            params["limit"] = self.DEFAULT_PAGE_SIZE

        return params

    def _build_filter_params(
        self,
        query: Optional[str] = None,
        view_option: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
        **additional_filters: Any,
    ) -> Dict[str, Any]:
        """
        Build filter parameters dictionary (aligned with Open WebUI).

        Args:
            query: Search query string
            view_option: View option filter
            order_by: Field to order by
            direction: Sort direction (asc/desc)
            **additional_filters: Additional filter parameters

        Returns:
            Dictionary of filter parameters
        """
        filter_params = {}

        if query:
            filter_params["query"] = query
        if view_option:
            filter_params["view_option"] = view_option
        if order_by:
            filter_params["order_by"] = order_by
        if direction:
            filter_params["direction"] = direction

        # Add additional filters
        filter_params.update(additional_filters)

        return filter_params

    def _parse_list_response(
        self, response_data: Any
    ) -> Tuple[List[Dict], Optional[int]]:
        """
        Parse list response and extract items and total count.

        Args:
            response_data: Response data from API

        Returns:
            Tuple of (items list, total count)
        """
        if isinstance(response_data, list):
            return response_data, len(response_data)
        elif isinstance(response_data, dict):
            items = response_data.get("data", response_data.get("items", []))
            total = response_data.get("total", len(items))
            return items, total
        return [], None

    # ==================== Access Control ====================

    def _build_access_control(
        self,
        permission_type: str,
        group_ids: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
    ) -> Union[Dict, None]:
        """
        Build access control configuration (aligned with Open WebUI).

        Args:
            permission_type: Type of permission ("public" or structured)
            group_ids: List of group IDs with access
            user_ids: List of user IDs with access

        Returns:
            Access control dict or None for public access
        """
        if permission_type == "public":
            return None

        access_control = {
            "read": {"group_ids": group_ids or [], "user_ids": user_ids or []},
            "write": {"group_ids": group_ids or [], "user_ids": user_ids or []},
        }

        return access_control

    def _check_write_access(
        self, resource: Dict[str, Any], user_id: str, user_role: str = "user"
    ) -> bool:
        """
        Check if user has write access to a resource.

        Args:
            resource: Resource dict with access_control
            user_id: User ID to check
            user_role: User role (admin/user)

        Returns:
            True if user has write access
        """
        # Admin has access to everything
        if user_role == "admin":
            return True

        # Owner has access
        if resource.get("user_id") == user_id:
            return True

        # Check access control
        access_control = resource.get("access_control", {})
        write_control = access_control.get("write", {})

        if user_id in write_control.get("user_ids", []):
            return True

        # TODO: Check group membership
        # if user_group_id in write_control.get("group_ids", []):
        #     return True

        return False

    # ==================== Batch Operations ====================

    def _batch_operation(
        self,
        items: List[Any],
        operation_func: Callable,
        max_workers: int = 3,
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute batch operation using thread pool.

        Args:
            items: List of items to process
            operation_func: Function to apply to each item
            max_workers: Maximum number of worker threads
            continue_on_error: Whether to continue on individual failures

        Returns:
            Dict with 'success' and 'failed' lists
        """
        results = {"success": [], "failed": []}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(operation_func, item): item for item in items
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    if result:
                        results["success"].append(result)
                    else:
                        results["failed"].append(
                            {"item": item, "error": "Operation returned None"}
                        )
                except Exception as e:
                    self.logger.error(f"Batch operation failed for item {item}: {e}")
                    results["failed"].append({"item": item, "error": str(e)})
                    if not continue_on_error:
                        break

        return results

    # ==================== Data Validation ====================

    def _validate_required_fields(
        self, data: Dict[str, Any], required: List[str], context: str
    ) -> bool:
        """
        Validate that required fields are present and not empty.

        Args:
            data: Data dictionary to validate
            required: List of required field names
            context: Context for error messages

        Returns:
            True if all required fields are valid
        """
        missing = [field for field in required if not data.get(field)]
        if missing:
            self.logger.error(
                f"{context}: Missing required fields: {', '.join(missing)}"
            )
            return False
        return True

    def _validate_enum_value(
        self, value: Any, allowed_values: List[Any], field_name: str
    ) -> bool:
        """
        Validate that value is in allowed enum values.

        Args:
            value: Value to validate
            allowed_values: List of allowed values
            field_name: Field name for error messages

        Returns:
            True if value is valid
        """
        if value not in allowed_values:
            self.logger.error(
                f"Invalid {field_name}: '{value}'. Allowed: {allowed_values}"
            )
            return False
        return True

    # ==================== URL Building ====================

    def _build_url(
        self, endpoint: str, path_params: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Build full URL with optional path parameters.

        Args:
            endpoint: API endpoint (may contain {param} placeholders)
            path_params: Dictionary of path parameters to substitute

        Returns:
            Complete URL string
        """
        if path_params:
            for key, value in path_params.items():
                placeholder = f"{{{key}}}"
                if placeholder in endpoint:
                    endpoint = endpoint.replace(
                        placeholder, self._encode_path_param(value)
                    )

        base = self.base_client.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"

    def _encode_path_param(self, param: str) -> str:
        """
        Safely encode URL path parameter.

        Args:
            param: Parameter value to encode

        Returns:
            URL-encoded string
        """
        return quote(str(param), safe="")

    # ==================== Enhanced Logging ====================

    def _log_operation_start(self, operation: str, **context: Any) -> None:
        """
        Log operation start with emoji indicator.

        Args:
            operation: Operation description
            **context: Additional context information
        """
        context_str = self._format_context(context)
        self.logger.info(f"🔄 {operation} {context_str}")

    def _log_operation_success(
        self, operation: str, result: Optional[Any] = None, **context: Any
    ) -> None:
        """
        Log successful operation with emoji indicator.

        Args:
            operation: Operation description
            result: Operation result (optional)
            **context: Additional context information
        """
        context_str = self._format_context(context)
        result_info = f" → {result}" if result else ""
        self.logger.info(f"✅ {operation} {context_str}{result_info}")

    def _log_operation_failure(
        self, operation: str, error: Exception, **context: Any
    ) -> None:
        """
        Log failed operation with emoji indicator.

        Args:
            operation: Operation description
            error: Exception that occurred
            **context: Additional context information
        """
        context_str = self._format_context(context)
        self.logger.error(f"❌ {operation} {context_str}: {error}")

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary for logging.

        Args:
            context: Context information

        Returns:
            Formatted string
        """
        if not context:
            return ""
        return "[" + ", ".join(f"{k}={v}" for k, v in context.items()) + "]"
