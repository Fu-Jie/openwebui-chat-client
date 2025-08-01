"""
OpenWebUI Chat Client - Refactored modular version.

An intelligent, stateful Python client for the Open WebUI API.
Supports single/multi-model chats, tagging, and RAG with both
direct file uploads and knowledge base collections, matching the backend format.
"""

import logging
from typing import Optional, List, Dict, Any, Union, Generator, Tuple

# Import required modules for backward compatibility with tests
import requests
import json
import uuid
import time
import base64
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .core.base_client import BaseClient
from .modules.model_manager import ModelManager
from .modules.notes_manager import NotesManager
from .modules.knowledge_base_manager import KnowledgeBaseManager
from .modules.file_manager import FileManager
from .modules.chat_manager import ChatManager

logger = logging.getLogger(__name__)


class OpenWebUIClient:
    """
    An intelligent, stateful Python client for the Open WebUI API.
    Supports single/multi-model chats, tagging, and RAG with both
    direct file uploads and knowledge base collections, matching the backend format.
    
    This refactored version uses a modular architecture with specialized managers
    while maintaining 100% backward compatibility with the original API.
    """

    def __init__(self, base_url: str, token: str, default_model_id: str, skip_model_refresh: bool = False):
        """
        Initialize the OpenWebUI client with modular architecture.
        
        Args:
            base_url: The base URL of the OpenWebUI instance
            token: Authentication token
            default_model_id: Default model identifier to use
            skip_model_refresh: If True, skip initial model refresh (useful for testing)
        """
        # Initialize base client
        self._base_client = BaseClient(base_url, token, default_model_id)
        
        # Initialize specialized managers
        self._model_manager = ModelManager(self._base_client, skip_initial_refresh=skip_model_refresh)
        self._notes_manager = NotesManager(self._base_client)
        self._knowledge_base_manager = KnowledgeBaseManager(self._base_client)
        self._file_manager = FileManager(self._base_client)
        self._chat_manager = ChatManager(self._base_client)
        
        # Set up available model IDs from model manager
        self._base_client.available_model_ids = self._model_manager.available_model_ids
        
        # For backward compatibility, expose base client properties
        self.base_url = self._base_client.base_url
        self.default_model_id = self._base_client.default_model_id
        self.session = self._base_client.session
        self.json_headers = self._base_client.json_headers
        self.chat_id = self._base_client.chat_id
        self.chat_object_from_server = self._base_client.chat_object_from_server
        self.model_id = self._base_client.model_id
        self.task_model = self._base_client.task_model
        self._auto_cleanup_enabled = self._base_client._auto_cleanup_enabled
        self._first_stream_request = self._base_client._first_stream_request

    @property
    def available_model_ids(self):
        """Get available model IDs."""
        return self._model_manager.available_model_ids
    
    @available_model_ids.setter
    def available_model_ids(self, value):
        """Set available model IDs and sync with model manager."""
        self._model_manager.available_model_ids = value
        self._base_client.available_model_ids = value

    def __del__(self):
        """
        Destructor: Automatically cleans up placeholder messages and syncs with remote server when instance is destroyed
        """
        if self._auto_cleanup_enabled and self.chat_id and self.chat_object_from_server:
            try:
                logger.info(
                    "🧹 Client cleanup: Removing unused placeholder messages..."
                )
                cleaned_count = self._cleanup_unused_placeholder_messages()
                if cleaned_count > 0:
                    logger.info(
                        f"🧹 Client cleanup: Cleaned {cleaned_count} placeholder message pairs before exit."
                    )
                else:
                    logger.info("🧹 Client cleanup: No placeholder messages to clean.")
            except Exception as e:
                logger.warning(
                    f"🧹 Client cleanup: Error during automatic cleanup: {e}"
                )

    # =============================================================================
    # CHAT OPERATIONS - Delegate to ChatManager
    # =============================================================================

    def chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Send a chat message with a single model."""
        return self._chat_manager.chat(
            question, chat_title, model_id, folder_name, image_paths,
            tags, rag_files, rag_collections, tool_ids,
            enable_follow_up, enable_auto_tagging, enable_auto_titling
        )

    def parallel_chat(
        self,
        question: str,
        chat_title: str,
        model_ids: List[str],
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Send a chat message to multiple models in parallel."""
        return self._chat_manager.parallel_chat(
            question, chat_title, model_ids, folder_name, image_paths,
            tags, rag_files, rag_collections, tool_ids,
            enable_follow_up, enable_auto_tagging, enable_auto_titling
        )

    def stream_chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Generator[str, None, None]:
        """Stream a chat response in real-time."""
        return self._chat_manager.stream_chat(
            question, chat_title, model_id, folder_name, image_paths,
            tags, rag_files, rag_collections, tool_ids,
            enable_follow_up, enable_auto_tagging, enable_auto_titling
        )

    def set_chat_tags(self, chat_id: str, tags: List[str]):
        """Set tags for a chat conversation."""
        return self._chat_manager.set_chat_tags(chat_id, tags)

    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """Rename an existing chat."""
        return self._chat_manager.rename_chat(chat_id, new_title)

    def update_chat_metadata(
        self,
        chat_id: str,
        regenerate_tags: bool = False,
        regenerate_title: bool = False,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Regenerates and updates the tags and/or title for an existing chat based on its history.

        Args:
            chat_id: The ID of the chat to update.
            regenerate_tags: If True, new tags will be generated and applied.
            regenerate_title: If True, a new title will be generated and applied.
            title: Direct title to set (alternative to regenerate_title)
            tags: Direct tags to set (alternative to regenerate_tags)
            folder_name: Folder to move chat to

        Returns:
            A dictionary containing the 'suggested_tags' and/or 'suggested_title' that were updated,
            or None if the chat could not be found or no action was requested.
        """
        if not regenerate_tags and not regenerate_title and title is None and tags is None and folder_name is None:
            logger.warning("No action requested for update_chat_metadata. Set regenerate_tags or regenerate_title to True, or provide title/tags/folder_name.")
            return None

        logger.info(f"Updating metadata for chat {chat_id[:8]}...")
        
        # For backward compatibility with the regenerate_ parameters, we need to implement the original behavior
        if regenerate_tags or regenerate_title:
            if not self._load_chat_details(chat_id):
                logger.error(f"Cannot update metadata, failed to load chat: {chat_id}")
                return None

            api_messages = self._build_linear_history_for_api(self.chat_object_from_server["chat"])
            return_data = {}

            if regenerate_tags:
                logger.info("Regenerating tags...")
                suggested_tags = self._get_tags(api_messages)
                if suggested_tags:
                    self.set_chat_tags(chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags
                    logger.info(f"  > Applied new tags: {suggested_tags}")
                else:
                    logger.warning("No tags were generated.")

            if regenerate_title:
                logger.info("Regenerating title...")
                suggested_title = self._get_title(api_messages)
                if suggested_title:
                    self.rename_chat(chat_id, suggested_title)
                    return_data["suggested_title"] = suggested_title
                    logger.info(f"  > Applied new title: '{suggested_title}'")
                else:
                    logger.warning("No title was generated.")

            return return_data if return_data else None
        else:
            # Use the new delegation to chat manager for direct values
            success = self._chat_manager.update_chat_metadata(chat_id, title, tags, folder_name)
            return {"updated": success} if success else None

    def switch_chat_model(self, chat_id: str, model_ids: Union[str, List[str]]) -> bool:
        """Switch the model(s) for an existing chat."""
        return self._chat_manager.switch_chat_model(chat_id, model_ids)

    def list_chats(self, page: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """List all chats for the current user."""
        return self._chat_manager.list_chats(page)

    def get_chats_by_folder(self, folder_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all chats in a specific folder."""
        return self._chat_manager.get_chats_by_folder(folder_id)

    def archive_chat(self, chat_id: str) -> bool:
        """Archive a chat conversation."""
        return self._chat_manager.archive_chat(chat_id)

    def create_folder(self, name: str) -> Optional[str]:
        """Create a new folder for organizing chats."""
        # Create the folder using the chat manager
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/folders/",
                json={"name": name},
                headers=self.json_headers,
            )
            response.raise_for_status()
            logger.info(f"Successfully sent request to create folder '{name}'.")
            # Now get the folder ID to return it, matching original behavior
            return self.get_folder_id_by_name(name)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    def get_folder_id_by_name(self, folder_name: str) -> Optional[str]:
        """Get folder ID by folder name."""
        return self._chat_manager.get_folder_id_by_name(folder_name)

    def move_chat_to_folder(self, chat_id: str, folder_id: str):
        """Move a chat to a specific folder."""
        return self._chat_manager.move_chat_to_folder(chat_id, folder_id)

    # =============================================================================
    # MODEL MANAGEMENT - Delegate to ModelManager
    # =============================================================================

    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available models for the user."""
        return self._model_manager.list_models()

    def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available base models that can be used to create variants."""
        return self._model_manager.list_base_models()

    def list_custom_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists custom models that can be created by users."""
        return self._model_manager.list_custom_models()

    def list_groups(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available groups from the Open WebUI instance."""
        return self._model_manager.list_groups()

    def _build_access_control(
        self, 
        permission_type: str, 
        group_identifiers: Optional[List[str]] = None, 
        user_ids: Optional[List[str]] = None
    ) -> Union[Dict[str, Any], None, bool]:
        """Build access control structure for model permissions."""
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
        """Resolve group names/identifiers to group IDs."""
        groups = self.list_groups()
        if not groups:
            logger.error("Failed to fetch groups for ID resolution.")
            return False
        
        # Create mapping of both names and IDs to IDs
        id_map = {}
        for group in groups:
            group_id = group.get("id")
            group_name = group.get("name")
            if group_id:
                id_map[group_id] = group_id  # ID to ID mapping
                if group_name:
                    id_map[group_name] = group_id  # Name to ID mapping
        
        resolved_ids = []
        for identifier in group_identifiers:
            if identifier in id_map:
                resolved_ids.append(id_map[identifier])
            else:
                logger.error(f"Group identifier '{identifier}' not found.")
                return False
        
        return resolved_ids

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Fetches the details of a specific model by its ID."""
        return self._model_manager.get_model(model_id)

    def create_model(
        self,
        model_id: str,
        name: Optional[str] = None,
        base_model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        stream_response: bool = True,
        other_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        profile_image_url: str = "/static/favicon.png",
        capabilities: Optional[Dict[str, bool]] = None,
        suggestion_prompts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        # New modular parameters for backward compatibility
        params: Optional[Dict[str, Any]] = None,
        permission_type: str = "public",
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a new model configuration - delegates to ModelManager.
        Maintains backward compatibility with original signature.
        """
        # Ensure we have required fields
        if not name or not base_model_id:
            raise ValueError("name and base_model_id are required parameters")
        
        # Build params dict from individual parameters if provided
        if params is None:
            params = {}
        
        if system_prompt is not None:
            params["system_prompt"] = system_prompt
        if temperature is not None:
            params["temperature"] = temperature
        if stream_response is not None:
            params["stream_response"] = stream_response
        if other_params:
            params.update(other_params)
        if profile_image_url != "/static/favicon.png":
            params["profile_image_url"] = profile_image_url
        if capabilities is not None:
            params["capabilities"] = capabilities
        if suggestion_prompts is not None:
            params["suggestion_prompts"] = suggestion_prompts
        if tags is not None:
            params["tags"] = tags
        if is_active is not None:
            params["is_active"] = is_active
            
        return self._model_manager.create_model(
            model_id=model_id,
            base_model_id=base_model_id,
            name=name,
            description=description or "",
            params=params,
            permission_type=permission_type,
            group_identifiers=group_identifiers,
            user_ids=user_ids,
        )

    def update_model(
        self,
        model_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        permission_type: Optional[str] = None,
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        access_control: Optional[Dict[str, Any]] = ...,
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing model configuration."""
        # If access_control is provided directly (including None), or if we need to handle
        # special cases for backward compatibility, handle it specially
        if access_control is not ... or any(param is not None for param in [name, description, params]):
            # Get current model data
            current_model = self.get_model(model_id)
            if not current_model:
                logger.error(f"Model '{model_id}' not found. Cannot update.")
                return None

            # Build update data with only provided fields
            update_data = {"id": model_id}
            
            if name is not None:
                update_data["name"] = name
            else:
                update_data["name"] = current_model.get("name", "")
                
            if description is not None:
                update_data["description"] = description
            else:
                update_data["description"] = current_model.get("description", "")
                
            if params is not None:
                update_data["params"] = params
            else:
                update_data["params"] = current_model.get("params", {})
                
            # Handle metadata
            update_data["meta"] = current_model.get("meta", {"capabilities": {}})
            
            # Handle access_control
            if access_control is not ...:
                # access_control was explicitly provided (including None)
                update_data["access_control"] = access_control
            else:
                # access_control was not provided, preserve existing
                update_data["access_control"] = current_model.get("access_control")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/models/model/update", 
                    params={"id": model_id},
                    json=update_data, 
                    headers=self.json_headers
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
        else:
            # Use the normal model manager path only if no parameters are provided
            return self._model_manager.update_model(
                model_id, name, description, params,
                permission_type, group_identifiers, user_ids
            )

    def delete_model(self, model_id: str) -> bool:
        """Deletes a model configuration."""
        return self._model_manager.delete_model(model_id)

    def batch_update_model_permissions(
        self,
        models: Optional[List[Dict[str, Any]]] = None,
        permission_type: str = "public",
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        max_workers: int = 5,
        model_identifiers: Optional[List[str]] = None,
        model_keyword: Optional[str] = None,
    ) -> Dict[str, List[Any]]:
        """Updates permissions for multiple models in parallel."""
        logger.info("Starting batch model permission update...")
        
        # Validate permission type
        if permission_type not in ["public", "private", "group"]:
            logger.error(f"Invalid permission_type '{permission_type}'. Must be 'public', 'private', or 'group'.")
            return {"success": [], "failed": [], "skipped": []}
        
        # Handle backward compatibility - if model_identifiers or model_keyword provided
        if model_identifiers is not None or model_keyword is not None:
            models_to_update = []
            
            if model_identifiers:
                # Use specific model IDs
                for model_id in model_identifiers:
                    model = self.get_model(model_id)
                    if model:
                        models_to_update.append(model)
                    else:
                        logger.warning(f"Model '{model_id}' not found, skipping.")
            elif model_keyword:
                # Filter by keyword
                all_models = self.list_models()
                if not all_models:
                    logger.error("Failed to retrieve models list.")
                    return {"success": [], "failed": [], "skipped": []}
                
                models_to_update = [
                    model for model in all_models 
                    if model_keyword.lower() in model.get("id", "").lower()
                    or model_keyword.lower() in model.get("name", "").lower()
                ]
                logger.info(f"Found {len(models_to_update)} models matching keyword '{model_keyword}'")
        else:
            # Original signature with models parameter
            if models is None:
                logger.error("Either models, model_identifiers, or model_keyword must be provided")
                return {"success": [], "failed": [], "skipped": []}
            models_to_update = models
        
        if not models_to_update:
            logger.warning("No models found to update.")
            return {"success": [], "failed": [], "skipped": []}
        
        # Prepare access control configuration
        access_control = self._build_access_control(permission_type, group_identifiers, user_ids)
        if access_control is False:  # Error occurred
            return {"success": [], "failed": [], "skipped": []}
        
        # Batch update using ThreadPoolExecutor
        results = {"success": [], "failed": [], "skipped": []}
        
        def update_single_model(model: Dict[str, Any]) -> Tuple[str, bool, str]:
            """Update a single model's permissions."""
            model_id = model.get("id", "")
            try:
                updated_model = self.update_model(model_id, access_control=access_control)
                if updated_model:
                    return model_id, True, "success"
                else:
                    return model_id, False, "update_failed"
            except Exception as e:
                logger.error(f"Exception updating model '{model_id}': {e}")
                return model_id, False, str(e)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_model = {
                executor.submit(update_single_model, model): model 
                for model in models_to_update
            }
            
            for future in as_completed(future_to_model):
                model = future_to_model[future]
                model_id = model.get("id", "unknown")
                try:
                    model_id, success, message = future.result()
                    if success:
                        results["success"].append(model_id)
                        logger.info(f"✅ Successfully updated permissions for model '{model_id}'")
                    else:
                        results["failed"].append({"model_id": model_id, "error": message})
                        logger.error(f"❌ Failed to update permissions for model '{model_id}': {message}")
                except Exception as e:
                    results["failed"].append({"model_id": model_id, "error": str(e)})
                    logger.error(f"❌ Exception processing result for model '{model_id}': {e}")
        
        logger.info(f"Batch update completed: {len(results['success'])} successful, {len(results['failed'])} failed")
        return results

    # =============================================================================
    # KNOWLEDGE BASE OPERATIONS - Delegate to KnowledgeBaseManager
    # =============================================================================

    def get_knowledge_base_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge base by its name."""
        return self._knowledge_base_manager.get_knowledge_base_by_name(name)

    def create_knowledge_base(
        self, name: str, description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Create a new knowledge base."""
        return self._knowledge_base_manager.create_knowledge_base(name, description)

    def add_file_to_knowledge_base(
        self, file_path: str, knowledge_base_name: str
    ) -> bool:
        """Add a file to a knowledge base."""
        return self._knowledge_base_manager.add_file_to_knowledge_base(
            file_path, knowledge_base_name
        )

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """Deletes a knowledge base by its ID."""
        return self._knowledge_base_manager.delete_knowledge_base(kb_id)

    def delete_all_knowledge_bases(self) -> Tuple[int, int]:
        """Deletes all knowledge bases for the current user."""
        return self._knowledge_base_manager.delete_all_knowledge_bases()

    def delete_knowledge_bases_by_keyword(
        self, keyword: str, case_sensitive: bool = False
    ) -> Tuple[int, int, List[str]]:
        """Deletes knowledge bases whose names contain a specific keyword."""
        return self._knowledge_base_manager.delete_knowledge_bases_by_keyword(
            keyword, case_sensitive
        )

    def create_knowledge_bases_with_files(
        self, kb_configs: List[Dict[str, Any]], max_workers: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """Creates multiple knowledge bases with files in parallel."""
        return self._knowledge_base_manager.create_knowledge_bases_with_files(
            kb_configs, max_workers
        )

    # =============================================================================
    # NOTES API - Delegate to NotesManager
    # =============================================================================

    def get_notes(self) -> Optional[List[Dict[str, Any]]]:
        """Get all notes for the current user."""
        return self._notes_manager.get_notes()

    def get_notes_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get a simplified list of notes with only id, title, and timestamps."""
        return self._notes_manager.get_notes_list()

    def create_note(
        self,
        title: str,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new note."""
        return self._notes_manager.create_note(title, data, meta, access_control)

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific note by its ID."""
        return self._notes_manager.get_note_by_id(note_id)

    def update_note_by_id(
        self,
        note_id: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing note by its ID."""
        return self._notes_manager.update_note_by_id(
            note_id, title, data, meta, access_control
        )

    def delete_note_by_id(self, note_id: str) -> bool:
        """Delete a note by its ID."""
        return self._notes_manager.delete_note_by_id(note_id)

    # =============================================================================
    # FILE OPERATIONS - Delegate to FileManager
    # =============================================================================

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file to the OpenWebUI server."""
        return self._file_manager.upload_file(file_path)

    @staticmethod
    def _encode_image_to_base64(image_path: str) -> Optional[str]:
        """Encode an image file to base64 format for use in multimodal chat."""
        # Create a temporary file manager instance for static method compatibility
        from .modules.file_manager import FileManager
        temp_manager = FileManager(None)
        return temp_manager.encode_image_to_base64(image_path)

    # =============================================================================
    # PLACEHOLDER METHODS - Will be implemented in next phase
    # =============================================================================
    
    def archive_chats_by_age(
        self,
        days_since_update: int = 30,
        folder_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Archive chats that haven't been updated for a specified number of days.
        
        Args:
            days_since_update: Number of days since last update (default: 30)
            folder_name: Optional folder name to filter chats. If None, only archives 
                        chats NOT in folders. If provided, only archives chats IN that folder.
            dry_run: If True, only shows what would be archived without actually archiving
                        
        Returns:
            Dictionary with archive results including counts and details
        """
        logger.info(f"Starting bulk archive operation for chats older than {days_since_update} days")
        if folder_name:
            logger.info(f"Filtering to folder: '{folder_name}'")
        else:
            logger.info("Filtering to chats NOT in folders")
            
        current_timestamp = int(time.time())
        cutoff_timestamp = current_timestamp - (days_since_update * 24 * 60 * 60)
        
        results = {
            "total_checked": 0,
            "total_archived": 0,
            "total_failed": 0,
            "archived_chats": [],
            "failed_chats": [],
            "errors": []
        }
        
        try:
            # Get target chats based on folder filter
            target_chats = []
            
            if folder_name:
                # Get folder ID by name
                folder_id = self.get_folder_id_by_name(folder_name)
                if not folder_id:
                    error_msg = f"Folder '{folder_name}' not found"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    return results
                    
                # Get chats in the specified folder
                folder_chats = self.get_chats_by_folder(folder_id)
                if folder_chats is None:
                    error_msg = f"Failed to get chats from folder '{folder_name}'"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    return results
                target_chats = folder_chats
            else:
                # Get all chats and filter to those NOT in folders
                all_chats = []
                page = 1
                
                # Handle pagination
                while True:
                    page_chats = self.list_chats(page=page)
                    if not page_chats:
                        break
                    all_chats.extend(page_chats)
                    # If we got fewer than expected, we've reached the end
                    if len(page_chats) < 50:  # Assuming default page size
                        break
                    page += 1
                
                if not all_chats:
                    error_msg = "Failed to get chat list"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    return results
                
                # Filter to chats not in folders
                # We need to get detailed chat info to check folder_id
                target_chats = []
                with ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_chat = {
                        executor.submit(self._get_chat_details, chat["id"]): chat 
                        for chat in all_chats
                    }
                    
                    for future in as_completed(future_to_chat):
                        chat_basic = future_to_chat[future]
                        try:
                            chat_details = future.result()
                            if chat_details and not chat_details.get("folder_id"):
                                target_chats.append(chat_details)
                        except Exception as e:
                            logger.warning(f"Failed to get details for chat {chat_basic['id']}: {e}")
                            
            results["total_checked"] = len(target_chats)
            logger.info(f"Found {len(target_chats)} chats to check for archiving")
            
            # Filter by age and archive
            chats_to_archive = []
            for chat in target_chats:
                updated_at = chat.get("updated_at", 0)
                if updated_at < cutoff_timestamp:
                    chats_to_archive.append(chat)
                    
            logger.info(f"Found {len(chats_to_archive)} chats older than {days_since_update} days")
            
            if dry_run:
                logger.info("Dry run mode: would archive the following chats:")
                for chat in chats_to_archive:
                    logger.info(f"  - {chat.get('title', 'Unknown')} (ID: {chat['id']})")
                results["total_archived"] = len(chats_to_archive)
                results["archived_chats"] = [{
                    "id": chat["id"],
                    "title": chat.get("title", "Unknown"),
                    "updated_at": chat.get("updated_at", 0)
                } for chat in chats_to_archive]
                return results
            
            # Archive chats in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_chat = {
                    executor.submit(self.archive_chat, chat["id"]): chat 
                    for chat in chats_to_archive
                }
                
                for future in as_completed(future_to_chat):
                    chat = future_to_chat[future]
                    try:
                        success = future.result()
                        if success:
                            results["total_archived"] += 1
                            results["archived_chats"].append({
                                "id": chat["id"],
                                "title": chat.get("title", "Unknown"),
                                "updated_at": chat.get("updated_at", 0)
                            })
                        else:
                            results["total_failed"] += 1
                            results["failed_chats"].append({
                                "id": chat["id"],
                                "title": chat.get("title", "Unknown"),
                                "error": "Archive request failed"
                            })
                    except Exception as e:
                        results["total_failed"] += 1
                        results["failed_chats"].append({
                            "id": chat["id"],
                            "title": chat.get("title", "Unknown"),
                            "error": str(e)
                        })
                        logger.error(f"Error archiving chat {chat['id']}: {e}")
            
            logger.info(f"Archive operation completed: {results['total_archived']} archived, {results['total_failed']} failed")
            return results
            
        except Exception as e:
            error_msg = f"Bulk archive operation failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def _cleanup_unused_placeholder_messages(self) -> int:
        """
        Clean up all unused empty placeholder messages in the current chat_object_from_server.
        Returns the number of message pairs cleaned up.
        """
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.error(
                "Chat object not initialized, cannot cleanup placeholder messages."
            )
            return 0

        chat_core = self.chat_object_from_server["chat"]
        messages = chat_core["history"]["messages"]

        # Collect all placeholder message IDs to be deleted
        message_ids_to_delete = []
        for msg_id, msg in messages.items():
            if self._is_placeholder_message(msg):
                message_ids_to_delete.append(msg_id)

        cleaned_count = 0
        if message_ids_to_delete:
            for msg_id in message_ids_to_delete:
                del messages[msg_id]
            cleaned_count = len(message_ids_to_delete) / 2  # Each pair contains user and assistant messages
            logger.info(
                f"Cleaned up {int(cleaned_count)} unused placeholder message pairs."
            )

            # After cleanup, need to rebuild the messages list and currentId to ensure history chain correctness
            # Find the new currentId (the ID of the last non-placeholder message)
            new_current_id = None
            for msg_id in reversed(list(messages.keys())):  # Search backwards
                msg = messages[msg_id]
                if not self._is_placeholder_message(msg):
                    new_current_id = msg_id
                    break

            chat_core["history"]["currentId"] = new_current_id
            chat_core["messages"] = self._build_linear_history_for_storage(
                chat_core, new_current_id
            )

            # Also need to sync with the backend
            if self._update_remote_chat():
                logger.info("Successfully synced chat state after cleanup.")
            else:
                logger.warning("Failed to sync chat state after cleanup.")

        return int(cleaned_count)

    def _is_placeholder_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is a placeholder (content is empty and not marked as done)"""
        return message.get("content", "").strip() == "" and not message.get("done", False)

    def _find_or_create_chat_by_title(self, title: str):
        """Find an existing chat by title or create a new one."""
        # TODO: Implement this method in ChatManager
        logger.warning("_find_or_create_chat_by_title not yet implemented in refactored version")
        pass

    def _load_chat_details(self, chat_id: str) -> bool:
        """Load chat details from server."""
        # TODO: Implement this method in ChatManager
        logger.warning("_load_chat_details not yet implemented in refactored version")
        return False

    def _search_latest_chat_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for the latest chat with the given title."""
        logger.info(f"Globally searching for chat with title '{title}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chats/search",
                params={"text": title},
                headers=self.json_headers,
            )
            response.raise_for_status()
            chats = response.json()
            if not chats:
                logger.info(f"No chats found with title '{title}'.")
                return None
            # Filter chats by title and find the most recent one
            matching_chats = [chat for chat in chats if chat.get("title") == title]
            if not matching_chats:
                logger.info(f"No chats found with exact title '{title}'.")
                return None
            # Return the most recent chat (highest updated_at)
            latest_chat = max(matching_chats, key=lambda x: x.get("updated_at", 0))
            logger.info(f"Found latest chat with title '{title}': {latest_chat['id'][:8]}...")
            return latest_chat
        except (requests.exceptions.RequestException, KeyError) as e:
            logger.error(f"Failed to search for chats with title '{title}': {e}")
            return None

    def _create_new_chat(self, title: str) -> Optional[str]:
        """Create a new chat with the given title."""
        logger.info(f"Creating new chat with title '{title}'...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chats/new",
                json={"chat": {"title": title}},
                headers=self.json_headers,
            )
            response.raise_for_status()
            chat_id = response.json().get("id")
            if chat_id:
                logger.info(f"Successfully created chat with ID: {chat_id[:8]}...")
                return chat_id
            else:
                logger.error("Chat creation response did not contain an ID.")
                return None
        except (requests.exceptions.RequestException, KeyError) as e:
            logger.error(f"Failed to create new chat: {e}")
            return None

    def _get_chat_details(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a chat."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chats/{chat_id}",
                headers=self.json_headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
            return None

    def _get_knowledge_base_details(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a knowledge base."""
        return self._knowledge_base_manager.get_knowledge_base_details(kb_id)

    def _build_linear_history_for_api(
        self, chat_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build linear message history for API calls."""
        history, current_id = [], chat_data.get("history", {}).get("currentId")
        messages = chat_data.get("history", {}).get("messages", {})
        while current_id and current_id in messages:
            msg = messages[current_id]
            if msg.get("files"):
                api_content = [{"type": "text", "text": msg["content"]}]
                for file_info in msg["files"]:
                    if file_info.get("type") == "image":
                        api_content.append(
                            {
                                "type": "image_url",
                                "image_url": {"url": file_info.get("url")},
                            }
                        )
                history.insert(0, {"role": msg["role"], "content": api_content})
            else:
                history.insert(0, {"role": msg["role"], "content": msg["content"]})
            current_id = msg.get("parentId")
        return history

    def _build_linear_history_for_storage(
        self, chat_core: Dict[str, Any], start_id: str
    ) -> List[Dict[str, Any]]:
        """Build linear message history for storage."""
        history, current_id = [], start_id
        messages = chat_core.get("history", {}).get("messages", {})
        while current_id and current_id in messages:
            history.insert(0, messages[current_id])
            current_id = messages[current_id].get("parentId")
        return history

    def _update_remote_chat(self) -> bool:
        """Update the remote chat with local changes."""
        try:
            self.session.post(
                f"{self.base_url}/api/v1/chats/{self.chat_id}",
                json={"chat": self.chat_object_from_server["chat"]},
                headers=self.json_headers,
            ).raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update remote chat: {e}")
            return False

    def _handle_rag_references(
        self, rag_files: Optional[List[str]] = None, rag_collections: Optional[List[str]] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """Handle RAG references for files and knowledge base collections."""
        api_payload, storage_payload = [], []
        if rag_files:
            logger.info("Processing RAG files...")
            for file_path in rag_files:
                if file_obj := self._upload_file(file_path):
                    api_payload.append({"type": "file", "id": file_obj["id"]})
                    storage_payload.append(
                        {"type": "file", "file": file_obj, **file_obj}
                    )
        if rag_collections:
            logger.info("Processing RAG knowledge base collections...")
            for kb_name in rag_collections:
                if kb_summary := self.get_knowledge_base_by_name(kb_name):
                    if kb_details := self._get_knowledge_base_details(kb_summary["id"]):
                        file_ids = [f["id"] for f in kb_details.get("files", [])]
                        api_payload.append(
                            {
                                "type": "collection",
                                "id": kb_details["id"],
                                "name": kb_details.get("name"),
                                "data": {"file_ids": file_ids},
                            }
                        )
                        storage_payload.append(
                            {
                                "type": "collection",
                                "collection": kb_details,
                                **kb_details,
                            }
                        )
        return api_payload, storage_payload

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file and return the file metadata."""
        return self._file_manager.upload_file(file_path)

    def _get_single_model_response_in_parallel(
        self,
        chat_core,
        model_id,
        question,
        image_paths,
        api_rag_payload,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
    ) -> Tuple[Optional[str], List, Optional[List[str]]]:
        """Get response from a single model for parallel chat functionality."""
        api_messages = self._build_linear_history_for_api(chat_core)
        current_user_content_parts = [{"type": "text", "text": question}]
        if image_paths:
            for path in image_paths:
                url = self._encode_image_to_base64(path)
                if url:
                    current_user_content_parts.append(
                        {"type": "image_url", "image_url": {"url": url}}
                    )
        final_api_content = (
            question
            if len(current_user_content_parts) == 1
            else current_user_content_parts
        )
        api_messages.append({"role": "user", "content": final_api_content})
        content, sources = self._get_model_completion(
            self.chat_id, api_messages, api_rag_payload, model_id, tool_ids
        )

        follow_ups = None
        if content and enable_follow_up:
            # To get follow-ups, we need the assistant's response in the history
            temp_history_for_follow_up = api_messages + [
                {"role": "assistant", "content": content}
            ]
            follow_ups = self._get_follow_up_completions(temp_history_for_follow_up)

        return content, sources, follow_ups

    def _get_title(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """
        Gets a title suggestion based on the conversation history.
        """
        task_model = self._get_task_model()
        if not task_model:
            logger.error("Could not determine task model for title. Aborting.")
            return None

        logger.info("Requesting title suggestion...")
        payload = {"model": task_model, "messages": messages, "stream": False}
        url = f"{self.base_url}/api/v1/tasks/title/completions"

        logger.debug(f"Sending title request to {url}: {json.dumps(payload, indent=2)}")

        try:
            response = self.session.post(url, json=payload, headers=self.json_headers)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if content:
                    try:
                        content_json = json.loads(content)
                        title = content_json.get("title")
                        if isinstance(title, str):
                            logger.info(f"   ✅ Received title suggestion: '{title}'")
                            return title
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from title content: {content}")
                        return None
            logger.warning(f"   ⚠️ Unexpected format for title response: {data}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Title API HTTP Error: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Title API Network Error: {e}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError):
            logger.error("Failed to parse JSON or find expected keys in title response.")
            return None

    def _get_tags(self, messages: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Gets tag suggestions based on the conversation history.
        """
        task_model = self._get_task_model()
        if not task_model:
            logger.error("Could not determine task model for tags. Aborting.")
            return None

        logger.info("Requesting tag suggestions...")
        payload = {"model": task_model, "messages": messages, "stream": False}
        url = f"{self.base_url}/api/v1/tasks/tags/completions"

        logger.debug(f"Sending tags request to {url}: {json.dumps(payload, indent=2)}")

        try:
            response = self.session.post(url, json=payload, headers=self.json_headers)
            response.raise_for_status()
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                try:
                    tags = json.loads(content)
                    if isinstance(tags, list):
                        logger.info(f"  > Generated tags: {tags}")
                        return tags
                    else:
                        logger.warning(f"Tags response not a list: {tags}")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tags JSON: {e}")
                    return None
            else:
                logger.error(f"Invalid tags response format: {response_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Tags request failed: {e}")
            return None

    def _ask(
        self,
        question: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
    ) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """Internal method for making chat requests."""
        if not self.chat_id:
            return None, None, None
        
        # For now, delegate to the chat manager's chat method
        # This is a simplified implementation for backward compatibility
        try:
            result = self._chat_manager.chat(
                question=question,
                chat_title=None,  # Use existing chat
                model_id=self.model_id,
                image_paths=image_paths,
                rag_files=rag_files,
                rag_collections=rag_collections,
                tool_ids=tool_ids,
                enable_follow_up=enable_follow_up
            )
            if result and "response" in result:
                response = result["response"]
                message_id = result.get("assistant_message_id")
                follow_up = result.get("suggested_follow_ups")
                return response, message_id, follow_up
            return None, None, None
        except Exception as e:
            logger.error(f"_ask failed: {e}")
            return None, None, None

    def _ask_stream(
        self,
        question: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
        cleanup_placeholder_messages: bool = False,
        placeholder_pool_size: int = 30,
        min_available_messages: int = 10,
    ) -> Generator[str, None, Tuple[str, List, Optional[List[str]]]]:
        """Internal method for making streaming chat requests."""
        if not self.chat_id:
            raise ValueError("Chat ID not set. Initialize chat first.")

        # For now, delegate to the chat manager's stream_chat method
        # This is a simplified implementation for backward compatibility
        try:
            generator = self._chat_manager.stream_chat(
                question=question,
                chat_title=None,  # Use existing chat
                model_id=self.model_id,
                image_paths=image_paths,
                rag_files=rag_files,
                rag_collections=rag_collections,
                tool_ids=tool_ids,
                enable_follow_up=enable_follow_up
            )
            
            # Yield the streaming content and return final result
            final_response = ""
            for chunk in generator:
                if isinstance(chunk, str):
                    final_response += chunk
                    yield chunk
                elif isinstance(chunk, dict):
                    # Final result
                    response = chunk.get("response", final_response)
                    sources = chunk.get("sources", [])
                    follow_up = chunk.get("suggested_follow_ups")
                    return response, sources, follow_up
            
            # If we reach here, return the accumulated response
            return final_response, [], None
            
        except Exception as e:
            logger.error(f"_ask_stream failed: {e}")
            return "", [], None

    def _get_follow_up_completions(
        self, messages: List[Dict[str, Any]]
    ) -> Optional[List[str]]:
        """
        Gets follow-up suggestions based on the conversation history.
        """
        task_model = self._get_task_model()
        if not task_model:
            logger.error(
                "Could not determine task model for follow-up suggestions. Aborting."
            )
            return None

        logger.info("Requesting follow-up suggestions...")
        payload = {
            "model": task_model,
            "messages": messages,
            "stream": False,
        }
        url = f"{self.base_url}/api/v1/tasks/follow_up/completions"

        logger.debug(
            f"Sending follow-up request to {url}: {json.dumps(payload, indent=2)}"
        )

        try:
            response = self.session.post(url, json=payload, headers=self.json_headers)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if content:
                    try:
                        # The actual suggestions are in a JSON string inside the content
                        content_json = json.loads(content)
                        follow_ups = content_json.get(
                            "follow_ups"
                        )  # Note: key is 'follow_ups' not 'followUps'
                        if isinstance(follow_ups, list):
                            logger.info(
                                f"   ✅ Received {len(follow_ups)} follow-up suggestions."
                            )
                            return follow_ups
                    except json.JSONDecodeError:
                        logger.error(
                            f"Failed to decode JSON from follow-up content: {content}"
                        )
                        return None

            logger.warning(f"   ⚠️ Unexpected format for follow-up response: {data}")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"Follow-up API HTTP Error: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Follow-up API Network Error: {e}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError):
            logger.error(
                "Failed to parse JSON or find expected keys in follow-up response."
            )
            return None

    def _get_model_completion(
        self,
        chat_id: str,
        messages: List[Dict[str, Any]],
        api_rag_payload: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], List]:
        """Get completion from a model."""
        active_model_id = model_id or self.model_id
        payload = {
            "model": active_model_id,
            "messages": messages,
            "stream": False,  # Non-streaming
        }
        if api_rag_payload:
            payload["files"] = api_rag_payload
            logger.info(
                f"Attaching {len(api_rag_payload)} RAG references to completion request for model {active_model_id}."
            )

        if tool_ids:
            # The backend expects a list of objects, each with an 'id'
            payload["tool_ids"] = tool_ids
            logger.info(
                f"Attaching {len(tool_ids)} tools to completion request for model {active_model_id}."
            )

        logger.debug(
            f"Sending NON-STREAMING completion request: {json.dumps(payload, indent=2)}"
        )

        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/completions",
                json=payload,
                headers=self.json_headers,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            sources = data.get("sources", [])
            return content, sources
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Completions API HTTP Error for {active_model_id}: {e.response.text}"
            )
            raise e
        except (KeyError, IndexError) as e:
            logger.error(f"Completions API Response Error for {active_model_id}: {e}")
            return None, []
        except requests.exceptions.RequestException as e:
            logger.error(f"Completions API Network Error for {active_model_id}: {e}")
            return None, []

    def _get_model_completion_stream(
        self,
        chat_id: str,
        messages: List[Dict[str, Any]],
        api_rag_payload: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Generator[str, None, List]:
        """Get streaming completion from a model."""
        active_model_id = model_id or self.model_id
        payload = {
            "model": active_model_id,
            "messages": messages,
            "stream": True,  # Enable streaming
        }
        if api_rag_payload:
            payload["files"] = api_rag_payload
        if tool_ids:
            payload["tool_ids"] = tool_ids

        logger.debug(
            f"Sending STREAMING completion request: {json.dumps(payload, indent=2)}"
        )

        try:
            # Use stream=True to keep the connection open
            with self.session.post(
                f"{self.base_url}/api/chat/completions",
                json=payload,
                headers=self.json_headers,
                stream=True,  # Enable streaming on requests session
            ) as response:
                response.raise_for_status()

                sources = []

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[len("data:") :].strip()
                            if json_data == "[DONE]":
                                break

                            try:
                                data = json.loads(json_data)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content_chunk = delta.get("content", "")

                                    # Handle sources if they come in streaming chunks (though usually at end)
                                    if "sources" in data:
                                        sources.extend(data["sources"])

                                    if content_chunk:
                                        yield content_chunk  # Yield each chunk of content

                                # Handle final sources if they are sent as part of a non-delta message at the end
                                if (
                                    "sources" in data and not sources
                                ):  # Only if sources haven't been collected yet
                                    sources.extend(data["sources"])

                            except json.JSONDecodeError:
                                logger.warning(
                                    f"Failed to decode JSON from stream: {json_data}"
                                )
                                continue
                return sources  # Return sources at the end of the generator
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Streaming Completions API Network Error for {active_model_id}: {e}"
            )
            raise

    def _get_task_model(self) -> Optional[str]:
        """Get the task model for metadata operations."""
        # Use the current model or task model
        return getattr(self, 'task_model', None) or self.model_id