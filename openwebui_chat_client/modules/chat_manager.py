"""
Chat management module for OpenWebUI Chat Client.
Handles all chat operations including creation, messaging, management, and streaming.
"""

import json
import logging
import requests
import time
import uuid
from typing import Optional, List, Dict, Any, Union, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ChatManager:
    """
    Handles all chat-related operations for the OpenWebUI client.
    
    This class manages:
    - Chat creation and management
    - Single and multi-model conversations
    - Streaming chat functionality
    - Chat organization (folders, tags)
    - Chat archiving and bulk operations
    - Message management and placeholder handling
    """
    
    def __init__(self, base_client):
        """
        Initialize the chat manager.
        
        Args:
            base_client: The base client instance for making API requests
        """
        self.base_client = base_client
    
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
        """
        Send a chat message with a single model.
        
        Args:
            question: The user's question/message
            chat_title: Title for the chat conversation
            model_id: Model to use (defaults to client's default model)
            folder_name: Optional folder to organize the chat
            image_paths: List of image file paths for multimodal chat
            tags: List of tags to apply to the chat
            rag_files: List of file paths for RAG context
            rag_collections: List of knowledge base names for RAG
            tool_ids: List of tool IDs to enable for this chat
            enable_follow_up: Whether to generate follow-up suggestions
            enable_auto_tagging: Whether to automatically generate tags
            enable_auto_titling: Whether to automatically generate title
            
        Returns:
            Dictionary containing response, chat_id, message_id and optional suggestions
        """
        self.base_client.model_id = model_id or self.base_client.default_model_id
        logger.info("=" * 60)
        logger.info(
            f"Processing SINGLE-MODEL request: title='{chat_title}', model='{self.base_client.model_id}'"
        )
        if folder_name:
            logger.info(f"Folder: '{folder_name}'")
        if tags:
            logger.info(f"Tags: {tags}")
        if image_paths:
            logger.info(f"With images: {image_paths}")
        if rag_files:
            logger.info(f"With RAG files: {rag_files}")
        if rag_collections:
            logger.info(f"With KB collections: {rag_collections}")
        if tool_ids:
            logger.info(f"Using tools: {tool_ids}")
        logger.info("=" * 60)

        self._find_or_create_chat_by_title(chat_title)

        if not self.base_client.chat_object_from_server or "chat" not in self.base_client.chat_object_from_server:
            logger.error("Chat object not loaded or malformed, cannot proceed with chat.")
            return None

        # Handle model switching for an existing chat
        if model_id and self.base_client.model_id != model_id:
            logger.warning(f"Model switch detected for chat '{chat_title}'.")
            logger.warning(f"  > Changing from: '{self.base_client.model_id}'")
            logger.warning(f"  > Changing to:   '{model_id}'")
            self.base_client.model_id = model_id
            if self.base_client.chat_object_from_server and "chat" in self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["chat"]["models"] = [model_id]

        if not self.base_client.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return None
            
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(folder_name)
            if folder_id and self.base_client.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.base_client.chat_id, folder_id)

        response, message_id, follow_ups = self._ask(
            question,
            image_paths,
            rag_files,
            rag_collections,
            tool_ids,
            enable_follow_up,
        )
        if response:
            if tags:
                self.set_chat_tags(self.base_client.chat_id, tags)

            # New auto-tagging and auto-titling logic
            api_messages_for_tasks = self._build_linear_history_for_api(
                self.base_client.chat_object_from_server["chat"]
            )
            
            return_data = {
                "response": response,
                "chat_id": self.base_client.chat_id,
                "message_id": message_id,
            }

            if enable_auto_tagging:
                suggested_tags = self._get_tags(api_messages_for_tasks)
                if suggested_tags:
                    self.set_chat_tags(self.base_client.chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags

            if enable_auto_titling and len(
                self.base_client.chat_object_from_server["chat"]["history"]["messages"]
            ) <= 2:
                suggested_title = self._get_title(api_messages_for_tasks)
                if suggested_title:
                    self.rename_chat(self.base_client.chat_id, suggested_title)
                    return_data["suggested_title"] = suggested_title

            if follow_ups:
                return_data["follow_ups"] = follow_ups
            return return_data
        return None

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
        """
        Send a chat message to multiple models in parallel.
        
        Args:
            question: The user's question/message
            chat_title: Title for the chat conversation
            model_ids: List of model IDs to query in parallel
            folder_name: Optional folder to organize the chat
            image_paths: List of image file paths for multimodal chat
            tags: List of tags to apply to the chat
            rag_files: List of file paths for RAG context
            rag_collections: List of knowledge base names for RAG
            tool_ids: List of tool IDs to enable for this chat
            enable_follow_up: Whether to generate follow-up suggestions
            enable_auto_tagging: Whether to automatically generate tags
            enable_auto_titling: Whether to automatically generate title
            
        Returns:
            Dictionary containing responses from all models, chat_id, and optional suggestions
        """
        if not model_ids:
            logger.error("`model_ids` list cannot be empty for parallel chat.")
            return None
        self.base_client.model_id = model_ids[0]
        logger.info("=" * 60)
        logger.info(
            f"Processing PARALLEL-MODEL request: title='{chat_title}', models={model_ids}"
        )
        if rag_files:
            logger.info(f"With RAG files: {rag_files}")
        if rag_collections:
            logger.info(f"With KB collections: {rag_collections}")
        if tool_ids:
            logger.info(f"Using tools: {tool_ids}")
        logger.info("=" * 60)

        self._find_or_create_chat_by_title(chat_title)

        if not self.base_client.chat_object_from_server or "chat" not in self.base_client.chat_object_from_server:
            logger.error("Chat object not loaded or malformed, cannot proceed with parallel chat.")
            return None

        if not self.base_client.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return None

        # Handle folder organization
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(folder_name)
            if folder_id and self.base_client.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.base_client.chat_id, folder_id)

        # Set multiple models for the chat
        if self.base_client.chat_object_from_server and "chat" in self.base_client.chat_object_from_server:
            self.base_client.chat_object_from_server["chat"]["models"] = model_ids

        # Get parallel responses
        model_responses = self._get_parallel_model_responses(
            question, model_ids, image_paths, rag_files, rag_collections, tool_ids, enable_follow_up
        )

        if not model_responses:
            logger.error("No successful responses from parallel models.")
            return None

        # Apply tags if provided
        if tags:
            self.set_chat_tags(self.base_client.chat_id, tags)

        # Auto-tagging and auto-titling (use first successful response)
        return_data = {
            "responses": model_responses,
            "chat_id": self.base_client.chat_id,
        }

        if enable_auto_tagging or enable_auto_titling:
            api_messages_for_tasks = self._build_linear_history_for_api(
                self.base_client.chat_object_from_server["chat"]
            )

            if enable_auto_tagging:
                suggested_tags = self._get_tags(api_messages_for_tasks)
                if suggested_tags:
                    self.set_chat_tags(self.base_client.chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags

            if enable_auto_titling and len(
                self.base_client.chat_object_from_server["chat"]["history"]["messages"]
            ) <= 2:
                suggested_title = self._get_title(api_messages_for_tasks)
                if suggested_title:
                    self.rename_chat(self.base_client.chat_id, suggested_title)
                    return_data["suggested_title"] = suggested_title

        return return_data

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
        """
        Stream a chat response in real-time.
        
        Args:
            question: The user's question/message
            chat_title: Title for the chat conversation
            model_id: Model to use (defaults to client's default model)
            folder_name: Optional folder to organize the chat
            image_paths: List of image file paths for multimodal chat
            tags: List of tags to apply to the chat
            rag_files: List of file paths for RAG context
            rag_collections: List of knowledge base names for RAG
            tool_ids: List of tool IDs to enable for this chat
            enable_follow_up: Whether to generate follow-up suggestions
            enable_auto_tagging: Whether to automatically generate tags
            enable_auto_titling: Whether to automatically generate title
            
        Yields:
            String chunks of the response as they arrive
        """
        self.base_client.model_id = model_id or self.base_client.default_model_id
        logger.info("=" * 60)
        logger.info(
            f"Processing STREAMING request: title='{chat_title}', model='{self.base_client.model_id}'"
        )
        if folder_name:
            logger.info(f"Folder: '{folder_name}'")
        if tags:
            logger.info(f"Tags: {tags}")
        if image_paths:
            logger.info(f"With images: {image_paths}")
        if rag_files:
            logger.info(f"With RAG files: {rag_files}")
        if rag_collections:
            logger.info(f"With KB collections: {rag_collections}")
        if tool_ids:
            logger.info(f"Using tools: {tool_ids}")
        logger.info("=" * 60)

        self._find_or_create_chat_by_title(chat_title)

        if not self.base_client.chat_object_from_server or "chat" not in self.base_client.chat_object_from_server:
            logger.error("Chat object not loaded or malformed, cannot proceed with streaming chat.")
            return

        # Handle model switching for an existing chat
        if model_id and self.base_client.model_id != model_id:
            logger.warning(f"Model switch detected for chat '{chat_title}'.")
            self.base_client.model_id = model_id
            if self.base_client.chat_object_from_server and "chat" in self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["chat"]["models"] = [model_id]

        if not self.base_client.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return

        # Handle folder organization
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(folder_name)
            if folder_id and self.base_client.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.base_client.chat_id, folder_id)

        # Stream the response
        accumulated_response = ""
        message_id = None
        follow_ups = None

        try:
            for chunk in self._ask_stream(
                question,
                image_paths,
                rag_files,
                rag_collections,
                tool_ids,
                enable_follow_up,
            ):
                if isinstance(chunk, dict):
                    # Handle metadata (message_id, follow_ups, etc.)
                    if "message_id" in chunk:
                        message_id = chunk["message_id"]
                    if "follow_ups" in chunk:
                        follow_ups = chunk["follow_ups"]
                else:
                    # Handle text chunk
                    accumulated_response += chunk
                    yield chunk

            # Apply post-processing after streaming completes
            if tags:
                self.set_chat_tags(self.base_client.chat_id, tags)

            # Auto-tagging and auto-titling
            if (enable_auto_tagging or enable_auto_titling) and accumulated_response:
                api_messages_for_tasks = self._build_linear_history_for_api(
                    self.base_client.chat_object_from_server["chat"]
                )

                if enable_auto_tagging:
                    suggested_tags = self._get_tags(api_messages_for_tasks)
                    if suggested_tags:
                        self.set_chat_tags(self.base_client.chat_id, suggested_tags)

                if enable_auto_titling and len(
                    self.base_client.chat_object_from_server["chat"]["history"]["messages"]
                ) <= 2:
                    suggested_title = self._get_title(api_messages_for_tasks)
                    if suggested_title:
                        self.rename_chat(self.base_client.chat_id, suggested_title)

        except Exception as e:
            logger.error(f"Error during streaming chat: {e}")
            yield f"[Error: {str(e)}]"

    def set_chat_tags(self, chat_id: str, tags: List[str]):
        """
        Set tags for a chat conversation.
        
        Args:
            chat_id: ID of the chat to tag
            tags: List of tag names to apply
        """
        if not tags:
            return
        logger.info(f"Applying tags {tags} to chat {chat_id[:8]}...")
        url_get = f"{self.base_client.base_url}/api/v1/chats/{chat_id}/tags"
        try:
            response = self.base_client.session.get(url_get, headers=self.base_client.json_headers)
            response.raise_for_status()
            existing_tags = {tag["name"] for tag in response.json()}
        except requests.exceptions.RequestException:
            logger.warning("Could not fetch existing tags. May create duplicates.")
            existing_tags = set()
        url_post = f"{self.base_client.base_url}/api/v1/chats/{chat_id}/tags"
        for tag_name in tags:
            if tag_name not in existing_tags:
                try:
                    self.base_client.session.post(
                        url_post, json={"name": tag_name}, headers=self.base_client.json_headers
                    ).raise_for_status()
                    logger.info(f"  + Added tag: '{tag_name}'")
                except requests.exceptions.RequestException as e:
                    logger.error(f"  - Failed to add tag '{tag_name}': {e}")
            else:
                logger.info(f"  = Tag '{tag_name}' already exists, skipping.")

    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """
        Rename an existing chat.
        
        Args:
            chat_id: ID of the chat to rename
            new_title: New title for the chat
            
        Returns:
            True if rename was successful, False otherwise
        """
        if not chat_id:
            logger.error("rename_chat: chat_id cannot be empty.")
            return False

        url = f"{self.base_client.base_url}/api/v1/chats/{chat_id}"
        payload = {"chat": {"title": new_title}}

        try:
            response = self.base_client.session.post(url, json=payload, headers=self.base_client.json_headers)
            response.raise_for_status()
            logger.info(f"Successfully renamed chat {chat_id[:8]}... to '{new_title}'")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to rename chat {chat_id[:8]}...: {e}")
            return False

    def update_chat_metadata(
        self,
        chat_id: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_name: Optional[str] = None
    ) -> bool:
        """
        Update various metadata for a chat.
        
        Args:
            chat_id: ID of the chat to update
            title: New title for the chat
            tags: New tags to apply to the chat
            folder_name: Folder to move the chat to
            
        Returns:
            True if all updates were successful, False otherwise
        """
        if not chat_id:
            logger.error("Chat ID cannot be empty.")
            return False

        success = True

        # Update title
        if title is not None:
            if not self.rename_chat(chat_id, title):
                success = False

        # Update tags
        if tags is not None:
            try:
                self.set_chat_tags(chat_id, tags)
            except Exception as e:
                logger.error(f"Failed to set tags: {e}")
                success = False

        # Update folder
        if folder_name is not None:
            try:
                folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(folder_name)
                if folder_id:
                    self.move_chat_to_folder(chat_id, folder_id)
                else:
                    success = False
            except Exception as e:
                logger.error(f"Failed to move chat to folder: {e}")
                success = False

        return success

    def switch_chat_model(self, chat_id: str, model_ids: Union[str, List[str]]) -> bool:
        """
        Switch the model(s) for an existing chat.
        
        Args:
            chat_id: ID of the chat to update
            model_ids: Single model ID or list of model IDs
            
        Returns:
            True if the switch was successful, False otherwise
        """
        if not chat_id:
            logger.error("Chat ID cannot be empty.")
            return False

        if isinstance(model_ids, str):
            model_ids = [model_ids]

        if not model_ids:
            logger.error("At least one model ID must be provided.")
            return False

        logger.info(f"Switching chat {chat_id[:8]}... to models: {model_ids}")

        try:
            # Get current chat details
            chat_details = self._get_chat_details(chat_id)
            if not chat_details or "chat" not in chat_details:
                logger.error(f"Failed to get chat details for {chat_id}")
                return False

            # Update the models
            chat_details["chat"]["models"] = model_ids

            # Update on server
            url = f"{self.base_client.base_url}/api/v1/chats/{chat_id}"
            response = self.base_client.session.put(
                url, 
                json=chat_details, 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()

            # Update local state if this is the current chat
            if self.base_client.chat_id == chat_id:
                self.base_client.model_id = model_ids[0] if model_ids else self.base_client.default_model_id
                self.base_client.chat_object_from_server = chat_details

            logger.info(f"Successfully switched models for chat {chat_id[:8]}...")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to switch models for chat {chat_id[:8]}...: {e}")
            return False

    def list_chats(self, page: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """
        List all chats for the current user.
        
        Args:
            page: Optional page number for pagination
            
        Returns:
            List of chat dictionaries or None if failed
        """
        logger.info("Fetching chat list...")
        url = f"{self.base_client.base_url}/api/v1/chats/list"
        params = {}
        if page is not None:
            params["page"] = page

        try:
            response = self.base_client.session.get(
                url, 
                params=params, 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            chats = response.json()
            logger.info(f"Successfully retrieved {len(chats)} chats.")
            return chats
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch chat list: {e}")
            return None

    def get_chats_by_folder(self, folder_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all chats in a specific folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of chat dictionaries in the folder or None if failed
        """
        logger.info(f"Fetching chats from folder: {folder_id}")
        url = f"{self.base_client.base_url}/api/v1/chats/folder/{folder_id}"

        try:
            response = self.base_client.session.get(url, headers=self.base_client.json_headers)
            response.raise_for_status()
            chats = response.json()
            logger.info(f"Successfully retrieved {len(chats)} chats from folder.")
            return chats
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch chats from folder {folder_id}: {e}")
            return None

    def archive_chat(self, chat_id: str) -> bool:
        """
        Archive a chat conversation.
        
        Args:
            chat_id: ID of the chat to archive
            
        Returns:
            True if archiving was successful, False otherwise
        """
        logger.info(f"Archiving chat: {chat_id}")
        url = f"{self.base_client.base_url}/api/v1/chats/{chat_id}/archive"

        try:
            response = self.base_client.session.post(url, headers=self.base_client.json_headers)
            response.raise_for_status()
            logger.info(f"Successfully archived chat: {chat_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to archive chat {chat_id}: {e}")
            return False

    def create_folder(self, name: str) -> Optional[str]:
        """
        Create a new folder for organizing chats.
        
        Args:
            name: Name of the folder to create
            
        Returns:
            Folder ID if creation was successful, None otherwise
        """
        logger.info(f"Creating folder: '{name}'")
        url = f"{self.base_client.base_url}/api/v1/folders/"
        payload = {"name": name}

        try:
            response = self.base_client.session.post(
                url, 
                json=payload, 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            folder_data = response.json()
            folder_id = folder_data.get("id")
            logger.info(f"Successfully created folder '{name}' with ID: {folder_id}")
            return folder_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    def get_folder_id_by_name(self, folder_name: str) -> Optional[str]:
        """
        Get folder ID by folder name.
        
        Args:
            folder_name: Name of the folder to find
            
        Returns:
            Folder ID if found, None otherwise
        """
        logger.info(f"Looking up folder ID for: '{folder_name}'")
        url = f"{self.base_client.base_url}/api/v1/folders/"

        try:
            response = self.base_client.session.get(url, headers=self.base_client.json_headers)
            response.raise_for_status()
            folders = response.json()
            
            for folder in folders:
                if folder.get("name") == folder_name:
                    folder_id = folder.get("id")
                    logger.info(f"Found folder '{folder_name}' with ID: {folder_id}")
                    return folder_id
            
            logger.info(f"Folder '{folder_name}' not found")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to lookup folder '{folder_name}': {e}")
            return None

    def move_chat_to_folder(self, chat_id: str, folder_id: str):
        """
        Move a chat to a specific folder.
        
        Args:
            chat_id: ID of the chat to move
            folder_id: ID of the destination folder
        """
        logger.info(f"Moving chat {chat_id[:8]}... to folder {folder_id[:8]}...")
        url = f"{self.base_client.base_url}/api/v1/chats/{chat_id}/folder"
        payload = {"folder_id": folder_id}

        try:
            response = self.base_client.session.post(
                url, 
                json=payload, 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            logger.info("Chat moved to folder successfully.")
            
            # Update local state
            if self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["folder_id"] = folder_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to move chat to folder: {e}")

    # Helper methods for chat management
    def _find_or_create_chat_by_title(self, title: str):
        """Find an existing chat by title or create a new one."""
        if existing_chat := self._search_latest_chat_by_title(title):
            logger.info(f"Found and loading chat '{title}' via API.")
            self._load_chat_details(existing_chat["id"])
        else:
            logger.info(f"Chat '{title}' not found, creating a new one.")
            if new_chat_id := self._create_new_chat(title):
                self._load_chat_details(new_chat_id)

    def _search_latest_chat_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for the latest chat with the given title."""
        logger.info(f"Globally searching for chat with title '{title}'...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/chats/search",
                params={"text": title},
                headers=self.base_client.json_headers,
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
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/chats/new",
                json={"chat": {"title": title}},
                headers=self.base_client.json_headers,
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

    def _load_chat_details(self, chat_id: str) -> bool:
        """Load chat details from server."""
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/chats/{chat_id}", 
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            details = response.json()
            if details:
                self.base_client.chat_id = chat_id
                self.base_client.chat_object_from_server = details
                chat_core = self.base_client.chat_object_from_server.setdefault("chat", {})
                chat_core.setdefault("history", {"messages": {}, "currentId": None})
                # Ensure 'models' is a list
                models_list = chat_core.get("models", [])
                if isinstance(models_list, list) and models_list:
                    self.base_client.model_id = models_list[0]
                else:
                    self.base_client.model_id = self.base_client.default_model_id
                logger.info(f"Successfully loaded chat details for {chat_id[:8]}...")
                return True
            else:
                logger.warning(f"Empty response when loading chat details for {chat_id}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
            return False
    
    def _ask(self, question: str, image_paths: Optional[List[str]] = None, 
             rag_files: Optional[List[str]] = None, rag_collections: Optional[List[str]] = None,
             tool_ids: Optional[List[str]] = None, enable_follow_up: bool = False) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """Send a message and get response."""
        if not self.base_client.chat_id:
            return None, None, None
        logger.info(f'Processing question: "{question}"')
        chat_core = self.base_client.chat_object_from_server["chat"]
        chat_core["models"] = [self.base_client.model_id]

        api_rag_payload, storage_rag_payloads = self._handle_rag_references(
            rag_files, rag_collections
        )

        api_messages = self._build_linear_history_for_api(chat_core)
        current_user_content_parts = [{"type": "text", "text": question}]
        if image_paths:
            for image_path in image_paths:
                base64_image = self._encode_image_to_base64(image_path)
                if base64_image:
                    current_user_content_parts.append(
                        {"type": "image_url", "image_url": {"url": base64_image}}
                    )
        final_api_content = (
            question
            if len(current_user_content_parts) == 1
            else current_user_content_parts
        )
        api_messages.append({"role": "user", "content": final_api_content})

        logger.info("Calling NON-STREAMING completions API to get model response...")
        assistant_content, sources = (
            self._get_model_completion(  # Call non-streaming method
                self.base_client.chat_id, api_messages, api_rag_payload, self.base_client.model_id, tool_ids
            )
        )
        if assistant_content is None:
            return None, None, None
        logger.info("Successfully received model response.")

        user_message_id, last_message_id = str(uuid.uuid4()), chat_core["history"].get(
            "currentId"
        )
        storage_user_message = {
            "id": user_message_id,
            "parentId": last_message_id,
            "childrenIds": [],
            "role": "user",
            "content": question,
            "files": [],
            "models": [self.base_client.model_id],
            "timestamp": int(time.time()),
        }
        if image_paths:
            for image_path in image_paths:
                base64_url = self._encode_image_to_base64(image_path)
                if base64_url:
                    storage_user_message["files"].append(
                        {"type": "image", "url": base64_url}
                    )
        storage_user_message["files"].extend(storage_rag_payloads)
        chat_core["history"]["messages"][user_message_id] = storage_user_message
        if last_message_id:
            chat_core["history"]["messages"][last_message_id]["childrenIds"].append(
                user_message_id
            )

        assistant_message_id = str(uuid.uuid4())
        storage_assistant_message = {
            "id": assistant_message_id,
            "parentId": user_message_id,
            "childrenIds": [],
            "role": "assistant",
            "content": assistant_content,
            "model": self.base_client.model_id,
            "modelName": self.base_client.model_id.split(":")[0],
            "timestamp": int(time.time()),
            "done": True,
            "sources": sources,
        }
        chat_core["history"]["messages"][
            assistant_message_id
        ] = storage_assistant_message
        chat_core["history"]["messages"][user_message_id]["childrenIds"].append(
            assistant_message_id
        )

        chat_core["history"]["currentId"] = assistant_message_id
        chat_core["messages"] = self._build_linear_history_for_storage(
            chat_core, assistant_message_id
        )
        chat_core["models"] = [self.base_client.model_id]
        existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
        chat_core.setdefault("files", []).extend(
            [f for f in storage_rag_payloads if f["id"] not in existing_file_ids]
        )

        logger.info("Updating chat history on the backend...")
        if self._update_remote_chat():
            logger.info("Chat history updated successfully!")

            follow_ups = None
            if enable_follow_up:
                logger.info("Follow-up is enabled, fetching suggestions...")
                # The API for follow-up needs the full context including the latest assistant response
                api_messages_for_follow_up = self._build_linear_history_for_api(
                    chat_core
                )
                follow_ups = self._get_follow_up_completions(api_messages_for_follow_up)
                if follow_ups:
                    logger.info(f"Received {len(follow_ups)} follow-up suggestions.")
                    # Update the specific assistant message with the follow-ups
                    chat_core["history"]["messages"][assistant_message_id][
                        "followUps"
                    ] = follow_ups
                    # A second update to save the follow-ups
                    if self._update_remote_chat():
                        logger.info(
                            "Successfully updated chat with follow-up suggestions."
                        )
                    else:
                        logger.warning(
                            "Failed to update chat with follow-up suggestions."
                        )
                else:
                    logger.info("No follow-up suggestions were generated.")

            return assistant_content, assistant_message_id, follow_ups
        return None, None, None
    
    def _ask_stream(self, question: str, image_paths: Optional[List[str]] = None,
                   rag_files: Optional[List[str]] = None, rag_collections: Optional[List[str]] = None,
                   tool_ids: Optional[List[str]] = None, enable_follow_up: bool = False) -> Generator[Union[str, Dict], None, None]:
        """Send a message and stream the response."""
        # Implementation will be added
        pass
    
    def _get_parallel_model_responses(self, question: str, model_ids: List[str],
                                    image_paths: Optional[List[str]] = None,
                                    rag_files: Optional[List[str]] = None,
                                    rag_collections: Optional[List[str]] = None,
                                    tool_ids: Optional[List[str]] = None,
                                    enable_follow_up: bool = False) -> Dict[str, Any]:
        """Get responses from multiple models in parallel."""
        # Implementation will be added
        pass
    
    def _build_linear_history_for_api(self, chat_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build linear message history for API calls."""
        history = chat_data.get("history", {})
        messages = history.get("messages", {})
        current_id = history.get("currentId")
        
        linear_messages = []
        if not current_id:
            return linear_messages
            
        # Build the conversation chain by following parentId relationships backwards
        message_chain = []
        msg_id = current_id
        while msg_id and msg_id in messages:
            message_chain.append(messages[msg_id])
            msg_id = messages[msg_id].get("parentId")
        
        # Reverse to get chronological order
        message_chain.reverse()
        
        # Convert to API format
        for msg in message_chain:
            if msg.get("role") in ["user", "assistant"]:
                linear_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })
        
        return linear_messages

    def _handle_rag_references(self, rag_files: Optional[List[str]] = None, 
                             rag_collections: Optional[List[str]] = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Handle RAG file and collection processing."""
        api_rag_payload = {}
        storage_rag_payloads = []
        
        if rag_files:
            # Process file uploads for RAG
            for file_path in rag_files:
                file_data = self.base_client._upload_file(file_path)
                if file_data:
                    storage_rag_payloads.append(file_data)
                    
        if rag_collections:
            # Add knowledge base collections to API payload
            api_rag_payload["knowledge"] = [{"name": name} for name in rag_collections]
            
        return api_rag_payload, storage_rag_payloads

    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 URL."""
        try:
            import base64
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/jpeg;base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    def _get_model_completion(self, chat_id: str, messages: List[Dict[str, Any]], 
                            rag_payload: Dict[str, Any], model_id: str, 
                            tool_ids: Optional[List[str]] = None) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Get model completion from API."""
        try:
            payload = {
                "model": model_id,
                "messages": messages,
                "stream": False,
                "chat_id": chat_id,
            }
            
            if rag_payload:
                payload.update(rag_payload)
                
            if tool_ids:
                payload["tools"] = [{"type": "function", "function": {"name": tool_id}} for tool_id in tool_ids]
                
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/chat/completions",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            sources = data.get("sources", [])
            
            return content, sources
            
        except Exception as e:
            logger.error(f"Failed to get model completion: {e}")
            return None, []

    def _build_linear_history_for_storage(self, chat_core: Dict[str, Any], start_id: str) -> List[Dict[str, Any]]:
        """Build linear message history for storage."""
        messages = chat_core.get("history", {}).get("messages", {})
        linear_messages = []
        
        # Build the conversation chain by following parentId relationships backwards
        message_chain = []
        msg_id = start_id
        while msg_id and msg_id in messages:
            message_chain.append(messages[msg_id])
            msg_id = messages[msg_id].get("parentId")
        
        # Reverse to get chronological order
        message_chain.reverse()
        
        # Convert to storage format
        for msg in message_chain:
            linear_messages.append({
                "id": msg["id"],
                "role": msg["role"],
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", int(time.time()))
            })
        
        return linear_messages

    def _update_remote_chat(self) -> bool:
        """Update remote chat on server."""
        if not self.base_client.chat_id or not self.base_client.chat_object_from_server:
            return False
            
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/chats/{self.base_client.chat_id}",
                json=self.base_client.chat_object_from_server,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update remote chat: {e}")
            return False

    def _get_follow_up_completions(self, messages: List[Dict[str, Any]]) -> Optional[List[str]]:
        """Get follow-up suggestions."""
        try:
            # Get task model for follow-up generation
            task_model = self.base_client._get_task_model()
            if not task_model:
                logger.error("Could not determine task model for follow-up suggestions. Aborting.")
                return None
            
            payload = {
                "model": task_model,
                "messages": messages,
                "stream": False
            }
            
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/tasks/follow_up/completions",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the follow-up content (it's usually JSON)
            try:
                import json
                follow_up_data = json.loads(content)
                return follow_up_data.get("follow_ups", [])
            except json.JSONDecodeError:
                logger.warning("Failed to parse follow-up response as JSON")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get follow-up completions: {e}")
            return None
    
    def _get_tags(self, messages: List[Dict[str, Any]]) -> Optional[List[str]]:
        """Generate tags for the conversation."""
        try:
            # Get task model for tag generation
            task_model = self.base_client._get_task_model()
            if not task_model:
                logger.error("Could not determine task model for tags. Aborting.")
                return None
            
            payload = {
                "model": task_model,
                "messages": messages,
                "stream": False
            }
            
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/tasks/tags/completions",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the tag content (usually JSON)
            try:
                import json
                tag_data = json.loads(content)
                return tag_data.get("tags", [])
            except json.JSONDecodeError:
                # Try to extract tags from plain text
                return content.split(",") if content else []
                
        except Exception as e:
            logger.error(f"Failed to generate tags: {e}")
            return None
    
    def _get_title(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a title for the conversation."""
        try:
            # Get task model for title generation
            task_model = self.base_client._get_task_model()
            if not task_model:
                logger.error("Could not determine task model for title. Aborting.")
                return None
            
            payload = {
                "model": task_model,
                "messages": messages,
                "stream": False
            }
            
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/tasks/title/completions",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the title content (usually JSON)
            try:
                import json
                title_data = json.loads(content)
                return title_data.get("title", content.strip())
            except json.JSONDecodeError:
                return content.strip() if content else None
                
        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            return None
    
    def _get_chat_details(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a chat."""
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/chats/{chat_id}",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
            return None

    # Folder management methods
    def get_folder_id_by_name(self, folder_name: str) -> Optional[str]:
        """Get folder ID by name."""
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/folders/",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            folders = response.json()
            for folder in folders:
                if folder.get("name") == folder_name:
                    return folder.get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to get folder ID for '{folder_name}': {e}")
            return None

    def create_folder(self, name: str) -> Optional[str]:
        """Create a new folder."""
        logger.info(f"Creating folder '{name}'...")
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/folders/",
                json={"name": name},
                headers=self.base_client.json_headers,
            )
            response.raise_for_status()
            folder_data = response.json()
            folder_id = folder_data.get("id")
            if folder_id:
                logger.info(f"Successfully created folder '{name}' with ID: {folder_id}")
                return folder_id
            else:
                logger.error("Folder creation response did not contain an ID.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    def move_chat_to_folder(self, chat_id: str, folder_id: str):
        """Move chat to a folder."""
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/chats/{chat_id}/folder",
                json={"folder_id": folder_id},
                headers=self.base_client.json_headers,
            )
            response.raise_for_status()
            logger.info(f"Successfully moved chat {chat_id[:8]}... to folder {folder_id}")
            # Update local chat object
            if self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["folder_id"] = folder_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to move chat to folder: {e}")

    def set_chat_tags(self, chat_id: str, tags: List[str]):
        """Set tags for a chat conversation."""
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/chats/{chat_id}/tags",
                json={"tags": tags},
                headers=self.base_client.json_headers,
            )
            response.raise_for_status()
            logger.info(f"Successfully set tags for chat {chat_id[:8]}...: {tags}")
            # Update local chat object
            if self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["tags"] = tags
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to set chat tags: {e}")

    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """Rename an existing chat."""
        try:
            response = self.base_client.session.post(  # Changed from PUT to POST
                f"{self.base_client.base_url}/api/v1/chats/{chat_id}",
                json={"title": new_title},
                headers=self.base_client.json_headers,
            )
            response.raise_for_status()
            logger.info(f"Successfully renamed chat {chat_id[:8]}... to '{new_title}'")
            # Update local chat object
            if self.base_client.chat_object_from_server:
                self.base_client.chat_object_from_server["title"] = new_title
                if "chat" in self.base_client.chat_object_from_server:
                    self.base_client.chat_object_from_server["chat"]["title"] = new_title
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to rename chat {chat_id}: {e}")
            return False