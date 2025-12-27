"""
Model management module for OpenWebUI Chat Client.
Handles all model-related operations including CRUD operations and permissions.
"""

import json
import logging
import requests
import time
from typing import Optional, List, Dict, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Handles all model-related operations for the OpenWebUI client.
    
    This class manages:
    - Model listing and retrieval
    - Model creation and updates
    - Model deletion
    - Model permissions and access control
    - Group management for model permissions
    """
    
    def __init__(self, base_client, skip_initial_refresh: bool = False):
        """
        Initialize the model manager.
        
        Args:
            base_client: The base client instance for making API requests
            skip_initial_refresh: If True, skip the initial refresh of available models (useful for testing)
        """
        self.base_client = base_client
        self.available_model_ids: List[str] = []
        if not skip_initial_refresh:
            self._refresh_available_models()
    
    def _refresh_available_models(self):
        """Refresh the list of available model IDs."""
        models = self.list_models()
        if models:
            self.available_model_ids = [model.get('id', '') for model in models if model.get('id')]
    
    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all available models for the user, including base models and user-created custom models. Excludes disabled base models. This corresponds to the model list shown in the top left of the chat page.
        """
        logger.info("Listing all available models for the user...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/models?refresh=true", 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            data = response.json()
            if (
                not isinstance(data, dict)
                or "data" not in data
                or not isinstance(data["data"], list)
            ):
                logger.error(
                    f"API response for all models did not contain expected 'data' key or was not a list. Response: {data}"
                )
                return None
            models = data["data"]
            logger.info(f"Successfully listed {len(models)} models.")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list all models. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when listing all models. Invalid JSON received."
            )
            return None

    def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all base models that can be used to create variants. Includes disabled base models.
        Corresponds to the model list in the admin settings page, including PIPE type models.
        """
        logger.info("Listing all  base models...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/models/base", 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            data = response.json()
            if (
                not isinstance(data, dict)
                or "data" not in data
                or not isinstance(data["data"], list)
            ):
                logger.error(
                    f"API response for base models did not contain expected 'data' key or was not a list. Response: {data}"
                )
                return None
            models = data["data"]
            logger.info(f"Successfully listed {len(models)} base models.")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list base models. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when listing base models. Invalid JSON received."
            )
            return None

    def list_custom_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists custom models that users can use or have created (not base models).
        A list of custom models available in the user's workspace, or None if the request fails.
        """
        logger.info("Listing all custom models...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/models", 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.error(
                    f"API response for custom models is not a list. Response: {data}"
                )
                return None
            logger.info(f"Successfully listed {len(data)} custom models.")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list custom models. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when listing custom models. Invalid JSON received."
            )
            return None

    def list_groups(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all available groups from the Open WebUI instance.
        
        Returns:
            A list of group dictionaries containing id, name, and other metadata,
            or None if the request fails.
        """
        logger.info("Listing all available groups...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/groups/", 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.error(
                    f"API response for groups did not contain expected list. Response: {data}"
                )
                return None
            logger.info(f"Successfully listed {len(data)} groups.")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list groups. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when listing groups. Invalid JSON received."
            )
            return None

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the details of a specific model by its ID.
        If the model ID is not found in the locally available models, it returns None.
        If the model ID is available locally but the API returns a 401 error (indicating the model is not initialized/saved on the backend),
        it will attempt to create the model and then retry fetching its details.

        Args:
            model_id: The ID of the model to fetch (e.g., 'gpt-4.1').

        Returns:
            A dictionary containing the model details, or None if not found or creation fails.
        """
        logger.info(f"Fetching details for model '{model_id}'...")
        if not model_id:
            logger.error("Model ID cannot be empty.")
            return None
        if model_id not in self.available_model_ids:
            logger.warning(
                f"Model '{model_id}' is not available in the locally cached model list. Refreshing and retrying..."
            )
            self._refresh_available_models()
            if model_id not in self.available_model_ids:
                logger.error(
                    f"Model '{model_id}' is still not found after refreshing the available models list."
                )
                return None

        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/models/model",
                params={"id": model_id},
                headers=self.base_client.json_headers
            )
            if response.status_code == 401:
                # Model exists locally but not initialized in backend, try to create it
                logger.warning(
                    f"Model '{model_id}' exists locally but is not initialized in the backend. Attempting to create it..."
                )
                created_model = self.create_model(
                    model_id=model_id,
                    name=f"{model_id}",
                )
                if not created_model:
                    logger.error(
                        f"Failed to auto-create model '{model_id}'. Cannot proceed."
                    )
                    return None
                # Retry fetching the model details
                logger.info(f"Retrying to fetch details for model '{model_id}'...")
                response = self.base_client.session.get(
                    f"{self.base_client.base_url}/api/v1/models/model",
                    params={"id": model_id},
                    headers=self.base_client.json_headers
                )
            response.raise_for_status()
            model_data = response.json()
            logger.info(f"Successfully fetched details for model '{model_id}'.")
            return model_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch model '{model_id}'. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when fetching model '{model_id}'. Invalid JSON received."
            )
            return None

    def create_model(
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
        """
        Creates a new model configuration with detailed metadata.

        Args:
            model_id: Unique identifier for the new model (e.g., 'my-gpt-4.1')
            name: Display name for the model
            base_model_id: ID of the base model to use. Can be None.
            description: Description for the model's meta object.
            params: Additional parameters for model configuration.
            permission_type: "public", "private", or "group".
            group_identifiers: List of group IDs or names for group permission.
            user_ids: List of user IDs for private/group permission.
            profile_image_url: URL for the model's profile image.
            suggestion_prompts: List of suggestion prompts.
            tags: List of tags.
            capabilities: Dictionary of model capabilities (e.g., {"vision": True}).
            is_active: Whether the model is active.

        Returns:
            The created model data, or None if creation fails.
        """
        logger.info(f"Creating model '{model_id}'...")

        if not model_id or not name:
            logger.error("Model ID and name are required.")
            return None

        # Build access control
        access_control = self._build_access_control(
            permission_type, group_identifiers, user_ids
        )
        if access_control is False:
            return None

        # Build the full model data payload, matching the curl command structure
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

        # The API expects `access_control: null` for public, not the absence of the key
        if permission_type == "public":
            model_data["access_control"] = None

        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/models/create",
                json=model_data, 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            created_model = response.json()
            logger.info(f"Successfully created model '{model_id}'.")
            self._refresh_available_models()
            return created_model
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create model '{model_id}'. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when creating model '{model_id}'. Invalid JSON received."
            )
            return None

    def update_model(
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
        """
        Updates an existing model configuration with detailed metadata.

        Args:
            model_id: ID of the model to update.
            ... (and all other optional parameters similar to create_model)

        Returns:
            The updated model data, or None if update fails.
        """
        logger.info(f"Updating model '{model_id}'...")

        if not model_id:
            logger.error("Model ID is required.")
            return None

        # Get current model data to use as a base
        current_model = self.get_model(model_id)
        if not current_model:
            logger.error(f"Model '{model_id}' not found. Cannot update.")
            return None

        # Build update payload by layering changes over the current state
        update_data = current_model.copy()

        # Update top-level fields
        if name is not None: update_data['name'] = name
        if base_model_id is not None: update_data['base_model_id'] = base_model_id
        if is_active is not None: update_data['is_active'] = is_active
        if params is not None: update_data['params'] = params

        # Update meta fields, merging with existing meta
        meta_update = {}
        if description is not None: meta_update['description'] = description
        if profile_image_url is not None: meta_update['profile_image_url'] = profile_image_url
        if suggestion_prompts is not None: meta_update['suggestion_prompts'] = suggestion_prompts
        if tags is not None: 
            # [{"name": "tag1"}, {"name": "tag2"}] -> ["tag1", "tag2"]
            meta_update['tags'] = [{"name": tag} for tag in tags]
        if capabilities is not None: meta_update['capabilities'] = capabilities

        if meta_update:
            update_data['meta'] = {**current_model.get('meta', {}), **meta_update}

        # Handle permission updates only if permission_type is explicitly provided
        if permission_type is not None:
            access_control = self._build_access_control(
                permission_type, group_identifiers, user_ids
            )
            if access_control is False:
                return None
            update_data["access_control"] = access_control
        # If permission_type is None, we do nothing and the existing access_control from current_model is preserved.

        try:
            # The endpoint for updating is different from creating
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/models/model/update",
                params={"id": model_id},
                json=update_data,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            updated_model = response.json()
            logger.info(f"Successfully updated model '{model_id}'.")
            return updated_model
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update model '{model_id}'. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON response when updating model '{model_id}'. Invalid JSON received."
            )
            return None

    def delete_model(self, model_id: str) -> bool:
        """
        Deletes a model configuration.

        Args:
            model_id: ID of the model to delete

        Returns:
            True if the model was successfully deleted, False otherwise.
        """
        logger.info(f"Deleting model '{model_id}'...")

        if not model_id:
            logger.error("Model ID cannot be empty.")
            return False

        try:
            response = self.base_client.session.delete(
                f"{self.base_client.base_url}/api/v1/models/model/delete",
                params={"id": model_id},
                headers=self.base_client.json_headers
            )
            if response.status_code == 405:
                logger.warning("DELETE not allowed, retrying with POST fallback.")
                response = self.base_client.session.post(
                    f"{self.base_client.base_url}/api/v1/models/model/delete",
                    params={"id": model_id},
                    headers=self.base_client.json_headers
                )
                if response.status_code >= 400:
                    logger.error(
                        f"POST fallback failed to delete model '{model_id}' "
                        f"with status {response.status_code}"
                    )
            response.raise_for_status()
            logger.info(f"Successfully deleted model '{model_id}'.")
            self._refresh_available_models()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete model '{model_id}'. Request error: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False

    def batch_update_model_permissions(
        self,
        models: List[Dict[str, Any]],
        permission_type: str = "public",
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        max_workers: int = 5,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Updates permissions for multiple models in parallel.

        Args:
            models: List of model dictionaries (each must have 'id' field)
            permission_type: "public", "private", or "group"
            group_identifiers: List of group IDs or names (for group permission)
            user_ids: List of user IDs (for private/group permission)
            max_workers: Maximum number of parallel workers

        Returns:
            Dictionary mapping model IDs to results:
            {"model_id": {"success": bool, "data": model_data_or_error_msg}}
        """
        if not models:
            logger.warning("No models provided for batch update.")
            return {}

        logger.info(
            f"Starting batch permission update for {len(models)} models with permission_type='{permission_type}'"
        )

        def update_single_model(model: Dict[str, Any]) -> Tuple[str, bool, str]:
            """Update a single model's permissions."""
            model_id = model.get("id")
            if not model_id:
                return "", False, "Model ID not found in model data"

            try:
                updated_model = self.update_model(
                    model_id=model_id,
                    permission_type=permission_type,
                    group_identifiers=group_identifiers,
                    user_ids=user_ids,
                )
                if updated_model:
                    return model_id, True, updated_model
                else:
                    return model_id, False, f"Failed to update model '{model_id}'"
            except Exception as e:
                return model_id, False, f"Exception updating model '{model_id}': {str(e)}"

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_model = {
                executor.submit(update_single_model, model): model 
                for model in models
            }

            # Collect results
            completed = 0
            for future in as_completed(future_to_model):
                completed += 1
                try:
                    model_id, success, data = future.result()
                    if model_id:  # Only add if we got a valid model ID
                        results[model_id] = {"success": success, "data": data}
                        status = "✅" if success else "❌"
                        logger.info(
                            f"{status} Model {completed}/{len(models)}: {model_id}"
                        )
                except Exception as e:
                    logger.error(f"Exception in batch update task: {e}")

        # Summary
        successful = sum(1 for r in results.values() if r["success"])
        failed = len(results) - successful
        logger.info(
            f"Batch permission update completed: {successful} successful, {failed} failed"
        )

        return results

    def _build_access_control(
        self,
        permission_type: str,
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
    ) -> Union[Dict[str, Any], None, bool]:
        """
        Build access control configuration based on permission type.
        
        Args:
            permission_type: "public", "private", or "group"
            group_identifiers: List of group IDs or names
            user_ids: List of user IDs
            
        Returns:
            Access control dict, None for public, or False for error
        """
        if permission_type == "public":
            return None
        
        if permission_type == "private":
            return {
                "read": {"group_ids": [], "user_ids": user_ids or []},
                "write": {"group_ids": [], "user_ids": user_ids or []}
            }
        
        if permission_type == "group":
            if not group_identifiers:
                logger.error("Group identifiers required for group permission type.")
                return False
            
            # Resolve group names to IDs if needed
            group_ids = self._resolve_group_ids(group_identifiers)
            if group_ids is False:
                return False
            
            return {
                "read": {"group_ids": group_ids, "user_ids": user_ids or []},
                "write": {"group_ids": group_ids, "user_ids": user_ids or []}
            }
        
        logger.error(f"Invalid permission type: {permission_type}")
        return False
    
    def _resolve_group_ids(self, group_identifiers: List[str]) -> Union[List[str], bool]:
        """
        Resolve group names to group IDs.
        
        Args:
            group_identifiers: List of group IDs or group names
            
        Returns:
            List of group IDs, or False if resolution fails
        """
        groups = self.list_groups()
        if not groups:
            logger.error("Failed to fetch groups for ID resolution.")
            return False
        
        # Create mapping of names to IDs
        name_to_id = {group.get("name", ""): group.get("id", "") for group in groups}
        id_to_name = {group.get("id", ""): group.get("name", "") for group in groups}
        
        resolved_ids = []
        for identifier in group_identifiers:
            if identifier in id_to_name:
                # It's already an ID
                resolved_ids.append(identifier)
            elif identifier in name_to_id:
                # It's a name, resolve to ID
                resolved_ids.append(name_to_id[identifier])
            else:
                logger.error(f"Group '{identifier}' not found.")
                return False
        
        return resolved_ids
