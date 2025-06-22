import requests
import json
import uuid
import time
import base64
import os
import logging
from typing import Optional, List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        self.session_cache: Dict[str, Dict[str, Any]] = {}
        self.file_upload_cache: Dict[str, Dict[str, Any]] = {}
        self.kb_cache: Dict[str, Dict[str, Any]] = {}
        self.chat_id: Optional[str] = None
        self.chat_object_from_server: Optional[Dict[str, Any]] = None
        self.model_id: str = default_model_id

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
    ) -> Tuple[Optional[str], Optional[str]]:
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
        logger.info("=" * 60)
        self._find_or_create_chat_by_title(chat_title)
        if not self.chat_id:
            logger.error("Chat initialization failed, cannot proceed.")
            return None, None
        if folder_name:
            folder_id = self.get_folder_id_by_name(folder_name) or self.create_folder(
                folder_name
            )
            if folder_id and self.chat_object_from_server.get("folder_id") != folder_id:
                self.move_chat_to_folder(self.chat_id, folder_id)
        response, message_id = self._ask(
            question, image_paths, rag_files, rag_collections
        )
        if response and tags:
            self.set_chat_tags(self.chat_id, tags)
        return response, message_id

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
    ) -> Optional[Dict[str, str]]:
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
        logger.info("=" * 60)
        self._find_or_create_chat_by_title(chat_title)
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
                ): model_id
                for model_id in model_ids
            }
            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    content, sources = future.result()
                    responses[model_id] = {"content": content, "sources": sources}
                except Exception as exc:
                    logger.error(f"Model '{model_id}' generated an exception: {exc}")
                    responses[model_id] = {"content": None, "sources": []}

        successful_responses = {
            k: v for k, v in responses.items() if v["content"] is not None
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
        if self._update_remote_chat():
            logger.info("Chat history updated successfully!")
            self.session_cache[self.chat_object_from_server["title"]] = {
                "id": self.chat_id,
                "obj": self.chat_object_from_server,
                "model": self.model_id,
            }
            if tags:
                self.set_chat_tags(self.chat_id, tags)
            return {k: v["content"] for k, v in successful_responses.items()}
        return None

    def get_knowledge_base_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        if name in self.kb_cache:
            logger.info(f"Found knowledge base '{name}' in cache.")
            return self.kb_cache[name]
        logger.info(f"🔍 Searching for knowledge base '{name}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/list", headers=self.json_headers
            )
            response.raise_for_status()
            for kb in response.json():
                self.kb_cache[kb.get("name")] = kb
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
            self.kb_cache[name] = kb_data
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

    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available models in Open WebUI, including custom variants."""
        logger.info("Listing all available models...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/models/", headers=self.json_headers
            )
            response.raise_for_status()
            models = response.json()
            logger.info(f"Found {len(models)} models.")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return None

    def list_base_models(self) -> Optional[List[Dict[str, Any]]]:
        """Lists all available base models that can be used to create variants."""
        logger.info("Listing all available base models...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/models/base", headers=self.json_headers
            )
            response.raise_for_status()
            models = response.json()
            logger.info(f"Found {len(models)} base models.")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list base models: {e}")
            return None

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the details of a specific model by its ID.

        Args:
            model_id: The ID of the model to fetch (e.g., 'llama3:latest').

        Returns:
            A dictionary containing the model details, or None if not found.
        """
        logger.info(f"Fetching details for model '{model_id}'...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/models/model",
                params={"id": model_id},
                headers=self.json_headers,
            )
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
                try:
                    if response.json() is True:
                        logger.info(f"Successfully deleted model '{model_id}'.")
                        return True
                    else:
                        logger.warning(
                            f"Model deletion for '{model_id}' returned an unexpected value: {response.text}"
                        )
                        return False
                except json.JSONDecodeError:
                    logger.info(
                        f"Successfully sent delete request for model '{model_id}' (empty response)."
                    )
                    return True
            return False
        except requests.exceptions.RequestException as e:
            error_msg = getattr(e.response, "text", str(e))
            logger.error(f"Failed to delete model '{model_id}': {error_msg}")
            return False

    def _ask(
        self,
        question: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        if not self.chat_id:
            return None, None
        logger.info(f'Processing question: "{question}"')
        chat_core = self.chat_object_from_server["chat"]

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

        logger.info("Calling completions API to get model response...")
        assistant_content, sources = self._get_model_completion(
            self.chat_id, api_messages, api_rag_payload
        )
        if assistant_content is None:
            return None, None
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
            self.session_cache[self.chat_object_from_server["title"]] = {
                "id": self.chat_id,
                "obj": self.chat_object_from_server,
                "model": self.model_id,
            }
            return assistant_content, assistant_message_id
        return None, None

    def _get_single_model_response_in_parallel(
        self, chat_core, model_id, question, image_paths, api_rag_payload
    ):
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
            self.chat_id, api_messages, api_rag_payload, model_id
        )
        return content, sources

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

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        if file_path in self.file_upload_cache:
            logger.info(f"Found file in cache: '{os.path.basename(file_path)}'")
            return self.file_upload_cache[file_path]
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
                self.file_upload_cache[file_path] = response_data
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
    ) -> Tuple[Optional[str], List]:
        active_model_id = model_id or self.model_id
        payload = {
            "model": active_model_id,
            "messages": messages,
            "chat_id": chat_id,
            "stream": False,
        }
        if api_rag_payload:
            payload["files"] = api_rag_payload
            logger.info(
                f"Attaching {len(api_rag_payload)} RAG references to completion request for model {active_model_id}."
            )
        logger.debug(f"Sending completion request: {json.dumps(payload, indent=2)}")
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
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            if hasattr(e, "response"):
                logger.error(
                    f"Completions API Error for {active_model_id}: {e.response.text}"
                )
            else:
                logger.error(f"Completions API Error for {active_model_id}: {e}")
            return None, []

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

    def _find_or_create_chat_by_title(self, title: str):
        if title in self.session_cache:
            logger.info(f"Loading chat '{title}' from session cache.")
            self._activate_chat_state(self.session_cache[title])
            return
        if existing_chat := self._search_latest_chat_by_title(title):
            logger.info(f"Found and loading chat '{title}' via API.")
            self._load_and_cache_chat_state(existing_chat["id"], title)
        else:
            logger.info(f"Chat '{title}' not found, creating a new one.")
            if new_chat_id := self._create_new_chat(title):
                self._load_and_cache_chat_state(new_chat_id, title)

    def _activate_chat_state(self, state: Dict[str, Any]):
        self.chat_id, self.chat_object_from_server, self.model_id = (
            state["id"],
            state["obj"],
            state["model"],
        )

    def _load_and_cache_chat_state(self, chat_id: str, cache_key: str):
        if self._load_chat_details(chat_id):
            self.session_cache[cache_key] = {
                "id": self.chat_id,
                "obj": self.chat_object_from_server,
                "model": self.model_id,
            }

    def _load_chat_details(self, chat_id: str) -> bool:
        if chat_details := self._get_chat_details(chat_id):
            self.chat_id, self.chat_object_from_server = chat_id, chat_details
            chat_core = self.chat_object_from_server.setdefault("chat", {})
            chat_core.setdefault("history", {"messages": {}, "currentId": None})
            self.model_id = chat_core.get("models", [self.default_model_id])[0]
            return True
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
            logger.info(f"Successfully created chat with ID: {chat_id[:8]}...")
            return chat_id
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
