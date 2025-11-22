"""
Async File management module for OpenWebUI Chat Client.
"""

import logging
import os
import base64
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncFileManager:
    """
    Handles async file-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file to the OpenWebUI server."""
        return await self.base_client._upload_file(file_path)

    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64 string.
        
        Note: This method is synchronous (not async) as it's CPU-bound and the file
        operations are typically fast for images. For consistency in async contexts,
        callers can use asyncio.to_thread(self.encode_image_to_base64, image_path)
        if non-blocking behavior is required for large files.
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None

        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                media_type = "image/jpeg"
                if image_path.lower().endswith(".png"):
                    media_type = "image/png"
                elif image_path.lower().endswith(".gif"):
                    media_type = "image/gif"
                elif image_path.lower().endswith(".webp"):
                    media_type = "image/webp"

                return f"data:{media_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None
