"""
Asynchronous model management module for OpenWebUI Chat Client.
Handles all model-related operations including CRUD and permissions using httpx.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union, Tuple

logger = logging.getLogger(__name__)


class AsyncModelManager:
    """
    Handles all asynchronous model-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        """
        Initialize the async model manager.

        Args:
            base_client: The async base client instance for making API requests.
        """
        self.base_client = base_client
        self.available_model_ids: List[str] = []

    async def refresh_available_models(self):
        """Asynchronously refresh the list of available model IDs."""
        models = await self.list_models()
        if models:
            self.available_model_ids = [model.get('id', '') for model in models if model.get('id')]
            self.base_client.available_model_ids = self.available_model_ids

    async def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously lists all available models for the user."""
        logger.info("Async listing all available models...")
        response = await self.base_client._get_json_response("GET", "/api/models")
        if response and isinstance(response, dict) and "data" in response:
            logger.info(f"Successfully listed {len(response['data'])} models.")
            return response["data"]
        logger.error(f"API response for all models did not contain 'data' key. Response: {response}")
        return None

    async def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously lists all available base models."""
        logger.info("Async listing all available base models...")
        response = await self.base_client._get_json_response("GET", "/api/models/base")
        if response and isinstance(response, dict) and "data" in response:
            logger.info(f"Successfully listed {len(response['data'])} base models.")
            return response["data"]
        logger.error(f"API response for base models did not contain 'data' key. Response: {response}")
        return None

    async def list_groups(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously lists all available groups."""
        logger.info("Async listing all available groups...")
        response = await self.base_client._get_json_response("GET", "/api/v1/groups/")
        if response and isinstance(response, list):
            logger.info(f"Successfully listed {len(response)} groups.")
            return response
        logger.error(f"API response for groups was not a list. Response: {response}")
        return None

    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Asynchronously fetches the details of a specific model by its ID."""
        logger.info(f"Async fetching details for model '{model_id}'...")
        if model_id not in self.available_model_ids:
            await self.refresh_available_models()
            if model_id not in self.available_model_ids:
                logger.error(f"Model '{model_id}' not found after refreshing list.")
                return None

        response = await self.base_client._get_json_response("GET", "/api/v1/models/model", params={"id": model_id})

        if response is None: # This could happen on 401
             logger.warning(
                f"Model '{model_id}' might not be initialized in the backend. Attempting to create it..."
            )
             created_model = await self.create_model(
                model_id=model_id,
                base_model_id=model_id,
                name=f"Auto-created model for {model_id}",
             )
             if not created_model:
                 logger.error(f"Failed to auto-create model '{model_id}'.")
                 return None
             return await self.base_client._get_json_response("GET", "/api/v1/models/model", params={"id": model_id})

        logger.info(f"Successfully fetched details for model '{model_id}'.")
        return response

    async def create_model(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Asynchronously creates a new model configuration."""
        model_id = kwargs.get("model_id")
        logger.info(f"Async creating model '{model_id}'...")

        # Simplified for brevity, will need full payload construction
        model_data = {
            "id": model_id,
            "name": kwargs.get("name"),
            "base_model_id": kwargs.get("base_model_id"),
            "meta": {},
            "params": {},
            "access_control": None,
            "is_active": True
        }

        response = await self.base_client._get_json_response(
            "POST", "/api/v1/models/create", json_data=model_data
        )
        if response:
            logger.info(f"Successfully created model '{model_id}'.")
            await self.refresh_available_models()
        return response

    async def delete_model(self, model_id: str) -> bool:
        """Asynchronously deletes a model configuration."""
        logger.info(f"Async deleting model '{model_id}'...")
        response = await self.base_client._make_request(
            "DELETE", "/api/v1/models/model/delete", params={"id": model_id}
        )
        if response and response.status_code == 200:
            logger.info(f"Successfully deleted model '{model_id}'.")
            await self.refresh_available_models()
            return True
        return False
