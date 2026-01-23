"""
Streaming Service for OpenWebUI Chat Client.

Handles:
- Streaming chat responses
- Real-time content updates
- SSE (Server-Sent Events) processing
"""

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional

from openwebui_chat_client.core.base_manager import BaseManager

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class StreamingService(BaseManager):
    """
    Service for handling streaming responses from OpenWebUI API.

    Provides real-time streaming of chat completions.
    """

    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the streaming service.

        Args:
            base_client: The base client instance
        """
        super().__init__(base_client)

    def stream_completion(
        self,
        chat_id: str,
        messages: list,
        model: str,
        files: Optional[list] = None,
        **options: Any,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat completion from the API.

        Args:
            chat_id: Chat ID
            messages: List of message dictionaries
            model: Model identifier
            files: Optional files for RAG
            **options: Additional options (temperature, max_tokens, etc.)

        Yields:
            Dict containing streaming response chunks
        """
        url = f"{self.base_url}/api/chat/completions"

        payload = {
            "chat_id": chat_id,
            "messages": messages,
            "model": model,
            "stream": True,
        }

        # Add files if provided
        if files:
            payload["files"] = files

        # Add optional parameters
        if "temperature" in options:
            payload["temperature"] = options["temperature"]
        if "max_tokens" in options:
            payload["max_tokens"] = options["max_tokens"]
        if "tool_ids" in options:
            payload["tool_ids"] = options["tool_ids"]

        self.logger.debug(f"Streaming completion for chat {chat_id} with model {model}")

        try:
            with self.session.post(
                url, json=payload, headers=self.json_headers, stream=True
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    line_str = line.decode("utf-8")

                    # Skip empty lines and comments
                    if not line_str.strip() or line_str.startswith(":"):
                        continue

                    # Parse SSE data
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove 'data: ' prefix

                        # Check for stream end
                        if data_str == "[DONE]":
                            self.logger.debug("Stream completed")
                            break

                        try:
                            data = json.loads(data_str)
                            yield data
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Failed to parse streaming data: {e}")
                            continue

        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            raise

    def collect_streaming_response(
        self, stream_generator: Generator[Dict[str, Any], None, None]
    ) -> str:
        """
        Collect full response from streaming generator.

        Args:
            stream_generator: Generator yielding response chunks

        Returns:
            Complete response text
        """
        content_parts = []

        for chunk in stream_generator:
            # Extract content from chunk
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    content_parts.append(content)
            elif "message" in chunk:
                # Alternative format
                content = chunk["message"].get("content", "")
                if content:
                    content_parts.append(content)

        return "".join(content_parts)
