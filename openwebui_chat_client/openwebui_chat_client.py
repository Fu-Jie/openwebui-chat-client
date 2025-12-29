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
import re
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
from .modules.prompts_manager import PromptsManager
from .modules.user_manager import UserManager

logger = logging.getLogger(__name__)


class OpenWebUIClient:
    """
    An intelligent, stateful Python client for the Open WebUI API.
    Supports single/multi-model chats, tagging, and RAG with both
    direct file uploads and knowledge base collections, matching the backend format.

    This refactored version uses a modular architecture with specialized managers
    while maintaining 100% backward compatibility with the original API.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        default_model_id: str,
        skip_model_refresh: bool = False,
    ):
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

        # Set parent reference so managers can access main client methods
        self._base_client._parent_client = self

        # Initialize specialized managers
        self._model_manager = ModelManager(
            self._base_client, skip_initial_refresh=skip_model_refresh
        )
        self._notes_manager = NotesManager(self._base_client)
        self._knowledge_base_manager = KnowledgeBaseManager(self._base_client)
        self._file_manager = FileManager(self._base_client)
        self._chat_manager = ChatManager(self._base_client)
        self._prompts_manager = PromptsManager(self._base_client)
        self._user_manager = UserManager(self._base_client)

        # Set up available model IDs from model manager
        self._base_client.available_model_ids = self._model_manager.available_model_ids

        # For backward compatibility, expose base client properties as dynamic properties

    @property
    def base_url(self):
        return self._base_client.base_url

    @property
    def default_model_id(self):
        return self._base_client.default_model_id

    @property
    def session(self):
        return self._base_client.session

    @session.setter
    def session(self, value):
        self._base_client.session = value

    @property
    def json_headers(self):
        return self._base_client.json_headers

    @property
    def chat_id(self):
        return self._base_client.chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._base_client.chat_id = value

    @property
    def chat_object_from_server(self):
        return self._base_client.chat_object_from_server

    @chat_object_from_server.setter
    def chat_object_from_server(self, value):
        self._base_client.chat_object_from_server = value

    @property
    def model_id(self):
        return self._base_client.model_id

    @model_id.setter
    def model_id(self, value):
        self._base_client.model_id = value

    @property
    def task_model(self):
        return self._base_client.task_model

    @task_model.setter
    def task_model(self, value):
        self._base_client.task_model = value

    @property
    def _auto_cleanup_enabled(self):
        return self._base_client._auto_cleanup_enabled

    @_auto_cleanup_enabled.setter
    def _auto_cleanup_enabled(self, value):
        self._base_client._auto_cleanup_enabled = value

    @property
    def _first_stream_request(self):
        return self._base_client._first_stream_request

    @_first_stream_request.setter
    def _first_stream_request(self, value):
        self._base_client._first_stream_request = value

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
        if (
            hasattr(self, "_base_client")
            and self._base_client
            and self._base_client._auto_cleanup_enabled
            and self.chat_id
            and self.chat_object_from_server
        ):
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
            question,
            chat_title,
            model_id,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_follow_up,
            enable_auto_tagging,
            enable_auto_titling,
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
            question,
            chat_title,
            model_ids,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_follow_up,
            enable_auto_tagging,
            enable_auto_titling,
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
        cleanup_placeholder_messages: bool = False,  # New: Clean up placeholder messages
        placeholder_pool_size: int = 30,  # New: Size of placeholder message pool (configurable)
        min_available_messages: int = 10,  # New: Minimum available messages threshold
        wait_before_request: float = 10.0,  # New: Wait time after initializing placeholders (seconds)
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Generator[str, None, Optional[Dict[str, Any]]]:
        """
        Initiates a streaming chat session. Yields content chunks as they are received.
        At the end of the stream, returns the full response content, sources, and follow-up suggestions.
        """
        return self._chat_manager.stream_chat(
            question,
            chat_title,
            model_id,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_follow_up,
            cleanup_placeholder_messages,
            placeholder_pool_size,
            min_available_messages,
            wait_before_request,
            enable_auto_tagging,
            enable_auto_titling,
        )

    def continuous_chat(
        self,
        initial_question: str,
        num_questions: int,
        chat_title: str,
        model_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Perform continuous conversation with automatic follow-up questions."""
        return self._chat_manager.continuous_chat(
            initial_question,
            num_questions,
            chat_title,
            model_id,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_auto_tagging,
            enable_auto_titling,
        )

    def continuous_parallel_chat(
        self,
        initial_question: str,
        num_questions: int,
        chat_title: str,
        model_ids: List[str],
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Perform continuous conversation with multiple models in parallel."""
        return self._chat_manager.continuous_parallel_chat(
            initial_question,
            num_questions,
            chat_title,
            model_ids,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_auto_tagging,
            enable_auto_titling,
        )

    def continuous_stream_chat(
        self,
        initial_question: str,
        num_questions: int,
        chat_title: str,
        model_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """Perform continuous conversation with streaming responses."""
        return self._chat_manager.continuous_stream_chat(
            initial_question,
            num_questions,
            chat_title,
            model_id,
            folder_name,
            image_paths,
            tags,
            rag_files,
            rag_collections,
            tool_ids,
            enable_auto_tagging,
            enable_auto_titling,
        )

    def deep_research(
        self,
        topic: str,
        chat_title: Optional[str] = None,
        num_steps: int = 3,
        general_models: Optional[List[str]] = None,
        search_models: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Performs an advanced, autonomous, multi-step research process on a given topic
        using intelligent model routing.

        The agent will iteratively plan questions and decide which type of model to use
        (general vs. search-capable), with the entire process being visible as a
        multi-turn chat in the UI.

        Args:
            topic: The topic to be researched.
            chat_title: Optional title for the research chat. If not provided,
                        it will be generated from the topic.
            num_steps: The number of research steps (plan -> execute cycles).
            general_models: A list of model IDs for general reasoning and summarization.
                            If not provided, the client's default model will be used.
            search_models: A list of model IDs with search capabilities. If not provided,
                           the agent will not have the option to use a search model.

        Returns:
            A dictionary containing the research results and chat information, or None if it fails.
        """
        logger.info("=" * 80)
        logger.info(
            f"🚀 Starting Deep Research on topic: '{topic}' for {num_steps} steps."
        )
        logger.info("=" * 80)

        # If no chat title is provided, create one from the topic
        final_chat_title = chat_title or f"Deep Dive: {topic}"

        # Ensure there's at least one general model to use
        if not general_models:
            general_models = [self._base_client.default_model_id]
            logger.warning(
                f"No general_models provided. Falling back to default model: {general_models[0]}"
            )

        if not search_models:
            search_models = []  # Ensure it's a list

        research_history = []

        for i in range(1, num_steps + 1):
            step_result = self._chat_manager._perform_research_step(
                topic=topic,
                chat_title=final_chat_title,
                research_history=research_history,
                step_num=i,
                total_steps=num_steps,
                general_models=general_models,
                search_models=search_models,
            )

            if step_result:
                question, answer, model_used = step_result
                # Append a formatted summary of the step to the history
                research_history.append(
                    f"Step {i}: Asked '{question}' (using {model_used}) and received a detailed answer."
                )
            else:
                logger.error(f"Research step {i} failed. Halting the research process.")
                return None

        # --- Final Report Generation ---
        logger.info("=" * 80)
        logger.info("✍️ All research steps completed. Generating final report...")

        # Format the research history for the final prompt
        formatted_history = "\n\n".join(research_history)

        summary_prompt = (
            f"You are a research analyst. Your task is to synthesize the following research findings "
            f"into a comprehensive and well-structured report on the topic: '{topic}'.\n\n"
            f"## Research Log:\n{formatted_history}\n\n"
            f"Based on the information gathered, please generate the final report. "
            f"The report should be clear, concise, and cover the key findings from the research steps."
        )

        # Use the first general model for the final summarization
        summary_model = general_models[0]
        logger.info(f"Using model '{summary_model}' for final report generation.")

        final_report_result = self._chat_manager.chat(
            question=summary_prompt,
            chat_title=final_chat_title,
            model_id=summary_model,
        )

        if not final_report_result or not final_report_result.get("response"):
            logger.error("❌ Failed to generate the final report.")
            final_report = "Error: Could not generate the final report."
        else:
            final_report = final_report_result["response"]
            logger.info("✅ Final report generated successfully.")

        return {
            "topic": topic,
            "chat_id": self._base_client.chat_id,
            "chat_title": final_chat_title,
            "research_log": research_history,
            "final_report": final_report,
            "total_steps_completed": len(research_history),
        }

    def process_task(
        self,
        question: str,
        model_id: str,
        tool_server_ids: Union[str, List[str]],
        knowledge_base_name: Optional[str] = None,
        max_iterations: int = 25,
        summarize_history: bool = False,
        decision_model_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Processes a task using an AI model and a tool server in a multi-step process.

        Args:
            question: The task to process.
            model_id: The ID of the model to use for task execution.
            tool_server_ids: The ID(s) of the tool server(s) to use.
            knowledge_base_name: The name of the knowledge base to use.
            max_iterations: The maximum number of iterations to attempt.
            summarize_history: If True, the conversation history will be summarized.
            decision_model_id: Optional model ID for automatic decision-making when 
                              the AI presents multiple options. If provided, this model
                              will analyze the options and select the best one automatically,
                              eliminating the need for user input when choices arise.

        Returns:
            A dictionary containing:
                - solution: The final answer or error message
                - conversation_history: Either the full message list or a summarized string (if summarize_history=True)
                - todo_list: The last parsed to-do list from the agent's thought process
            Returns None if initialization fails.
        """
        return self._chat_manager.process_task(
            question=question,
            model_id=model_id,
            tool_server_ids=tool_server_ids,
            knowledge_base_name=knowledge_base_name,
            max_iterations=max_iterations,
            summarize_history=summarize_history,
            decision_model_id=decision_model_id,
        )

    def stream_process_task(
        self,
        question: str,
        model_id: str,
        tool_server_ids: Union[str, List[str]],
        knowledge_base_name: Optional[str] = None,
        max_iterations: int = 25,
        summarize_history: bool = False,
        decision_model_id: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """
        Processes a task in a streaming fashion, yielding results for each step.
        
        Args:
            question: The task to process.
            model_id: The ID of the model to use for task execution.
            tool_server_ids: The ID(s) of the tool server(s) to use.
            knowledge_base_name: The name of the knowledge base to use.
            max_iterations: The maximum number of iterations to attempt.
            summarize_history: If True, the conversation history will be summarized.
            decision_model_id: Optional model ID for automatic decision-making when 
                              the AI presents multiple options. If provided, this model
                              will analyze the options and select the best one automatically.
        """
        return self._chat_manager.stream_process_task(
            question=question,
            model_id=model_id,
            tool_server_ids=tool_server_ids,
            knowledge_base_name=knowledge_base_name,
            max_iterations=max_iterations,
            summarize_history=summarize_history,
            decision_model_id=decision_model_id,
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
        folder_name: Optional[str] = None,
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
        if (
            not regenerate_tags
            and not regenerate_title
            and title is None
            and tags is None
            and folder_name is None
        ):
            logger.warning(
                "No action requested for update_chat_metadata. Set regenerate_tags or regenerate_title to True, or provide title/tags/folder_name."
            )
            return None

        logger.info(f"Updating metadata for chat {chat_id[:8]}...")

        # For backward compatibility with the regenerate_ parameters, we need to implement the original behavior
        if regenerate_tags or regenerate_title:
            if not self._load_chat_details(chat_id):
                logger.error(f"Cannot update metadata, failed to load chat: {chat_id}")
                return None

            api_messages = self._build_linear_history_for_api(
                self.chat_object_from_server["chat"]
            )
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
            success = self._chat_manager.update_chat_metadata(
                chat_id, title, tags, folder_name
            )
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

    def delete_all_chats(self) -> bool:
        """
        Delete ALL chat conversations for the current user.

        ⚠️ WARNING: This is a DESTRUCTIVE operation!
        This method will permanently delete ALL chats associated with the current user account.
        This action CANNOT be undone. Use with extreme caution.

        This method is useful for:
        - Cleaning up test data after integration tests
        - Resetting an account to a clean state
        - Bulk cleanup operations

        Returns:
            True if deletion was successful, False otherwise

        Example:
            >>> # ⚠️ WARNING: This will delete ALL your chats!
            >>> success = client.delete_all_chats()
            >>> if success:
            ...     print("All chats have been permanently deleted")
        """
        return self._chat_manager.delete_all_chats()

    def create_folder(self, name: str) -> Optional[str]:
        """Create a new folder for organizing chats."""
        return self._chat_manager.create_folder(name)

    def get_folder_id_by_name(
        self, name: str, suppress_log: bool = False
    ) -> Optional[str]:
        """Get folder ID by folder name."""
        return self._chat_manager.get_folder_id_by_name(name)

    def move_chat_to_folder(self, chat_id: str, folder_id: str):
        """Move a chat to a specific folder."""
        return self._chat_manager.move_chat_to_folder(chat_id, folder_id)

    # =============================================================================
    # MODEL MANAGEMENT - Delegate to ModelManager
    # =============================================================================

    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all available models for the user, including base models and user-created custom models. Excludes disabled base models. This corresponds to the model list shown in the top left of the chat page.
        """
        return self._model_manager.list_models()

    def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all base models that can be used to create variants. Includes disabled base models.
        Corresponds to the model list in the admin settings page, including PIPE type models.
        """
        return self._model_manager.list_base_models()

    def list_custom_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists custom models that users can use or have created (not base models).
        A list of custom models available in the user's workspace.
        """
        return self._model_manager.list_custom_models()

    def list_groups(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available groups from the Open WebUI instance."""
        return self._model_manager.list_groups()

    def _build_access_control(
        self,
        permission_type: str,
        group_identifiers: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
    ) -> Union[Dict[str, Any], None, bool]:
        """Build access control structure for model permissions."""
        if permission_type == "public":
            return None

        if permission_type == "private":
            return {
                "read": {"group_ids": [], "user_ids": user_ids or []},
                "write": {"group_ids": [], "user_ids": user_ids or []},
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
                "write": {"group_ids": group_ids, "user_ids": user_ids or []},
            }

        logger.error(f"Invalid permission type: {permission_type}")
        return False

    def _resolve_group_ids(
        self, group_identifiers: List[str]
    ) -> Union[List[str], bool]:
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
        Creates a new model configuration with detailed metadata. This method
        delegates directly to the ModelManager.
        """
        return self._model_manager.create_model(
            model_id=model_id,
            name=name,
            base_model_id=base_model_id,
            description=description,
            params=params,
            permission_type=permission_type,
            group_identifiers=group_identifiers,
            user_ids=user_ids,
            profile_image_url=profile_image_url,
            suggestion_prompts=suggestion_prompts,
            tags=tags,
            capabilities=capabilities,
            is_active=is_active,
        )

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
        Updates an existing model configuration with detailed metadata. This method
        delegates directly to the ModelManager.
        """
        return self._model_manager.update_model(
            model_id=model_id,
            name=name,
            base_model_id=base_model_id,
            description=description,
            params=params,
            permission_type=permission_type,
            group_identifiers=group_identifiers,
            user_ids=user_ids,
            profile_image_url=profile_image_url,
            suggestion_prompts=suggestion_prompts,
            tags=tags,
            capabilities=capabilities,
            is_active=is_active,
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
            logger.error(
                f"Invalid permission_type '{permission_type}'. Must be 'public', 'private', or 'group'."
            )
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
                    model
                    for model in all_models
                    if model_keyword.lower() in model.get("id", "").lower()
                    or model_keyword.lower() in model.get("name", "").lower()
                ]
                logger.info(
                    f"Found {len(models_to_update)} models matching keyword '{model_keyword}'"
                )
        else:
            # Original signature with models parameter
            if models is None:
                logger.error(
                    "Either models, model_identifiers, or model_keyword must be provided"
                )
                return {"success": [], "failed": [], "skipped": []}
            models_to_update = models

        if not models_to_update:
            logger.warning("No models found to update.")
            return {"success": [], "failed": [], "skipped": []}

        # Prepare access control configuration
        access_control = self._build_access_control(
            permission_type, group_identifiers, user_ids
        )
        if access_control is False:  # Error occurred
            return {"success": [], "failed": [], "skipped": []}

        # Batch update using ThreadPoolExecutor
        results = {"success": [], "failed": [], "skipped": []}

        def update_single_model(model: Dict[str, Any]) -> Tuple[str, bool, str]:
            """Update a single model's permissions."""
            model_id = model.get("id", "")
            try:
                updated_model = self.update_model(
                    model_id, access_control=access_control
                )
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
                        logger.info(
                            f"✅ Successfully updated permissions for model '{model_id}'"
                        )
                    else:
                        results["failed"].append(
                            {"model_id": model_id, "error": message}
                        )
                        logger.error(
                            f"❌ Failed to update permissions for model '{model_id}': {message}"
                        )
                except Exception as e:
                    results["failed"].append({"model_id": model_id, "error": str(e)})
                    logger.error(
                        f"❌ Exception processing result for model '{model_id}': {e}"
                    )

        logger.info(
            f"Batch update completed: {len(results['success'])} successful, {len(results['failed'])} failed"
        )
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
        access_control: Optional[Dict[str, Any]] = None,
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
        access_control: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing note by its ID."""
        return self._notes_manager.update_note_by_id(
            note_id, title, data, meta, access_control
        )

    def delete_note_by_id(self, note_id: str) -> bool:
        """Delete a note by its ID."""
        return self._notes_manager.delete_note_by_id(note_id)

    # =============================================================================
    # PROMPTS API - Delegate to PromptsManager
    # =============================================================================

    def get_prompts(self) -> Optional[List[Dict[str, Any]]]:
        """Get all prompts for the current user."""
        return self._prompts_manager.get_prompts()

    def get_prompts_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get a detailed list of prompts with user information."""
        return self._prompts_manager.get_prompts_list()

    def create_prompt(
        self,
        command: str,
        title: str,
        content: str,
        access_control: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new prompt."""
        return self._prompts_manager.create_prompt(
            command, title, content, access_control
        )

    def get_prompt_by_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by its command."""
        return self._prompts_manager.get_prompt_by_command(command)

    def update_prompt_by_command(
        self,
        command: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        access_control: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing prompt by its command (title/content only)."""
        return self._prompts_manager.update_prompt_by_command(
            command, title, content, access_control
        )

    def replace_prompt_by_command(
        self,
        old_command: str,
        new_command: str,
        title: str,
        content: str,
        access_control: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Replace a prompt completely including command (delete + recreate)."""
        return self._prompts_manager.replace_prompt_by_command(
            old_command, new_command, title, content, access_control
        )

    def delete_prompt_by_command(self, command: str) -> bool:
        """Delete a prompt by its command."""
        return self._prompts_manager.delete_prompt_by_command(command)

    def search_prompts(
        self,
        query: Optional[str] = None,
        by_command: bool = False,
        by_title: bool = True,
        by_content: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search prompts by various criteria."""
        return self._prompts_manager.search_prompts(
            query, by_command, by_title, by_content
        )

    def extract_variables(self, content: str) -> List[str]:
        """Extract variable names from prompt content."""
        return self._prompts_manager.extract_variables(content)

    def substitute_variables(
        self,
        content: str,
        variables: Dict[str, Any],
        system_variables: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Substitute variables in prompt content."""
        return self._prompts_manager.substitute_variables(
            content, variables, system_variables
        )

    def get_system_variables(self) -> Dict[str, Any]:
        """Get current system variables for substitution."""
        return self._prompts_manager.get_system_variables()

    def batch_create_prompts(
        self, prompts_data: List[Dict[str, Any]], continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """Create multiple prompts in batch."""
        return self._prompts_manager.batch_create_prompts(
            prompts_data, continue_on_error
        )

    def batch_delete_prompts(
        self, commands: List[str], continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """Delete multiple prompts by their commands."""
        return self._prompts_manager.batch_delete_prompts(commands, continue_on_error)

    # =============================================================================
    # USER MANAGEMENT - Delegate to UserManager
    # =============================================================================

    def get_users(
        self, skip: int = 0, limit: int = 50
    ) -> Optional[List[Dict[str, Any]]]:
        """Get a list of all users."""
        return self._user_manager.get_users(skip, limit)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by their ID."""
        return self._user_manager.get_user_by_id(user_id)

    def update_user_role(self, user_id: str, role: str) -> bool:
        """Update a user's role (admin/user)."""
        return self._user_manager.update_user_role(user_id, role)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self._user_manager.delete_user(user_id)

    # =============================================================================
    # FILE OPERATIONS - Delegate to FileManager
    # =============================================================================

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file and return the file metadata."""
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
        dry_run: bool = False,
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
        logger.info(
            f"Starting bulk archive operation for chats older than {days_since_update} days"
        )
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
            "errors": [],
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
                            logger.warning(
                                f"Failed to get details for chat {chat_basic['id']}: {e}"
                            )

            results["total_checked"] = len(target_chats)
            logger.info(f"Found {len(target_chats)} chats to check for archiving")

            # Filter by age and archive
            chats_to_archive = []
            for chat in target_chats:
                updated_at = chat.get("updated_at", 0)
                if updated_at < cutoff_timestamp:
                    chats_to_archive.append(chat)

            logger.info(
                f"Found {len(chats_to_archive)} chats older than {days_since_update} days"
            )

            if dry_run:
                logger.info("Dry run mode: would archive the following chats:")
                for chat in chats_to_archive:
                    logger.info(
                        f"  - {chat.get('title', 'Unknown')} (ID: {chat['id']})"
                    )
                results["total_archived"] = len(chats_to_archive)
                results["archived_chats"] = [
                    {
                        "id": chat["id"],
                        "title": chat.get("title", "Unknown"),
                        "updated_at": chat.get("updated_at", 0),
                    }
                    for chat in chats_to_archive
                ]
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
                            results["archived_chats"].append(
                                {
                                    "id": chat["id"],
                                    "title": chat.get("title", "Unknown"),
                                    "updated_at": chat.get("updated_at", 0),
                                }
                            )
                        else:
                            results["total_failed"] += 1
                            results["failed_chats"].append(
                                {
                                    "id": chat["id"],
                                    "title": chat.get("title", "Unknown"),
                                    "error": "Archive request failed",
                                }
                            )
                    except Exception as e:
                        results["total_failed"] += 1
                        results["failed_chats"].append(
                            {
                                "id": chat["id"],
                                "title": chat.get("title", "Unknown"),
                                "error": str(e),
                            }
                        )
                        logger.error(f"Error archiving chat {chat['id']}: {e}")

            logger.info(
                f"Archive operation completed: {results['total_archived']} archived, {results['total_failed']} failed"
            )
            return results

        except Exception as e:
            error_msg = f"Bulk archive operation failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def _is_placeholder_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is a placeholder (content is empty and not marked as done)"""
        return message.get("content", "").strip() == "" and not message.get(
            "done", False
        )

    def _find_or_create_chat_by_title(self, title: str):
        """Find an existing chat by title or create a new one."""
        logger.info(f"Finding or creating chat with title: '{title}'")

        # First, search for existing chat
        existing_chat = self._search_latest_chat_by_title(title)
        if existing_chat:
            chat_id = existing_chat["id"]
            logger.info(f"Found existing chat: {chat_id}")
            self.chat_id = chat_id
            # Also set on base client for ChatManager compatibility
            if hasattr(self, "_base_client"):
                self._base_client.chat_id = chat_id

            # Load chat details
            if self._load_chat_details(chat_id):
                logger.info(f"Successfully loaded existing chat: {chat_id}")
                return chat_id
            else:
                logger.warning(f"Failed to load details for existing chat: {chat_id}")

        # If no existing chat found or failed to load, create new one
        new_chat_id = self._create_new_chat(title)
        if new_chat_id:
            self.chat_id = new_chat_id
            # Also set on base client for ChatManager compatibility
            if hasattr(self, "_base_client"):
                self._base_client.chat_id = new_chat_id

            # Load the newly created chat details
            if self._load_chat_details(new_chat_id):
                logger.info(f"Successfully created and loaded new chat: {new_chat_id}")
                return new_chat_id
            else:
                logger.warning(
                    f"Created new chat {new_chat_id} but failed to load details"
                )
                return new_chat_id  # Still return the ID even if loading fails
        else:
            logger.error(f"Failed to create new chat with title: '{title}'")
            return None

    def _load_chat_details(self, chat_id: str) -> bool:
        """Load chat details from server."""
        logger.info(f"Loading chat details for: {chat_id}")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chats/{chat_id}",
                headers=self.json_headers,
            )
            response.raise_for_status()
            chat_data = response.json()

            # Check for None/empty response specifically
            if chat_data is None:
                logger.warning(
                    f"Empty/None response when loading chat details for {chat_id}"
                )
                return False

            if chat_data:
                self.chat_object_from_server = chat_data
                # Also set on base client for ChatManager compatibility
                if hasattr(self, "_base_client"):
                    self._base_client.chat_object_from_server = chat_data
                logger.info(f"Successfully loaded chat details for: {chat_id}")
                return True
            else:
                logger.warning(
                    f"Empty response when loading chat details for {chat_id}"
                )
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
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
            logger.info(
                f"Found latest chat with title '{title}': {latest_chat['id'][:8]}..."
            )
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
                f"{self.base_url}/api/v1/chats/{chat_id}", headers=self.json_headers
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
                        logger.error(
                            f"Failed to decode JSON from title content: {content}"
                        )
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
            logger.error(
                "Failed to parse JSON or find expected keys in title response."
            )
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
        logger.info(f'Processing question: "{question}"')
        chat_core = self.chat_object_from_server["chat"]
        chat_core["models"] = [self.model_id]

        # Ensure chat_core has the required history structure
        chat_core.setdefault("history", {"messages": {}, "currentId": None})

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
                self.chat_id, api_messages, api_rag_payload, self.model_id, tool_ids
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
            "models": [self.model_id],
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
            "model": self.model_id,
            "modelName": self.model_id.split(":")[0],
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
        chat_core["models"] = [self.model_id]
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

    def _extract_json_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from content that may be wrapped in markdown code blocks or have extra formatting.

        Args:
            content: The raw content string that may contain JSON

        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        if not content or not content.strip():
            return None

        # Try parsing the content as-is first (most common case)
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        # Look for JSON wrapped in markdown code blocks
        # Patterns: ```json\n{...}\n``` or ```\n{...}\n```
        code_block_patterns = [
            r"```json\s*\n(.*?)\n\s*```",  # ```json ... ```
            r"```\s*\n(.*?)\n\s*```",  # ``` ... ```
            r"`(.*?)`",  # `...` (single backticks)
        ]

        for pattern in code_block_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # Try to find JSON-like content by looking for { ... } patterns
        json_patterns = [
            r"\{.*\}",  # Find any {...} block
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # If all parsing attempts fail, log the content for debugging
        logger.debug(f"Failed to extract JSON from content: {content[:200]}...")
        return None

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
                    # Use the robust JSON extraction method
                    content_json = self._extract_json_from_content(content)
                    if content_json:
                        follow_ups = content_json.get(
                            "follow_ups"
                        )  # Note: key is 'follow_ups' not 'followUps'
                        if isinstance(follow_ups, list):
                            logger.info(
                                f"   ✅ Received {len(follow_ups)} follow-up suggestions."
                            )
                            return follow_ups
                        else:
                            logger.warning(
                                f"follow_ups field is not a list: {type(follow_ups)}"
                            )
                    else:
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
            "parent_message": {},
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
        if not self.chat_id:
            raise ValueError("Chat ID not set. Initialize chat first.")

        logger.info(f'Processing STREAMING question: "{question}"')
        chat_core = self.chat_object_from_server["chat"]
        chat_core["models"] = [self.model_id]

        # 1. If cleanup of placeholder messages is needed, perform cleanup
        if cleanup_placeholder_messages:
            self._cleanup_unused_placeholder_messages()

        # 2. Ensure there are enough placeholder messages available
        self._ensure_placeholder_messages(placeholder_pool_size, min_available_messages)

        # 3. Get the next available placeholder message ID pair
        message_pair = self._get_next_available_message_pair()
        if not message_pair:
            logger.error(
                "No available placeholder message pairs after ensuring, cannot proceed with stream."
            )
            raise RuntimeError("No available placeholder message pairs.")

        user_message_id, assistant_message_id = message_pair

        # 4. Preparation for API call
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

        # --- Update local storage placeholder message content ---
        # Find the corresponding user and assistant message objects
        storage_user_message = chat_core["history"]["messages"][user_message_id]
        storage_assistant_message = chat_core["history"]["messages"][
            assistant_message_id
        ]

        # Update user message content and files
        storage_user_message["content"] = question
        storage_user_message["files"] = []  # Clear previous files and re-add
        if image_paths:
            for image_path in image_paths:
                base64_url = self._encode_image_to_base64(image_path)
                if base64_url:
                    storage_user_message["files"].append(
                        {"type": "image", "url": base64_url}
                    )
        storage_user_message["files"].extend(storage_rag_payloads)
        storage_user_message["models"] = [self.model_id]  # Ensure correct model ID

        # Ensure assistant message initial state is correct
        storage_assistant_message["content"] = ""
        storage_assistant_message["model"] = self.model_id
        storage_assistant_message["modelName"] = self.model_id.split(":")[0]
        storage_assistant_message["timestamp"] = int(time.time())
        storage_assistant_message["done"] = False
        storage_assistant_message["sources"] = []

        # 5. Update user message content via delta event to trigger UI update
        logger.info(f"📤 Updating user message content for {user_message_id[:8]}...")
        self._stream_delta_update(self.chat_id, user_message_id, question)

        # 6. Start streaming completion
        logger.info(
            f"🔄 Starting streaming completion for {assistant_message_id[:8]}..."
        )
        try:
            content_chunks = []
            sources = []

            for chunk_content in self._get_model_completion_stream(
                self.chat_id, api_messages, api_rag_payload, self.model_id, tool_ids
            ):
                if chunk_content is None:
                    continue
                if not isinstance(chunk_content, str):
                    chunk_content = str(chunk_content)
                content_chunks.append(chunk_content)
                yield chunk_content

                # Update assistant message content incrementally
                storage_assistant_message["content"] = "".join(content_chunks)
                self._stream_delta_update(
                    self.chat_id,
                    assistant_message_id,
                    storage_assistant_message["content"],
                )

            # Final content assembly
            final_content = "".join(content_chunks)
            storage_assistant_message["content"] = final_content
            storage_assistant_message["done"] = True

            # Get follow-ups if requested
            follow_ups = None
            if enable_follow_up and final_content:
                temp_history_for_follow_up = api_messages + [
                    {"role": "assistant", "content": final_content}
                ]
                follow_ups = self._get_follow_up_completions(temp_history_for_follow_up)
                if follow_ups:
                    storage_assistant_message["followUps"] = follow_ups

            # Update chat core history
            chat_core["history"]["currentId"] = assistant_message_id
            chat_core["messages"] = self._build_linear_history_for_storage(
                chat_core, assistant_message_id
            )

            # Add RAG files to chat
            existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
            chat_core.setdefault("files", []).extend(
                [f for f in storage_rag_payloads if f["id"] not in existing_file_ids]
            )

            # Final update to remote
            if self._update_remote_chat():
                logger.info("✅ Streaming chat completed and saved successfully.")
            else:
                logger.warning("⚠️ Failed to save final streaming chat state.")

            return final_content, sources, follow_ups

        except Exception as e:
            logger.error(f"❌ Error during streaming: {e}")
            # Clean up on error
            storage_assistant_message["content"] = f"Error: {str(e)}"
            storage_assistant_message["done"] = True
            raise e

    def _ensure_placeholder_messages(self, pool_size: int, min_available: int) -> bool:
        """
        Ensures there are enough placeholder message pairs available for streaming.
        Creates placeholder pairs that form a proper multi-turn conversation chain.
        """
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.warning("No chat object available for placeholder message creation.")
            return False

        chat_core = self.chat_object_from_server["chat"]
        chat_core.setdefault("history", {"messages": {}, "currentId": None})

        # Count available placeholder pairs
        available_pairs = self._count_available_placeholder_pairs()
        logger.info(f"🔍 Found {available_pairs} available placeholder message pairs.")

        if available_pairs >= min_available:
            logger.info(
                f"✅ Sufficient placeholder pairs available ({available_pairs} >= {min_available})."
            )
            return True

        # Create more placeholder pairs as a connected conversation chain
        pairs_to_create = pool_size - available_pairs
        logger.info(
            f"🔧 Creating {pairs_to_create} new placeholder message pairs as a conversation chain..."
        )

        # Find the last message in the current conversation to continue the chain
        messages = chat_core["history"]["messages"]
        last_message_id = None

        # Find the current end of the conversation chain
        if chat_core["history"].get("currentId"):
            last_message_id = chat_core["history"]["currentId"]
        else:
            # Find the last non-placeholder message
            for msg_id, msg in messages.items():
                if not msg.get("_is_placeholder") and not msg.get("childrenIds"):
                    last_message_id = msg_id
                    break

        # Create connected conversation pairs
        parent_id = last_message_id
        for i in range(pairs_to_create):
            user_id = str(uuid.uuid4())
            assistant_id = str(uuid.uuid4())

            # Create placeholder user message
            user_message = {
                "id": user_id,
                "parentId": parent_id,  # Connect to previous message in conversation
                "childrenIds": [assistant_id],
                "role": "user",
                "content": "PLACEHOLDER_USER_MESSAGE",
                "files": [],
                "models": [self.model_id],
                "timestamp": int(time.time()),
                "_is_placeholder": True,
                "_is_available": True,
            }

            # Create placeholder assistant message
            assistant_message = {
                "id": assistant_id,
                "parentId": user_id,
                "childrenIds": [],
                "role": "assistant",
                "content": "",
                "model": self.model_id,
                "modelName": self.model_id.split(":")[0],
                "timestamp": int(time.time()),
                "done": False,
                "sources": [],
                "_is_placeholder": True,
                "_is_available": True,
            }

            # Update parent message to point to this user message
            if parent_id and parent_id in messages:
                if "childrenIds" not in messages[parent_id]:
                    messages[parent_id]["childrenIds"] = []
                messages[parent_id]["childrenIds"].append(user_id)

            # Add to history
            messages[user_id] = user_message
            messages[assistant_id] = assistant_message

            # Set up for next iteration - assistant becomes parent for next user message
            parent_id = assistant_id

        # Update the outer messages array and currentId for proper storage
        if messages:
            # Find the last assistant message to set as currentId
            last_assistant_id = None
            for msg_id, msg in messages.items():
                if msg.get("role") == "assistant" and not msg.get("childrenIds"):
                    last_assistant_id = msg_id
                    break

            if last_assistant_id:
                chat_core["history"]["currentId"] = last_assistant_id
                # Update the linear messages array
                chat_core["messages"] = self._build_linear_history_for_storage(
                    chat_core, last_assistant_id
                )

        logger.info(
            f"✅ Created {pairs_to_create} placeholder message pairs in conversation chain."
        )
        return True

    def _count_available_placeholder_pairs(self) -> int:
        """Count the number of available placeholder message pairs."""
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            return 0

        messages = (
            self.chat_object_from_server["chat"].get("history", {}).get("messages", {})
        )
        available_pairs = 0

        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):
                # Check if corresponding assistant message is also available
                children = message.get("childrenIds", [])
                if children:
                    assistant_message = messages.get(children[0])
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        available_pairs += 1

        return available_pairs

    def _get_next_available_message_pair(self) -> Optional[Tuple[str, str]]:
        """Get the next available placeholder message pair."""
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            return None

        messages = (
            self.chat_object_from_server["chat"].get("history", {}).get("messages", {})
        )

        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):
                children = message.get("childrenIds", [])
                if children:
                    assistant_id = children[0]
                    assistant_message = messages.get(assistant_id)
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        # Mark as used
                        message["_is_available"] = False
                        assistant_message["_is_available"] = False
                        return message["id"], assistant_id

        return None

    def _cleanup_unused_placeholder_messages(self) -> int:
        """Remove unused placeholder message pairs."""
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            return 0

        chat_core = self.chat_object_from_server["chat"]
        messages = chat_core.get("history", {}).get("messages", {})
        cleaned_count = 0

        # Find placeholder pairs that are still available (unused)
        pairs_to_remove = []
        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):
                children = message.get("childrenIds", [])
                if children:
                    assistant_id = children[0]
                    assistant_message = messages.get(assistant_id)
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        pairs_to_remove.append((message["id"], assistant_id))

        # Remove the pairs
        for user_id, assistant_id in pairs_to_remove:
            if user_id in messages:
                del messages[user_id]
                cleaned_count += 1
            if assistant_id in messages:
                del messages[assistant_id]

        if cleaned_count > 0:
            logger.info(
                f"🧹 Cleaned up {cleaned_count} unused placeholder message pairs."
            )

        return cleaned_count

    def _stream_delta_update(
        self, chat_id: str, message_id: str, delta_content: str
    ) -> None:
        """
        Push incremental content in real-time to the specified message of the specified chat to achieve a typewriter effect.
        Use asynchronous execution to avoid blocking the main process.

        Args:
            chat_id: Chat ID
            message_id: Message ID
            delta_content: Incremental content
        """
        if not delta_content.strip():  # Skip empty content
            return

        def _send_delta_update():
            """Internal function for asynchronous real-time updates"""
            url = f"{self.base_url}/api/v1/chats/{chat_id}/messages/{message_id}/event"
            payload = {"type": "chat:message:delta", "data": {"content": delta_content}}

            try:
                # Use a longer timeout to ensure the request can complete
                response = self.session.post(
                    url,
                    json=payload,
                    headers=self.json_headers,
                    timeout=3.0,  # 3 second timeout
                )
                response.raise_for_status()
                logger.debug(
                    f"✅ Delta update sent successfully for message {message_id[:8]}..."
                )
            except Exception as e:
                # Silently handle errors without affecting the main process
                logger.debug(
                    f"⚠️ Delta update failed for message {message_id[:8]}...: {e}"
                )

        # Use ThreadPoolExecutor for asynchronous execution to avoid blocking the main process
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(_send_delta_update)

    def _get_model_completion_stream(
        self,
        chat_id: str,
        messages: List[Dict[str, Any]],
        api_rag_payload: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Generator[str, None, List]:
        """Get streaming completion from a model.

        Yields content chunks, returns a list (sources) at the end.
        """
        active_model_id = model_id or self.model_id
        payload = {
            "model": active_model_id,
            "messages": messages,
            "stream": True,  # Enable streaming
            "parent_message": {},
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

    def _handle_rag_references(
        self, rag_files: Optional[List[str]], rag_collections: Optional[List[str]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Handle RAG file and collection references."""
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
                            {"type": "collection", "collection": kb_details, **kb_details}
                        )
                    else:
                        logger.warning(
                            f"Could not get details for knowledge base '{kb_name}', it will be skipped."
                        )
                else:
                    logger.warning(
                        f"Could not find knowledge base '{kb_name}', it will be skipped."
                    )
        return api_payload, storage_payload

    def _get_task_model(self) -> Optional[str]:
        """Get the task model for metadata operations."""
        # Return cached task model if available
        if hasattr(self, "task_model") and self.task_model:
            return self.task_model

        # Fetch task model from config
        url = f"{self.base_url}/api/v1/tasks/config"
        try:
            response = self.session.get(url, headers=self.json_headers)
            response.raise_for_status()
            config = response.json()
            task_model = config.get("TASK_MODEL")
            if task_model:
                logger.info(f"   ✅ Found task model: {task_model}")
                self.task_model = task_model
                return task_model
            else:
                logger.error("   ❌ 'TASK_MODEL' not found in config response.")
                return self.model_id  # Fallback to default model
        except Exception as e:
            logger.error(f"Failed to fetch task config: {e}")
            return self.model_id  # Fallback to default model
