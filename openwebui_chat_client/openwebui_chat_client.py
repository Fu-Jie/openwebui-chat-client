import requests
import json
import uuid
import time
import base64
import os
import logging
from typing import Optional, List, Tuple, Dict, Any

# Set up a logger for the library.
# The application using this library will configure the handler and level.
logger = logging.getLogger(__name__)


class OpenWebUIClient:
    """
    An intelligent, stateful Python client for the Open WebUI API.
    It treats chat titles as globally unique identifiers to automatically
    create or continue conversations, and can place them in specified folders.
    """

    def __init__(self, base_url: str, token: str, default_model_id: str):
        """
        Initializes the client.

        Args:
            base_url (str): The base URL of the Open WebUI instance.
            token (str): The authentication token (Bearer Token), api key, or jwt token.
            default_model_id (str): The default model ID to use for new chats.
        """
        self.base_url = base_url
        self.default_model_id = default_model_id
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        self.session_cache: Dict[str, Dict[str, Any]] = {}
        self.chat_id: Optional[str] = None
        self.chat_object_from_server: Optional[Dict[str, Any]] = None
        self.model_id: str = default_model_id

    def chat(
        self,
        question: str,
        chat_title: str,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        The main public method: intelligently starts or continues a chat based on its
        globally unique title and ensures it's in the correct folder.

        Args:
            question (str): The question text to ask.
            chat_title (str): The globally unique title for the chat.
            folder_name (str, optional): The folder where the chat should reside. Defaults to None.
            image_paths (List[str], optional): A list of local paths to images. Defaults to None.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple of (assistant's response, message ID).
        """
        logger.info("=" * 60)
        logger.info(
            f"Processing new request: title='{chat_title}', folder='{folder_name}'"
        )
        if image_paths:
            logger.info(f"With images: {image_paths}")
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

        return self._ask(question, image_paths)

    # --- Internal Core Logic ---

    def _find_or_create_chat_by_title(self, title: str):
        cache_key = title
        if cache_key in self.session_cache:
            logger.info(f"Loading chat '{title}' from session cache.")
            self._activate_chat_state(self.session_cache[cache_key])
            return

        existing_chat = self._search_latest_chat_by_title(title)
        if existing_chat:
            logger.info(f"Found and loading chat '{title}' via API.")
            self._load_and_cache_chat_state(existing_chat["id"], cache_key)
        else:
            logger.info(f"Chat '{title}' not found, creating a new one.")
            new_chat_id = self._create_new_chat(title)
            if new_chat_id:
                self._load_and_cache_chat_state(new_chat_id, cache_key)

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
        chat_details = self._get_chat_details(chat_id)
        if chat_details:
            self.chat_id, self.chat_object_from_server = chat_id, chat_details
            chat_core = self.chat_object_from_server.setdefault("chat", {})
            chat_core.setdefault("history", {"messages": {}, "currentId": None})
            self.model_id = chat_core.get("model", self.default_model_id)
            return True
        return False

    def _ask(
        self, question: str, image_paths: Optional[List[str]] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        if not self.chat_id:
            return None, None

        logger.info(f'Processing question: "{question}"')
        chat_core = self.chat_object_from_server["chat"]

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
        assistant_content = self._get_model_completion(api_messages)
        if not assistant_content:
            return None, None
        logger.info("Successfully received model response.")

        user_message_id = str(uuid.uuid4())
        last_message_id = chat_core["history"].get("currentId")
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

    # --- API Helper Methods ---

    def create_folder(self, name: str) -> Optional[str]:
        logger.info(f"Creating folder '{name}'...")
        try:
            self.session.post(
                f"{self.base_url}/api/v1/folders/", json={"name": name}
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
            folders = self.session.get(f"{self.base_url}/api/v1/folders/").json()
            for folder in folders:
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
            ).raise_for_status()
            self.chat_object_from_server["folder_id"] = folder_id
            logger.info("Chat moved successfully!")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to move chat: {e}")

    def _create_new_chat(self, title: str) -> Optional[str]:
        logger.info(f"Creating new chat with title '{title}'...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chats/new", json={"chat": {"title": title}}
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
                f"{self.base_url}/api/v1/chats/search", params={"text": title}
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
            response = self.session.get(f"{self.base_url}/api/v1/chats/{chat_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get chat details for {chat_id}: {e}")
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

    def _get_model_completion(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        payload = {"model": self.model_id, "messages": messages, "stream": False}
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/completions", json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            if hasattr(e, "response"):
                logger.error(f"Completions API Error: {e.response.text}")
            else:
                logger.error(f"Completions API Error: {e}")
            return None

    def _update_remote_chat(self) -> bool:
        try:
            self.session.post(
                f"{self.base_url}/api/v1/chats/{self.chat_id}",
                json={"chat": self.chat_object_from_server["chat"]},
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
            mime_type = "image/jpeg"
            if image_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_path.lower().endswith(".gif"):
                mime_type = "image/gif"
            elif image_path.lower().endswith(".webp"):
                mime_type = "image/webp"

            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Error encoding image '{image_path}': {e}")
            return None
