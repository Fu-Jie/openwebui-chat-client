import requests
import json
import uuid
import time
import base64
import os
import logging
from typing import Optional, List, Tuple, Dict, Any, Union, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

# It is recommended to configure logging at the beginning of your main program
# to see detailed output from the client.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenWebUIClient:
    """
    An intelligent, stateful Python client for the Open WebUI API.
    Supports single/multi-model chats, tagging, and RAG with both
    direct file uploads and knowledge base collections, matching the backend format.
    """

    def __init__(self, base_url: str, token: str, default_model_id: str):
        self.base_url = base_url
        self.default_model_id = default_model_id
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.json_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.chat_id: Optional[str] = None
        self.chat_object_from_server: Optional[Dict[str, Any]] = None
        self.model_id: str = default_model_id
        self.task_model: Optional[str] = None
        self.available_model_ids: List[str] = self.list_models() or []
        self._auto_cleanup_enabled: bool = (
            True  # Controls whether to auto-cleanup placeholder messages
        )
        self._first_stream_request: bool = (
            True  # Tracks if this is the first streaming request
        )

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
        self.model_id = model_id or self.default_model_id
        logger.info("=" * 60)
        logger.info(
            f"Processing SINGLE-MODEL request: title='{chat_title}', model='{self.model_id}'"
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

        if not self.chat_object_from_server or "chat" not in self.chat_object_from_server:
            logger.error("Chat object not loaded or malformed, cannot proceed with chat.")
            return None

        # Handle model switching for an existing chat
        if model_id and self.model_id != model_id:
            logger.warning(f"Model switch detected for chat '{chat_title}'.")
            logger.warning(f"  > Changing from: '{self.model_id}'")
            logger.warning(f"  > Changing to:   '{model_id}'")
            self.model_id = model_id
            if self.chat_object_from_server and "chat" in self.chat_object_from_server:
                self.chat_object_from_server["chat"]["models"] = [model_id]

        if not self.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return None
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(
                folder_name
            )
            if folder_id and self.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.chat_id, folder_id)

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
                self.set_chat_tags(self.chat_id, tags)

            # New auto-tagging and auto-titling logic
            api_messages_for_tasks = self._build_linear_history_for_api(
                self.chat_object_from_server["chat"]
            )
            
            return_data = {
                "response": response,
                "chat_id": self.chat_id,
                "message_id": message_id,
            }

            if enable_auto_tagging:
                suggested_tags = self._get_tags(api_messages_for_tasks)
                if suggested_tags:
                    self.set_chat_tags(self.chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags

            if enable_auto_titling and len(
                self.chat_object_from_server["chat"]["history"]["messages"]
            ) <= 2:
                suggested_title = self._get_title(api_messages_for_tasks)
                if suggested_title:
                    self.rename_chat(self.chat_id, suggested_title)
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
        if not model_ids:
            logger.error("`model_ids` list cannot be empty for parallel chat.")
            return None
        self.model_id = model_ids[0]
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

        if not self.chat_object_from_server or "chat" not in self.chat_object_from_server:
            logger.error(
                "Chat object not loaded or malformed, cannot proceed with parallel chat."
            )
            return None

        # Handle model set changes for existing parallel chats
        if self.chat_object_from_server and "chat" in self.chat_object_from_server:
            current_models = self.chat_object_from_server["chat"].get("models", [])
            if set(current_models) != set(model_ids):
                logger.warning(f"Parallel model set changed for chat '{chat_title}'.")
                logger.warning(f"  > From: {current_models}")
                logger.warning(f"  > To:   {model_ids}")
                self.model_id = model_ids[0]
                self.chat_object_from_server["chat"]["models"] = model_ids

        if not self.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return None
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(
                folder_name
            )
            if folder_id and self.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.chat_id, folder_id)

        chat_core = self.chat_object_from_server["chat"]
        api_rag_payload, storage_rag_payloads = self._handle_rag_references(
            rag_files, rag_collections
        )
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
            "models": model_ids,
            "timestamp": int(time.time()),
        }
        if image_paths:
            for path in image_paths:
                url = self._encode_image_to_base64(path)
                if url:
                    storage_user_message["files"].append({"type": "image", "url": url})
        storage_user_message["files"].extend(storage_rag_payloads)
        chat_core["history"]["messages"][user_message_id] = storage_user_message
        if last_message_id:
            chat_core["history"]["messages"][last_message_id]["childrenIds"].append(
                user_message_id
            )
        logger.info(f"Querying {len(model_ids)} models in parallel...")
        responses: Dict[str, Dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=len(model_ids)) as executor:
            future_to_model = {
                executor.submit(
                    self._get_single_model_response_in_parallel,
                    chat_core,
                    model_id,
                    question,
                    image_paths,
                    api_rag_payload,
                    tool_ids,
                    enable_follow_up,
                ): model_id
                for model_id in model_ids
            }
            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    content, sources, follow_ups = future.result()
                    responses[model_id] = {
                        "content": content,
                        "sources": sources,
                        "followUps": follow_ups,
                    }
                except Exception as exc:
                    logger.error(f"Model '{model_id}' generated an exception: {exc}")
                    responses[model_id] = {
                        "content": None,
                        "sources": [],
                        "followUps": None,
                    }

        successful_responses = {
            k: v for k, v in responses.items() if v.get("content") is not None
        }
        if not successful_responses:
            logger.error("All models failed to respond.")
            del chat_core["history"]["messages"][user_message_id]
            return None
        logger.info("Received all responses.")
        assistant_message_ids = []
        for model_id, resp_data in successful_responses.items():
            assistant_id = str(uuid.uuid4())
            assistant_message_ids.append(assistant_id)
            storage_assistant_message = {
                "id": assistant_id,
                "parentId": user_message_id,
                "childrenIds": [],
                "role": "assistant",
                "content": resp_data["content"],
                "model": model_id,
                "modelName": model_id.split(":")[0],
                "timestamp": int(time.time()),
                "done": True,
                "sources": resp_data["sources"],
            }
            if "followUps" in resp_data:
                storage_assistant_message["followUps"] = resp_data["followUps"]
            chat_core["history"]["messages"][assistant_id] = storage_assistant_message

        chat_core["history"]["messages"][user_message_id][
            "childrenIds"
        ] = assistant_message_ids
        chat_core["history"]["currentId"] = assistant_message_ids[0]
        chat_core["models"] = model_ids
        chat_core["messages"] = self._build_linear_history_for_storage(
            chat_core, assistant_message_ids[0]
        )
        existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
        chat_core.setdefault("files", []).extend(
            [f for f in storage_rag_payloads if f["id"] not in existing_file_ids]
        )

        logger.info("Updating chat history on the backend...")
        logger.info("First update to save main responses...")
        if self._update_remote_chat():
            logger.info("Main responses saved successfully!")

            # This part is simplified because follow-ups are already in the message objects.
            # We just need to perform the final update if any follow-ups were generated.
            if any(
                r.get("followUps")
                for r in successful_responses.values()
                if r.get("followUps")
            ):
                logger.info("Updating chat again with follow-up suggestions...")
                if self._update_remote_chat():
                    logger.info("Follow-up suggestions saved successfully!")
                else:
                    logger.warning("Failed to save follow-up suggestions.")

            if tags:
                self.set_chat_tags(self.chat_id, tags)

            # Prepare a more detailed response object
            final_responses = {
                k: {"content": v["content"], "follow_ups": v.get("followUps")}
                for k, v in successful_responses.items()
            }

            return_data = {
                "responses": final_responses,
                "chat_id": self.chat_id,
                "message_ids": assistant_message_ids,
            }

            # Auto-tagging and auto-titling logic for parallel chat
            api_messages_for_tasks = self._build_linear_history_for_api(
                self.chat_object_from_server["chat"]
            )
            if enable_auto_tagging:
                suggested_tags = self._get_tags(api_messages_for_tasks)
                if suggested_tags:
                    self.set_chat_tags(self.chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags

            if enable_auto_titling and len(
                self.chat_object_from_server["chat"]["history"]["messages"]
            ) <= 2:
                suggested_title = self._get_title(api_messages_for_tasks)
                if suggested_title:
                    self.rename_chat(self.chat_id, suggested_title)
                    return_data["suggested_title"] = suggested_title
            
            return return_data

        return None

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
    ) -> Generator[
        str, None, Optional[Dict[str, Any]]
    ]:
        """
        Initiates a streaming chat session. Yields content chunks as they are received.
        At the end of the stream, returns the full response content, sources, and follow-up suggestions.
        """
        self.model_id = model_id or self.default_model_id
        logger.info("=" * 60)
        logger.info(
            f"Processing STREAMING request: title='{chat_title}', model='{self.model_id}'"
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

        if not self.chat_object_from_server or "chat" not in self.chat_object_from_server:
            logger.error("Chat object not loaded or malformed, cannot proceed with stream.")
            return  # End generator

        if not self.chat_id:
            logger.error("Chat initialization failed, cannot proceed with stream.")
            return  # Yield nothing, effectively end the generator

        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(
                folder_name
            )
            if folder_id and self.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.chat_id, folder_id)

        try:
            # 1. Ensure there are enough placeholder messages available
            self._ensure_placeholder_messages(
                placeholder_pool_size, min_available_messages
            )

            # 2. If this is the first streaming request and wait time is set, wait for specified seconds
            if self._first_stream_request and wait_before_request > 0:
                logger.info(
                    f"⏱️ First stream request: Waiting {wait_before_request} seconds before requesting AI response..."
                )
                time.sleep(wait_before_request)
                logger.info("⏱️ Wait completed, starting AI request...")
                self._first_stream_request = False  # Mark as not first request

            # 3. Call _ask_stream method, which now uses placeholder messages
            final_response_content, final_sources, follow_ups = (
                yield from self._ask_stream(
                    question,
                    image_paths,
                    rag_files,
                    rag_collections,
                    tool_ids,
                    enable_follow_up,
                    cleanup_placeholder_messages,
                    placeholder_pool_size,
                    min_available_messages,
                )
            )

            if tags:
                self.set_chat_tags(self.chat_id, tags)

            return_data = {
                "response": final_response_content,
                "sources": final_sources,
                "follow_ups": follow_ups,
            }

            # Auto-tagging and auto-titling logic for stream chat
            api_messages_for_tasks = self._build_linear_history_for_api(
                self.chat_object_from_server["chat"]
            )
            if enable_auto_tagging:
                suggested_tags = self._get_tags(api_messages_for_tasks)
                if suggested_tags:
                    self.set_chat_tags(self.chat_id, suggested_tags)
                    return_data["suggested_tags"] = suggested_tags

            if enable_auto_titling and len(
                self.chat_object_from_server["chat"]["history"]["messages"]
            ) <= 2:
                suggested_title = self._get_title(api_messages_for_tasks)
                if suggested_title:
                    self.rename_chat(self.chat_id, suggested_title)
                    return_data["suggested_title"] = suggested_title

            return return_data

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            raise  # Re-raise the exception for the caller

    def get_knowledge_base_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        logger.info(f"🔍 Searching for knowledge base '{name}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/list", headers=self.json_headers
            )
            response.raise_for_status()
            for kb in response.json():
                if kb.get("name") == name:
                    logger.info("   ✅ Found knowledge base.")
                    return kb
            logger.info(f"   ℹ️ Knowledge base '{name}' not found.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list knowledge bases: {e}")
            return None

    def create_knowledge_base(
        self, name: str, description: str = ""
    ) -> Optional[Dict[str, Any]]:
        logger.info(f"📁 Creating knowledge base '{name}'...")
        payload = {"name": name, "description": description}
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/knowledge/create",
                json=payload,
                headers=self.json_headers,
            )
            response.raise_for_status()
            kb_data = response.json()
            logger.info(
                f"   ✅ Knowledge base created successfully. ID: {kb_data.get('id')}"
            )
            return kb_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create knowledge base '{name}': {e}")
            return None

    def add_file_to_knowledge_base(
        self, file_path: str, knowledge_base_name: str
    ) -> bool:
        kb = self.get_knowledge_base_by_name(
            knowledge_base_name
        ) or self.create_knowledge_base(knowledge_base_name)
        if not kb:
            logger.error(
                f"Could not find or create knowledge base '{knowledge_base_name}'."
            )
            return False
        kb_id = kb.get("id")
        file_obj = self._upload_file(file_path)
        if not file_obj:
            logger.error(f"Failed to upload file '{file_path}' for knowledge base.")
            return False
        file_id = file_obj.get("id")
        logger.info(
            f"🔗 Adding file {file_id[:8]}... to knowledge base {kb_id[:8]} ('{knowledge_base_name}')..."
        )
        payload = {"file_id": file_id}
        try:
            self.session.post(
                f"{self.base_url}/api/v1/knowledge/{kb_id}/file/add",
                json=payload,
                headers=self.json_headers,
            ).raise_for_status()
            logger.info("   ✅ File add request sent successfully.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add file to knowledge base: {e}")
            return False

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        Deletes a knowledge base by its ID.
        """
        logger.info(f"🗑️ Deleting knowledge base with ID: {kb_id[:8]}...")
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/knowledge/{kb_id}/delete",
                headers=self.json_headers,
            )
            response.raise_for_status()
            if response.json() is True:
                logger.info(f"   ✅ Knowledge base {kb_id[:8]} deleted successfully.")
                return True
            else:
                logger.warning(
                    f"   ⚠️ Knowledge base {kb_id[:8]} deletion returned unexpected response: {response.text}"
                )
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Failed to delete knowledge base {kb_id[:8]}: {e}")
            return False

    def delete_all_knowledge_bases(self) -> Tuple[int, int]:
        """
        Deletes all knowledge bases.
        Returns a tuple of (successful_deletions, failed_deletions).
        """
        logger.info("🗑️ Deleting ALL knowledge bases...")
        successful_deletions = 0
        failed_deletions = 0
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/list", headers=self.json_headers
            )
            response.raise_for_status()
            knowledge_bases = response.json()
            if not knowledge_bases:
                logger.info("   ℹ️ No knowledge bases found to delete.")
                return 0, 0

            with ThreadPoolExecutor(max_workers=5) as executor:  # Limit concurrency
                futures = {
                    executor.submit(self.delete_knowledge_base, kb["id"]): kb["name"]
                    for kb in knowledge_bases
                }
                for future in as_completed(futures):
                    kb_name = futures[future]
                    try:
                        if future.result():
                            successful_deletions += 1
                        else:
                            failed_deletions += 1
                    except Exception as exc:
                        logger.error(
                            f"   ❌ Knowledge base '{kb_name}' generated an exception during deletion: {exc}"
                        )
                        failed_deletions += 1
            logger.info(
                f"   ✅ Finished deleting knowledge bases. Successful: {successful_deletions}, Failed: {failed_deletions}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"   ❌ Failed to retrieve knowledge bases for batch deletion: {e}"
            )
            return successful_deletions, failed_deletions
        return successful_deletions, failed_deletions

    def delete_knowledge_bases_by_keyword(
        self, keyword: str
    ) -> Tuple[int, int, List[str]]:
        """
        Deletes knowledge bases whose names contain the given keyword (case-insensitive).
        Returns a tuple of (successful_deletions, failed_deletions, names_deleted).
        """
        logger.info(f"🗑️ Deleting knowledge bases with keyword '{keyword}'...")
        successful_deletions = 0
        failed_deletions = 0
        names_deleted: List[str] = []
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/list", headers=self.json_headers
            )
            response.raise_for_status()
            knowledge_bases = response.json()

            kbs_to_delete = [
                kb
                for kb in knowledge_bases
                if keyword.lower() in kb.get("name", "").lower()
            ]

            if not kbs_to_delete:
                logger.info(
                    f"   ℹ️ No knowledge bases found matching keyword '{keyword}'."
                )
                return 0, 0, []

            with ThreadPoolExecutor(max_workers=5) as executor:  # Limit concurrency
                futures = {
                    executor.submit(self.delete_knowledge_base, kb["id"]): kb["name"]
                    for kb in kbs_to_delete
                }
                for future in as_completed(futures):
                    kb_name = futures[future]
                    try:
                        if future.result():
                            successful_deletions += 1
                            names_deleted.append(kb_name)
                        else:
                            failed_deletions += 1
                    except Exception as exc:
                        logger.error(
                            f"   ❌ Knowledge base '{kb_name}' generated an exception during deletion: {exc}"
                        )
                        failed_deletions += 1
            logger.info(
                f"   ✅ Finished deleting knowledge bases by keyword. Successful: {successful_deletions}, Failed: {failed_deletions}. Deleted: {names_deleted}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"   ❌ Failed to retrieve knowledge bases for keyword deletion: {e}"
            )
            return successful_deletions, failed_deletions, names_deleted
        return successful_deletions, failed_deletions, names_deleted

    def create_knowledge_bases_with_files(
        self, knowledge_base_files: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Creates multiple knowledge bases and adds specified files to each.

        Args:
            knowledge_base_files: A dictionary where keys are knowledge base names
                                  and values are lists of file paths to add to that KB.

        Returns:
            A dictionary with keys "success" (list of successfully created KB names)
            and "failed" (dict of {KB_name: error_message} for failed KBs).
        """
        logger.info("📁 Batch creating knowledge bases and adding files...")
        results: Dict[str, Any] = {"success": [], "failed": {}}

        def _process_single_kb(
            kb_name: str, file_paths: List[str]
        ) -> Tuple[str, bool, Optional[str]]:
            try:
                kb_data = self.create_knowledge_base(kb_name)
                if not kb_data:
                    return (
                        kb_name,
                        False,
                        f"Failed to create knowledge base '{kb_name}'.",
                    )

                kb_id = kb_data["id"]
                file_add_success_count = 0
                file_add_fail_count = 0

                for file_path in file_paths:
                    if self.add_file_to_knowledge_base(
                        file_path, kb_name
                    ):  # This method handles file upload internally
                        file_add_success_count += 1
                    else:
                        file_add_fail_count += 1

                if file_add_fail_count > 0:
                    return (
                        kb_name,
                        False,
                        f"KB created, but {file_add_fail_count}/{len(file_paths)} files failed to add.",
                    )
                return kb_name, True, None
            except Exception as e:
                return kb_name, False, str(e)

        with ThreadPoolExecutor(
            max_workers=5
        ) as executor:  # Limit concurrency for KB creation
            futures = {
                executor.submit(_process_single_kb, kb_name, file_paths): kb_name
                for kb_name, file_paths in knowledge_base_files.items()
            }

            for future in as_completed(futures):
                kb_name, success, error_msg = future.result()
                if success:
                    results["success"].append(kb_name)
                else:
                    results["failed"][kb_name] = error_msg or "Unknown error"

        logger.info(
            f"   ✅ Batch creation complete. Successful KBs: {len(results['success'])}, Failed KBs: {len(results['failed'])}"
        )
        return results

    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all available models for the user, including base models and user-created custom models.
        """
        logger.info("Listing all available models for the user...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/models", headers=self.json_headers
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
        """Lists all available base models that can be used to create variants."""
        logger.info("Listing all available base models...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/models/base", headers=self.json_headers
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
        Lists all custom models created by the user, excluding base models.
        """
        logger.info("Listing all custom models created by the user...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/models/custom", headers=self.json_headers
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.error(
                    f"API response for custom models did not contain expected list. Response: {data}"
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
            logger.warning(f"Model ID '{model_id}' not found in available models.")
            return None
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/models/model",
                params={"id": model_id},
                headers=self.json_headers,
            )
            if response.status_code == 401:
                logger.warning(
                    f"Model '{model_id}' not found in API, attempting to create it."
                )
                # Attempt to create the model
                created_model = self.create_model(
                    model_id=model_id, name=model_id, base_model_id=None
                )
                if created_model:
                    logger.info(
                        f"Model '{model_id}' created successfully, retrying to fetch details."
                    )
                    # Retry fetching the model details after creation
                    response = self.session.get(
                        f"{self.base_url}/api/v1/models/model",
                        params={"id": model_id},
                        headers=self.json_headers,
                    )
                else:
                    logger.error(
                        f"Failed to create model '{model_id}', cannot fetch details."
                    )
                    return None
            response.raise_for_status()
            model = response.json()
            if model:
                logger.info(f"   ✅ Found model '{model_id}'.")
                return model
            else:
                logger.warning(
                    f"   ℹ️ Model '{model_id}' not found (API returned empty)."
                )
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model details for '{model_id}': {e}")
            return None

    def create_model(
        self,
        model_id: str,
        name: str,
        base_model_id: str,
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
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a new detailed custom model variant in Open WebUI.

        Args:
            model_id: The tag for the new model (e.g., 'my-custom-model:latest').
            name: The display name for the new model (e.g., 'My Custom Model').
            base_model_id: The ID of the base model to use (e.g., 'gpt-4.1').
            system_prompt: A custom system prompt for the model.
            temperature: The temperature setting for the model.
            stream_response: Whether to stream responses.
            other_params: A dictionary of any other model parameters.
            description: A description for the model's profile.
            profile_image_url: URL for the model's profile image.
            capabilities: Dictionary to set model capabilities like 'vision', 'web_search'.
            suggestion_prompts: A list of suggested prompts for the model.
            tags: A list of tags to categorize the model.
            is_active: Whether the model should be active after creation.

        Returns:
            A dictionary of the created model, or None on failure.
        """
        logger.info(f"Creating new model variant '{name}' ({model_id})...")

        meta = {
            "profile_image_url": profile_image_url,
            "description": description,
            "capabilities": capabilities or {},
            "suggestion_prompts": (
                [{"content": p} for p in suggestion_prompts]
                if suggestion_prompts
                else []
            ),
            "tags": [{"name": t} for t in tags] if tags else [],
        }
        params = {
            "system": system_prompt,
            "temperature": temperature,
            "stream_response": stream_response,
        }
        if other_params:
            params.update(other_params)

        # Filter out None values to keep the payload clean
        params = {k: v for k, v in params.items() if v is not None}
        meta = {k: v for k, v in meta.items() if v is not None}

        payload = {
            "id": model_id,
            "name": name,
            "base_model_id": base_model_id,
            "params": params,
            "meta": meta,
            "is_active": is_active,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/models/create",
                json=payload,
                headers=self.json_headers,
            )
            response.raise_for_status()
            created_model = response.json()
            logger.info(
                f"Successfully created model with ID: {created_model.get('id')}"
            )
            # Add the new model ID to the available models list
            if model_id not in self.available_model_ids:
                self.available_model_ids.append(model_id)
            return created_model
        except requests.exceptions.RequestException as e:
            error_msg = getattr(e.response, "text", str(e))
            logger.error(f"Failed to create model '{name}': {error_msg}")
            return None

    def update_model(
        self,
        model_id: str,
        name: Optional[str] = None,
        base_model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        stream_response: Optional[bool] = None,
        other_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        capabilities: Optional[Dict[str, bool]] = None,
        suggestion_prompts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing custom model in Open WebUI with granular changes.

        Args:
            model_id: The ID of the model to update.
            All other arguments are optional and will only be updated if provided.
        """
        logger.info(f"Updating model '{model_id}'...")
        current_model = self.get_model(model_id)
        if not current_model:
            logger.error(
                f"Cannot update model '{model_id}' because it could not be found."
            )
            return None

        # Start with the existing model data as the base payload
        payload = current_model.copy()

        # Update top-level fields if provided
        if name is not None:
            payload["name"] = name
        if base_model_id is not None:
            payload["base_model_id"] = base_model_id
        if is_active is not None:
            payload["is_active"] = is_active

        # Ensure nested dictionaries exist before updating
        payload.setdefault("params", {})
        payload.setdefault("meta", {})
        payload["meta"].setdefault("capabilities", {})

        # Update nested 'params'
        if system_prompt is not None:
            payload["params"]["system"] = system_prompt
        if temperature is not None:
            payload["params"]["temperature"] = temperature
        if stream_response is not None:
            payload["params"]["stream_response"] = stream_response
        if other_params:
            payload["params"].update(other_params)

        # Update nested 'meta'
        if description is not None:
            payload["meta"]["description"] = description
        if profile_image_url is not None:
            payload["meta"]["profile_image_url"] = profile_image_url
        if capabilities is not None:
            payload["meta"]["capabilities"].update(capabilities)
        if suggestion_prompts is not None:
            payload["meta"]["suggestion_prompts"] = [
                {"content": p} for p in suggestion_prompts
            ]
        if tags is not None:
            payload["meta"]["tags"] = [{"name": t} for t in tags]

        # Remove read-only keys before sending the update request
        for key in ["user", "user_id", "created_at", "updated_at"]:
            payload.pop(key, None)

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/models/model/update",
                params={"id": model_id},
                json=payload,
                headers=self.json_headers,
            )
            response.raise_for_status()
            updated_model = response.json()
            logger.info(f"Successfully updated model '{model_id}'.")
            return updated_model
        except requests.exceptions.RequestException as e:
            error_msg = getattr(e.response, "text", str(e))
            logger.error(f"Failed to update model '{model_id}': {error_msg}")
            return None

    def delete_model(self, model_id: str) -> bool:
        """
        Deletes a model entry from Open WebUI. This does not delete the model from the underlying source (e.g., Ollama).

        Args:
            model_id: The ID of the model to delete (e.g., 'my-custom-model:latest').

        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.info(f"Deleting model entry '{model_id}' from Open WebUI...")
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/models/model/delete",
                params={"id": model_id},
                headers=self.json_headers,
            )
            response.raise_for_status()

            if response.status_code == 200:
                success = False
                try:
                    if response.json() is True:
                        success = True
                except json.JSONDecodeError:
                    success = True  # Empty response also indicates success

                if success:
                    logger.info(f"Successfully deleted model '{model_id}'.")
                    # Remove the model ID from the available models list
                    if model_id in self.available_model_ids:
                        self.available_model_ids.remove(model_id)
                    return True
                else:
                    logger.warning(
                        f"Model deletion for '{model_id}' returned an unexpected value: {response.text}"
                    )
                    return False
            return False
        except requests.exceptions.RequestException as e:
            error_msg = getattr(e.response, "text", str(e))
            logger.error(f"Failed to delete model '{model_id}': {error_msg}")
            return False

    def update_chat_metadata(
        self,
        chat_id: str,
        regenerate_tags: bool = False,
        regenerate_title: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Regenerates and updates the tags and/or title for an existing chat based on its history.

        Args:
            chat_id: The ID of the chat to update.
            regenerate_tags: If True, new tags will be generated and applied.
            regenerate_title: If True, a new title will be generated and applied.

        Returns:
            A dictionary containing the 'suggested_tags' and/or 'suggested_title' that were updated,
            or None if the chat could not be found or no action was requested.
        """
        if not regenerate_tags and not regenerate_title:
            logger.warning("No action requested for update_chat_metadata. Set regenerate_tags or regenerate_title to True.")
            return None

        logger.info(f"Updating metadata for chat {chat_id[:8]}...")
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
                logger.warning("  > Failed to generate new tags.")

        if regenerate_title:
            logger.info("Regenerating title...")
            suggested_title = self._get_title(api_messages)
            if suggested_title:
                self.rename_chat(chat_id, suggested_title)
                return_data["suggested_title"] = suggested_title
                logger.info(f"  > Applied new title: '{suggested_title}'")
            else:
                logger.warning("  > Failed to generate new title.")
        
        return return_data if return_data else None

    def switch_chat_model(self, chat_id: str, model_ids: Union[str, List[str]]) -> bool:
        """
        Switches the model(s) for an existing chat without sending a new message.

        Args:
            chat_id: The ID of the chat to update.
            model_ids: A single model ID (str) or a list of model IDs (List[str]) to set for the chat.

        Returns:
            True if the model(s) were successfully switched, False otherwise.
        """
        if isinstance(model_ids, str):
            model_ids_list = [model_ids]
        elif isinstance(model_ids, list):
            model_ids_list = model_ids
        else:
            logger.error("`model_ids` must be a string or a list of strings.")
            return False

        if not model_ids_list:
            logger.error("`model_ids` list cannot be empty for switching chat models.")
            return False

        logger.info(
            f"Attempting to switch models for chat '{chat_id[:8]}...' to {model_ids_list}"
        )

        # Load chat details to ensure self.chat_object_from_server is populated
        # and self.chat_id is set correctly for the update.
        if not self._load_chat_details(chat_id):
            logger.error(f"Failed to load chat details for chat ID: {chat_id}")
            return False

        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.error(f"Chat object not properly loaded for chat ID: {chat_id}")
            return False

        current_models = self.chat_object_from_server["chat"].get("models", [])
        if set(current_models) == set(model_ids_list):
            logger.info(
                f"Chat '{chat_id[:8]}...' is already using models {model_ids_list}. No change needed."
            )
            return True

        logger.info(
            f"  > Changing models from: {current_models if current_models else 'None'}"
        )
        logger.info(f"  > Changing models to:   {model_ids_list}")

        self.model_id = (
            model_ids_list[0] if model_ids_list else self.default_model_id
        )  # Set internal state to the first model if multiple
        self.chat_object_from_server["chat"]["models"] = model_ids_list

        if self._update_remote_chat():
            logger.info(
                f"Successfully switched models for chat '{chat_id[:8]}...' to {model_ids_list}."
            )
            return True
        else:
            logger.error(f"Failed to update remote chat for chat ID: {chat_id}")
            return False

    def _ask(
        self,
        question: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
    ) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        if not self.chat_id:
            return None, None, None
        logger.info(f'Processing question: "{question}"')
        chat_core = self.chat_object_from_server["chat"]
        chat_core["models"] = [self.model_id]

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

    def _replace_message_content(
        self, chat_id: str, message_id: str, content: str
    ) -> None:
        """
        Replaces the content of a specific message using a 'replace' event.
        This is a fire-and-forget operation.
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/messages/{message_id}/event"
        payload = {"type": "chat:message:replace", "data": {"content": content}}

        def _send_replace_event():
            """Internal function for asynchronous real-time updates"""
            try:
                response = self.session.post(
                    url, json=payload, headers=self.json_headers, timeout=5.0
                )
                response.raise_for_status()
                logger.debug(
                    f"✅ Replace event sent successfully for message {message_id[:8]}..."
                )
            except Exception as e:
                logger.debug(
                    f"⚠️ Replace event failed for message {message_id[:8]}...: {e}"
                )

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(_send_replace_event)

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
        # Local storage user message content has been updated above

        # 6. Stream and fill assistant message
        try:
            logger.info("🔄 Starting streaming completion...")
            assistant_full_content = ""
            sources = []

            stream_generator = self._get_model_completion_stream(
                self.chat_id, api_messages, api_rag_payload, self.model_id, tool_ids
            )

            # Properly handle streaming response, use try/except to catch StopIteration to get sources
            try:
                while True:
                    chunk = next(stream_generator)
                    assistant_full_content += chunk
                    self._stream_delta_update(self.chat_id, assistant_message_id, chunk)
                    yield chunk
            except StopIteration as e:
                # Get sources from StopIteration.value
                sources = e.value if e.value is not None else []

            logger.info("Successfully received full streaming model response.")

            # 7. Update final state and sync
            storage_assistant_message["content"] = assistant_full_content
            storage_assistant_message["done"] = True
            storage_assistant_message["sources"] = sources

            logger.info("📤 Updating final chat state on backend...")
            follow_ups = None
            if self._update_remote_chat():
                logger.info("✅ Final chat state updated successfully!")

                if enable_follow_up:
                    logger.info("Follow-up is enabled, fetching suggestions...")
                    api_messages_for_follow_up = self._build_linear_history_for_api(
                        chat_core
                    )
                    follow_ups = self._get_follow_up_completions(
                        api_messages_for_follow_up
                    )
                    if follow_ups:
                        logger.info(
                            f"Received {len(follow_ups)} follow-up suggestions."
                        )
                        storage_assistant_message["followUps"] = (
                            follow_ups  # Update local storage assistant message
                        )
                        if self._update_remote_chat():  # Sync again to save follow-ups
                            logger.info(
                                "Successfully updated chat with follow-up suggestions."
                            )
                        else:
                            logger.warning(
                                "Failed to update chat with follow-up suggestions."
                            )
                    else:
                        logger.info("No follow-up suggestions were generated.")

            return assistant_full_content, sources, follow_ups
        except Exception as e:
            logger.error(f"Error during streaming chat: {e}")
            raise

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

    def _handle_rag_references(
        self, rag_files: Optional[List[str]], rag_collections: Optional[List[str]]
    ) -> Tuple[List[Dict], List[Dict]]:
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
                        storage_payload.append({"type": "collection", **kb_details})
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
        if hasattr(self, "task_model") and self.task_model:
            return self.task_model

        logger.info("Fetching task model configuration...")
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
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch task config: {e}")
            return None
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from task config response.")
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
            data = response.json()

            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if content:
                    try:
                        content_json = json.loads(content)
                        tags = content_json.get("tags")
                        if isinstance(tags, list):
                            logger.info(f"   ✅ Received {len(tags)} tag suggestions.")
                            return tags
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from tags content: {content}")
                        return None
            logger.warning(f"   ⚠️ Unexpected format for tags response: {data}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Tags API HTTP Error: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Tags API Network Error: {e}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError):
            logger.error("Failed to parse JSON or find expected keys in tags response.")
            return None

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

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            logger.error(f"RAG file not found at path: {file_path}")
            return None
        url, file_name = f"{self.base_url}/api/v1/files/", os.path.basename(file_path)
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f)}
                headers = {"Authorization": self.session.headers["Authorization"]}
                logger.info(f"Uploading file '{file_name}' for RAG...")
                response = self.session.post(url, headers=headers, files=files)
                response.raise_for_status()
            response_data = response.json()
            if file_id := response_data.get("id"):
                logger.info(f"  > Upload successful. File ID: {file_id}")
                return response_data
            logger.error(f"File upload response did not contain an ID: {response_data}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file '{file_name}': {e}")
            return None

    def _get_model_completion(
        self,
        chat_id: str,
        messages: List[Dict[str, Any]],
        api_rag_payload: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], List]:
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
                    url, json=payload, headers=self.json_headers, timeout=3.0  # 3 second timeout
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

    def _get_model_completion_stream(  # New method for streaming
        self,
        chat_id: str,
        messages: List[Dict[str, Any]],
        api_rag_payload: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Generator[
        str, None, List
    ]:  # Yields content chunks, returns a list (sources) at the end
        active_model_id = model_id or self.model_id
        payload = {
            "model": active_model_id,
            "messages": messages,
            "stream": True,  # KEY CHANGE: Enable streaming
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
                stream=True,  # KEY CHANGE: Enable streaming on requests session
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

    def set_chat_tags(self, chat_id: str, tags: List[str]):
        if not tags:
            return
        logger.info(f"Applying tags {tags} to chat {chat_id[:8]}...")
        url_get = f"{self.base_url}/api/v1/chats/{chat_id}/tags"
        try:
            response = self.session.get(url_get, headers=self.json_headers)
            response.raise_for_status()
            existing_tags = {tag["name"] for tag in response.json()}
        except requests.exceptions.RequestException:
            logger.warning("Could not fetch existing tags. May create duplicates.")
            existing_tags = set()
        url_post = f"{self.base_url}/api/v1/chats/{chat_id}/tags"
        for tag_name in tags:
            if tag_name not in existing_tags:
                try:
                    self.session.post(
                        url_post, json={"name": tag_name}, headers=self.json_headers
                    ).raise_for_status()
                    logger.info(f"  + Added tag: '{tag_name}'")
                except requests.exceptions.RequestException as e:
                    logger.error(f"  - Failed to add tag '{tag_name}': {e}")
            else:
                logger.info(f"  = Tag '{tag_name}' already exists, skipping.")

    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """
        Renames an existing chat.
        """
        if not chat_id:
            logger.error("rename_chat: chat_id cannot be empty.")
            return False

        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        payload = {"chat": {"title": new_title}}

        try:
            logger.info(f"Renaming chat {chat_id[:8]}... to '{new_title}'")
            response = self.session.post(url, headers=self.json_headers, json=payload)
            response.raise_for_status()
            logger.info("Chat renamed successfully.")

            # If the renamed chat is the currently active one, update its internal state.
            if self.chat_id == chat_id and self.chat_object_from_server:
                self.chat_object_from_server["title"] = new_title
                if "chat" in self.chat_object_from_server:
                    self.chat_object_from_server["chat"]["title"] = new_title

            return True
        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Failed to rename chat: {e.response.text}")
            else:
                logger.error(f"Failed to rename chat: {e}")
            return False

    def _find_or_create_chat_by_title(self, title: str):
        if existing_chat := self._search_latest_chat_by_title(title):
            logger.info(f"Found and loading chat '{title}' via API.")
            self._load_chat_details(existing_chat["id"])
        else:
            logger.info(f"Chat '{title}' not found, creating a new one.")
            if new_chat_id := self._create_new_chat(title):
                self._load_chat_details(new_chat_id)

    def _load_chat_details(self, chat_id: str) -> bool:
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chats/{chat_id}", headers=self.json_headers
            )
            response.raise_for_status()
            details = response.json()
            if details:
                self.chat_id = chat_id
                self.chat_object_from_server = details
                chat_core = self.chat_object_from_server.setdefault("chat", {})
                chat_core.setdefault("history", {"messages": {}, "currentId": None})
                # Ensure 'models' is a list
                models_list = chat_core.get("models", [])
                if isinstance(models_list, list) and models_list:
                    self.model_id = models_list[0]
                else:
                    self.model_id = self.default_model_id
                return True
            else:
                logger.warning(f"Empty response when loading chat details for {chat_id}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
            return False

    def create_folder(self, name: str) -> Optional[str]:
        logger.info(f"Creating folder '{name}'...")
        try:
            self.session.post(
                f"{self.base_url}/api/v1/folders/",
                json={"name": name},
                headers=self.json_headers,
            ).raise_for_status()
            logger.info(f"Successfully sent request to create folder '{name}'.")
            return self.get_folder_id_by_name(name, suppress_log=True)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    def get_folder_id_by_name(
        self, name: str, suppress_log: bool = False
    ) -> Optional[str]:
        if not suppress_log:
            logger.info(f"Searching for folder '{name}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/folders/", headers=self.json_headers
            )
            response.raise_for_status()
            for folder in response.json():
                if folder.get("name") == name:
                    if not suppress_log:
                        logger.info("Found folder.")
                    return folder.get("id")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get folder list: {e}")
        if not suppress_log:
            logger.info(f"Folder '{name}' not found.")
        return None

    def move_chat_to_folder(self, chat_id: str, folder_id: str):
        logger.info(f"Moving chat {chat_id[:8]}... to folder {folder_id[:8]}...")
        try:
            self.session.post(
                f"{self.base_url}/api/v1/chats/{chat_id}/folder",
                json={"folder_id": folder_id},
                headers=self.json_headers,
            ).raise_for_status()
            self.chat_object_from_server["folder_id"] = folder_id
            logger.info("Chat moved successfully!")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to move chat: {e}")

    def _is_placeholder_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is a placeholder (content is empty and not marked as done)"""
        return message.get("content", "").strip() == "" and not message.get(
            "done", False
        )

    def _create_placeholder_messages(self, count: int) -> List[Tuple[str, str]]:
        """
        Create the specified number of placeholder message pairs (user-assistant) and add them to the current chat_object_from_server history.
        Returns [(user_message_id, assistant_message_id), ...]
        """
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.error(
                "Chat object not initialized, cannot create placeholder messages."
            )
            return []

        chat_core = self.chat_object_from_server["chat"]
        messages = chat_core["history"]["messages"]
        current_id = chat_core["history"].get("currentId")

        placeholder_ids = []
        for _ in range(count):
            user_message_id = str(uuid.uuid4())
            assistant_message_id = str(uuid.uuid4())

            # User message as parent message, pointing to assistant message
            user_message = {
                "id": user_message_id,
                "parentId": current_id,
                "childrenIds": [assistant_message_id],
                "role": "user",
                "content": "",  # Initial content is empty
                "files": [],
                "models": [self.model_id],
                "timestamp": int(time.time()),
                "done": False,  # Placeholder message not completed
            }
            # Assistant message as child message
            assistant_message = {
                "id": assistant_message_id,
                "parentId": user_message_id,
                "childrenIds": [],
                "role": "assistant",
                "content": "",  # Initial content is empty
                "model": self.model_id,
                "modelName": self.model_id.split(":")[0],
                "timestamp": int(time.time()),
                "done": False,  # Placeholder message not completed
                "sources": [],
            }

            messages[user_message_id] = user_message
            messages[assistant_message_id] = assistant_message
            placeholder_ids.append((user_message_id, assistant_message_id))

            # Update currentId to the latest created assistant message ID to ensure correct message chain
            current_id = assistant_message_id

        chat_core["history"]["currentId"] = current_id  # Update chat_core's currentId
        chat_core["messages"] = self._build_linear_history_for_storage(
            chat_core, current_id
        )

        # Immediately sync placeholder messages to remote server
        if self._update_remote_chat():
            logger.info(
                f"Created and synced {count} placeholder message pairs to server."
            )
        else:
            logger.warning(
                f"Created {count} placeholder message pairs but failed to sync to server."
            )

        return placeholder_ids

    def _ensure_placeholder_messages(self, pool_size: int, min_available: int) -> bool:
        """
        Ensure there are enough placeholder messages available.
        If the current number of placeholder messages is less than min_available, create new placeholder messages until pool_size is reached.
        """
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.error(
                "Chat object not initialized, cannot ensure placeholder messages."
            )
            return False

        chat_core = self.chat_object_from_server["chat"]
        messages = chat_core["history"]["messages"]

        # Count the current number of unfinished placeholder messages
        current_placeholder_count = 0
        for msg_id in messages:
            msg = messages[msg_id]
            if self._is_placeholder_message(msg):
                current_placeholder_count += 1

        # Calculate the number of placeholder message pairs to create (each pair contains one user message and one assistant message)
        current_placeholder_pairs = current_placeholder_count // 2  # Because each pair has 2 messages

        pairs_to_create = 0
        if (
            current_placeholder_pairs < min_available // 2
        ):  # min_available also refers to the number of message pairs
            pairs_to_create = (pool_size // 2) - current_placeholder_pairs
            if pairs_to_create < 0:
                pairs_to_create = 0

        if pairs_to_create > 0:
            logger.info(f"Ensuring {pairs_to_create} new placeholder message pairs...")
            self._create_placeholder_messages(pairs_to_create)
            logger.info("Placeholder messages ensured.")
            return True
        else:
            logger.info("Enough placeholder messages already exist.")
            return False

    def _get_next_available_message_pair(self) -> Optional[Tuple[str, str]]:
        """
        Find the next available placeholder message ID pair (user message ID, assistant message ID) from the current chat_object_from_server history.
        Does not modify message status, only finds available placeholder message pairs.
        """
        if (
            not self.chat_object_from_server
            or "chat" not in self.chat_object_from_server
        ):
            logger.error(
                "Chat object not initialized, cannot get next available message pair."
            )
            return None

        chat_core = self.chat_object_from_server["chat"]
        messages = chat_core["history"]["messages"]

        # Find the first completely empty placeholder message pair
        # Note: We are looking for truly placeholder messages with empty content and done=False
        found_placeholder = False
        user_placeholder_id = None
        assistant_placeholder_id = None

        # Traverse in message creation order, looking for the first empty assistant placeholder message
        for msg_id, msg in messages.items():
            if (
                msg.get("role") == "assistant"
                and msg.get("content", "").strip() == ""
                and not msg.get("done", False)
            ):

                # Check if the corresponding user message is also an empty placeholder
                user_id = msg.get("parentId")
                if (
                    user_id
                    and user_id in messages
                    and messages[user_id].get("role") == "user"
                    and messages[user_id].get("content", "").strip() == ""
                    and not messages[user_id].get("done", False)
                ):

                    user_placeholder_id = user_id
                    assistant_placeholder_id = msg_id
                    found_placeholder = True
                    break

        if found_placeholder:
            logger.info(
                f"Found available placeholder pair: User={user_placeholder_id[:8]}..., Assistant={assistant_placeholder_id[:8]}..."
            )
            return user_placeholder_id, assistant_placeholder_id
        else:
            logger.warning("No available placeholder message pairs found.")
            return None

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

    def _create_new_chat(self, title: str) -> Optional[str]:
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

    def _search_latest_chat_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Globally searching for chat with title '{title}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chats/search",
                params={"text": title},
                headers=self.json_headers,
            )
            response.raise_for_status()
            candidates = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search for chats: {e}")
            return None
        matching_chats = [chat for chat in candidates if chat.get("title") == title]
        if not matching_chats:
            logger.info("No exact match found.")
            return None
        if len(matching_chats) > 1:
            logger.warning(
                f"Found {len(matching_chats)} chats with the same title. Selecting the most recent one."
            )
            matching_chats.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return matching_chats[0]

    def _get_chat_details(self, chat_id: str) -> Optional[Dict[str, Any]]:
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
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/{kb_id}", headers=self.json_headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get knowledge base details for {kb_id}: {e}")
            return None

    def _build_linear_history_for_api(
        self, chat_core: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        history, current_id = [], chat_core.get("history", {}).get("currentId")
        messages = chat_core.get("history", {}).get("messages", {})
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
        history, current_id = [], start_id
        messages = chat_core.get("history", {}).get("messages", {})
        while current_id and current_id in messages:
            history.insert(0, messages[current_id])
            current_id = messages[current_id].get("parentId")
        return history

    def _update_remote_chat(self) -> bool:
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

    @staticmethod
    def _encode_image_to_base64(image_path: str) -> Optional[str]:
        if not os.path.exists(image_path):
            logger.warning(f"Image file not found: {image_path}")
            return None
        try:
            ext = image_path.split(".")[-1].lower()
            mime_type = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "webp": "image/webp",
            }.get(ext, "application/octet-stream")
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Error encoding image '{image_path}': {e}")
            return None

    # Notes API Methods
    def get_notes(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all notes for the current user.
        
        Returns:
            A list of note objects with user information, or None if failed.
        """
        logger.info("Getting all notes...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/notes/",
                headers=self.json_headers
            )
            response.raise_for_status()
            notes = response.json()
            logger.info(f"Successfully retrieved {len(notes)} notes.")
            return notes
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get notes: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting notes: {e}")
            return None

    def get_notes_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get a simplified list of notes with only id, title, and timestamps.
        
        Returns:
            A list of simplified note objects, or None if failed.
        """
        logger.info("Getting notes list...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/notes/list",
                headers=self.json_headers
            )
            response.raise_for_status()
            notes_list = response.json()
            logger.info(f"Successfully retrieved notes list with {len(notes_list)} items.")
            return notes_list
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get notes list: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting notes list: {e}")
            return None

    def create_note(
        self,
        title: str,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new note.
        
        Args:
            title: The title of the note (required).
            data: Optional data dictionary for the note.
            meta: Optional metadata dictionary for the note.
            access_control: Optional access control settings.
            
        Returns:
            The created note object, or None if creation failed.
        """
        logger.info(f"Creating note with title: '{title}'...")
        payload = {"title": title}
        
        if data is not None:
            payload["data"] = data
        if meta is not None:
            payload["meta"] = meta
        if access_control is not None:
            payload["access_control"] = access_control
            
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/notes/create",
                json=payload,
                headers=self.json_headers
            )
            response.raise_for_status()
            note = response.json()
            if note:
                logger.info(f"Successfully created note with ID: {note.get('id', 'Unknown')}")
                return note
            else:
                logger.warning("Note creation returned empty response.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create note: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating note: {e}")
            return None

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific note by its ID.
        
        Args:
            note_id: The ID of the note to retrieve.
            
        Returns:
            The note object, or None if not found or failed.
        """
        logger.info(f"Getting note by ID: {note_id}")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/notes/{note_id}",
                headers=self.json_headers
            )
            response.raise_for_status()
            note = response.json()
            if note:
                logger.info(f"Successfully retrieved note: {note.get('title', 'Unknown title')}")
                return note
            else:
                logger.warning(f"Note with ID {note_id} not found.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get note by ID {note_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting note by ID {note_id}: {e}")
            return None

    def update_note_by_id(
        self,
        note_id: str,
        title: str,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing note by its ID.
        
        Args:
            note_id: The ID of the note to update.
            title: The new title of the note (required).
            data: Optional new data dictionary for the note.
            meta: Optional new metadata dictionary for the note.
            access_control: Optional new access control settings.
            
        Returns:
            The updated note object, or None if update failed.
        """
        logger.info(f"Updating note ID {note_id} with title: '{title}'...")
        payload = {"title": title}
        
        if data is not None:
            payload["data"] = data
        if meta is not None:
            payload["meta"] = meta
        if access_control is not None:
            payload["access_control"] = access_control
            
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/notes/{note_id}/update",
                json=payload,
                headers=self.json_headers
            )
            response.raise_for_status()
            note = response.json()
            if note:
                logger.info(f"Successfully updated note with ID: {note_id}")
                return note
            else:
                logger.warning(f"Note update for ID {note_id} returned empty response.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update note ID {note_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating note ID {note_id}: {e}")
            return None

    def delete_note_by_id(self, note_id: str) -> bool:
        """
        Delete a note by its ID.
        
        Args:
            note_id: The ID of the note to delete.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.info(f"Deleting note with ID: {note_id}")
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/notes/{note_id}/delete",
                headers=self.json_headers
            )
            response.raise_for_status()
            
            # The API returns a boolean indicating success
            result = response.json()
            if result is True:
                logger.info(f"Successfully deleted note with ID: {note_id}")
                return True
            else:
                logger.warning(f"Note deletion for ID {note_id} returned: {result}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete note ID {note_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting note ID {note_id}: {e}")
            return False
