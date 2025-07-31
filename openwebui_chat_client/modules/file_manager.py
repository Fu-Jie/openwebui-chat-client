"""
File management module for OpenWebUI Chat Client.
Handles file uploads, image encoding, and file-related operations.
"""

import base64
import logging
import os
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class FileManager:
    """
    Handles all file-related operations for the OpenWebUI client.
    
    This class manages:
    - File uploads to the server
    - Image encoding for multimodal chat
    - File validation and processing
    """
    
    def __init__(self, base_client):
        """
        Initialize the file manager.
        
        Args:
            base_client: The base client instance for making API requests
        """
        self.base_client = base_client
    
    def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to the OpenWebUI server.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Dictionary containing file information including ID, or None if upload failed
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            return None
            
        url = f"{self.base_client.base_url}/api/v1/files/"
        file_name = os.path.basename(file_path)
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f)}
                headers = {"Authorization": self.base_client.session.headers["Authorization"]}
                logger.info(f"Uploading file '{file_name}'...")
                response = self.base_client.session.post(url, headers=headers, files=files)
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
        except Exception as e:
            logger.error(f"Unexpected error uploading file '{file_name}': {e}")
            return None
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64 format for use in multimodal chat.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string with data URL format, or None if encoding failed
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
            
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Error encoding image '{image_path}': {e}")
            return None
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Validate that a file exists at the given path.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file exists, False otherwise
        """
        exists = os.path.exists(file_path)
        if not exists:
            logger.warning(f"File not found: {file_path}")
        return exists
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information or None if file doesn't exist
        """
        if not self.validate_file_exists(file_path):
            return None
        
        try:
            stat = os.stat(file_path)
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "extension": os.path.splitext(file_path)[1].lower(),
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error getting file info for '{file_path}': {e}")
            return None
    
    def prepare_image_messages(self, image_paths: List[str]) -> List[str]:
        """
        Prepare a list of image paths by encoding them to base64.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of base64 encoded image strings
        """
        if not image_paths:
            return []
        
        encoded_images = []
        for image_path in image_paths:
            encoded = self.encode_image_to_base64(image_path)
            if encoded:
                encoded_images.append(encoded)
            else:
                logger.warning(f"Skipping invalid image: {image_path}")
        
        return encoded_images
    
    def batch_upload_files(self, file_paths: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Upload multiple files and return results.
        
        Args:
            file_paths: List of file paths to upload
            
        Returns:
            Dictionary mapping file paths to upload results (or None if failed)
        """
        if not file_paths:
            return {}
        
        results = {}
        
        for file_path in file_paths:
            logger.info(f"Processing file: {file_path}")
            result = self.upload_file(file_path)
            results[file_path] = result
            
            if result:
                logger.info(f"  ✅ Upload successful")
            else:
                logger.error(f"  ❌ Upload failed")
        
        successful = sum(1 for r in results.values() if r is not None)
        failed = len(results) - successful
        logger.info(f"Batch upload completed: {successful} successful, {failed} failed")
        
        return results