"""
Async Model management module for OpenWebUI Chat Client.
"""

import logging
import json
import asyncio
import httpx
from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncModelManager:
    """
    Handles async model-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client
        self.available_model_ids: List[str] = []
        # Note: Async initialization patterns usually require a factory method or separate init call
        # We can't await in __init__. The client calling this should call initialize() if needed.

    async def initialize(self):
        """Perform async initialization (refresh models)."""
        await self._refresh_available_models()

    async def _refresh_available_models(self):
        """Refresh the list of available model IDs."""
        models = await self.list_models()
        if models:
            self.available_model_ids = [model.get('id', '') for model in models if model.get('id')]

    async def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available models."""
        logger.info("Listing all available models for the user...")
        response = await self.base_client._make_request(
            "GET",
            "/api/models?refresh=true"
        )

        if response:
            try:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
            except json.JSONDecodeError:
                # Response is not valid JSON, return None
                logger.warning("Failed to decode JSON response from list_models")
        return None

    async def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all base models."""
        response = await self.base_client._make_request(
            "GET",
            "/api/models/base"
        )
        if response:
            try:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
            except json.JSONDecodeError:
                # Response is not valid JSON, return None
                logger.warning("Failed to decode JSON response from list_base_models")
        return None

    async def list_custom_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists custom models."""
        return await self.base_client._get_json_response(
            "GET",
            "/api/v1/models"
        )

    async def list_groups(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available groups."""
        return await self.base_client._get_json_response(
            "GET",
            "/api/v1/groups/"
        )

    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Fetches details of a specific model."""
        if not model_id:
            return None

        # Try fetch
        response = await self.base_client._make_request(
            "GET",
            "/api/v1/models/model",
            params={"id": model_id}
        )

        if response:
            if response.status_code == 401:
                # Try create if missing in backend
                logger.warning(f"Model '{model_id}' not initialized in backend. creating...")
                created = await self.create_model(model_id=model_id, name=f"{model_id}")
                if not created:
                    return None
                # Retry
                response = await self.base_client._make_request(
                    "GET",
                    "/api/v1/models/model",
                    params={"id": model_id}
                )
                if response and response.status_code == 200:
                    return response.json()
            elif response.status_code == 200:
                return response.json()

        return None

    async def create_model(
        self,
        model_id: str,
        name: str,
        base_model_id: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        permission_type: str = "public",
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        profile_image_url: str = "/static/favicon.png",
        suggestion_prompts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        capabilities: Optional[Dict[str, bool]] = None,
        is_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Creates a new model configuration."""
        access_control = await self._build_access_control(
            permission_type, group_identifiers, user_ids
        )
        if access_control is False:
            return None

        model_data = {
            "meta": {
                "profile_image_url": profile_image_url,
                "description": description,
                "suggestion_prompts": suggestion_prompts,
                "tags": tags or [],
                "capabilities": capabilities or {},
            },
            "id": model_id,
            "name": name,
            "base_model_id": base_model_id,
            "params": params or {},
            "access_control": access_control,
            "is_active": is_active,
        }

        if permission_type == "public":
            model_data["access_control"] = None

        response = await self.base_client._make_request(
            "POST",
            "/api/v1/models/create",
            json_data=model_data
        )

        if response:
            await self._refresh_available_models()
            return response.json()
        return None

    async def update_model(
        self,
        model_id: str,
        name: Optional[str] = None,
        base_model_id: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        permission_type: Optional[str] = None,
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        profile_image_url: Optional[str] = None,
        suggestion_prompts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        capabilities: Optional[Dict[str, bool]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing model."""
        current_model = await self.get_model(model_id)
        if not current_model:
            return None

        update_data = current_model.copy()

        if name is not None: update_data['name'] = name
        if base_model_id is not None: update_data['base_model_id'] = base_model_id
        if is_active is not None: update_data['is_active'] = is_active
        if params is not None: update_data['params'] = params

        meta_update = {}
        if description is not None: meta_update['description'] = description
        if profile_image_url is not None: meta_update['profile_image_url'] = profile_image_url
        if suggestion_prompts is not None: meta_update['suggestion_prompts'] = suggestion_prompts
        if tags is not None: meta_update['tags'] = [{"name": tag} for tag in tags]
        if capabilities is not None: meta_update['capabilities'] = capabilities

        if meta_update:
            update_data['meta'] = {**current_model.get('meta', {}), **meta_update}

        if permission_type is not None:
            access_control = await self._build_access_control(
                permission_type, group_identifiers, user_ids
            )
            if access_control is False:
                return None
            update_data["access_control"] = access_control

        response = await self.base_client._make_request(
            "POST",
            "/api/v1/models/model/update",
            params={"id": model_id},
            json_data=update_data
        )

        if response:
            return response.json()
        return None

    async def delete_model(self, model_id: str) -> bool:
        """Deletes a model."""
        response = await self.base_client._make_request(
            "DELETE",
            "/api/v1/models/model/delete",
            params={"id": model_id}
        )
        if not response:
            return False

        if response.status_code == 405:
            logger.warning("DELETE not allowed, retrying with POST fallback.")
            response = await self.base_client._make_request(
                "POST",
                "/api/v1/models/model/delete",
                params={"id": model_id}
            )
            if not response:
                return False
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"Failed to delete model '{model_id}': {exc}")
            return False
        except Exception as exc:
            logger.error(
                f"Unexpected error deleting model '{model_id}': {type(exc).__name__}: {exc}"
            )
            return False
        logger.info(f"Successfully deleted model '{model_id}'.")
        await self._refresh_available_models()
        return True

    async def batch_update_model_permissions(
        self,
        models: List[Dict[str, Any]],
        permission_type: str = "public",
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Updates permissions for multiple models in parallel."""
        async def update_single(model):
            model_id = model.get("id")
            if not model_id:
                return None, False
            result = await self.update_model(
                model_id,
                permission_type=permission_type,
                group_identifiers=group_identifiers,
                user_ids=user_ids
            )
            return model_id, (result is not None)

        tasks = [update_single(m) for m in models]
        results_list = await asyncio.gather(*tasks)

        results = {}
        for model_id, success in results_list:
            if model_id:
                results[model_id] = {"success": success}
        return results

    async def _build_access_control(
        self, permission_type: str, group_identifiers: Optional[List[str]], user_ids: Optional[List[str]]
    ) -> Union[Dict[str, Any], None, bool]:
        if permission_type == "public":
            return None

        if permission_type == "private":
            return {
                "read": {"group_ids": [], "user_ids": user_ids or []},
                "write": {"group_ids": [], "user_ids": user_ids or []}
            }

        if permission_type == "group":
            if not group_identifiers:
                return False
            group_ids = await self._resolve_group_ids(group_identifiers)
            if group_ids is False:
                return False
            return {
                "read": {"group_ids": group_ids, "user_ids": user_ids or []},
                "write": {"group_ids": group_ids, "user_ids": user_ids or []}
            }
        return False

    async def _resolve_group_ids(self, group_identifiers: List[str]) -> Union[List[str], bool]:
        groups = await self.list_groups()
        if not groups:
            return False

        name_to_id = {group.get("name", ""): group.get("id", "") for group in groups}
        id_to_name = {group.get("id", ""): group.get("name", "") for group in groups}

        resolved_ids = []
        for identifier in group_identifiers:
            if identifier in id_to_name:
                resolved_ids.append(identifier)
            elif identifier in name_to_id:
                resolved_ids.append(name_to_id[identifier])
            else:
                return False
        return resolved_ids
