"""
Asynchronous file management module for OpenWebUI Chat Client.
Handles async file uploads, image encoding, and file-related operations.
"""

import aiofiles
import base64
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AsyncFileManager:
    """
    Handles all asynchronous file-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        """
        Initialize the async file manager.

        Args:
            base_client: The async base client instance for making API requests.
        """
        self.base_client = base_client

    async def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously upload a file to the OpenWebUI server.
        """
        if not os.path.exists(file_path): # os.path.exists is sync, but fast enough
            logger.error(f"File not found at path: {file_path}")
            return None

        url = f"{self.base_client.base_url}/api/v1/files/"
        file_name = os.path.basename(file_path)

        try:
            async with aiofiles.open(file_path, "rb") as f:
                files = {"file": (file_name, await f.read(), "application/octet-stream")}
                # We need to create a new client or use a different header format for multipart
                headers = {"Authorization": self.base_client.session.headers["Authorization"]}

                response = await self.base_client.session.post(url, headers=headers, files=files)
                response.raise_for_status()

            response_data = response.json()
            if response_data.get("id"):
                logger.info(f"Async upload successful. File ID: {response_data['id']}")
                return response_data
            logger.error(f"Async file upload response did not contain an ID: {response_data}")
            return None
        except Exception as e:
            logger.error(f"Failed to async upload file '{file_name}': {e}")
            return None

    @staticmethod
    async def encode_image_to_base64(image_path: str) -> Optional[str]:
        """
        Asynchronously encode an image file to base64 format.
        """
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

            async with aiofiles.open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(await image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Error async encoding image '{image_path}': {e}")
            return None
