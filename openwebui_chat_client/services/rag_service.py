"""
RAG (Retrieval-Augmented Generation) Service for OpenWebUI Chat Client.

Handles:
- File upload and processing for RAG
- Knowledge base collection processing
- RAG payload generation for API and storage
"""

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Any

from openwebui_chat_client.core.base_manager import BaseManager

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class RAGService(BaseManager):
    """
    Service for handling RAG (Retrieval-Augmented Generation) operations.

    Extracted from ChatCoreMixin._handle_rag_references to provide
    a cleaner, more testable architecture.
    """

    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the RAG service.

        Args:
            base_client: The base client instance
        """
        super().__init__(base_client)

    def handle_rag_references(
        self,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Handle RAG file and collection processing.

        This is the main public method that coordinates file and KB processing.

        Args:
            rag_files: List of file paths to upload and use for RAG
            rag_collections: List of knowledge base collection names to use

        Returns:
            Tuple of (api_payload, storage_payload):
                - api_payload: Data to send in API requests
                - storage_payload: Data to store in chat metadata
        """
        api_payload: List[Dict[str, Any]] = []
        storage_payload: List[Dict[str, Any]] = []

        # Process files
        if rag_files:
            file_api, file_storage = self.process_rag_files(rag_files)
            api_payload.extend(file_api)
            storage_payload.extend(file_storage)

        # Process knowledge base collections
        if rag_collections:
            kb_api, kb_storage = self.process_rag_collections(rag_collections)
            api_payload.extend(kb_api)
            storage_payload.extend(kb_storage)

        return api_payload, storage_payload

    def process_rag_files(
        self, file_paths: List[str]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process RAG files by uploading them.

        Args:
            file_paths: List of file paths to upload

        Returns:
            Tuple of (api_payload, storage_payload) for the files
        """
        api_payload: List[Dict[str, Any]] = []
        storage_payload: List[Dict[str, Any]] = []

        self.logger.info(f"Processing {len(file_paths)} RAG files...")

        for file_path in file_paths:
            file_obj = self._upload_file(file_path)

            if file_obj:
                api_payload.append({"type": "file", "id": file_obj["id"]})
                storage_payload.append({"type": "file", "file": file_obj, **file_obj})
                self.logger.debug(f"Successfully processed file: {file_path}")
            else:
                self.logger.warning(f"Failed to upload RAG file: {file_path}")

        return api_payload, storage_payload

    def process_rag_collections(
        self, kb_names: List[str]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process RAG knowledge base collections.

        Args:
            kb_names: List of knowledge base names

        Returns:
            Tuple of (api_payload, storage_payload) for the collections
        """
        api_payload: List[Dict[str, Any]] = []
        storage_payload: List[Dict[str, Any]] = []

        self.logger.info(
            f"Processing {len(kb_names)} RAG knowledge base collections..."
        )

        for kb_name in kb_names:
            # Get knowledge base summary
            kb_summary = self._get_knowledge_base_by_name(kb_name)

            if not kb_summary:
                self.logger.warning(
                    f"Could not find knowledge base '{kb_name}', it will be skipped."
                )
                continue

            # Get detailed knowledge base info
            kb_details = self._get_knowledge_base_details(kb_summary["id"])

            if not kb_details:
                self.logger.warning(
                    f"Could not get details for knowledge base '{kb_name}', it will be skipped."
                )
                continue

            # Extract file IDs from the knowledge base
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

            self.logger.debug(
                f"Successfully processed KB '{kb_name}' with {len(file_ids)} files"
            )

        return api_payload, storage_payload

    def _upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file for RAG processing.

        Tries to use parent client's _upload_file method if available,
        otherwise falls back to base client.

        Args:
            file_path: Path to the file to upload

        Returns:
            File object dict or None on failure
        """
        parent_client = getattr(self.base_client, "_parent_client", None)

        # Try parent client first
        if parent_client and hasattr(parent_client, "_upload_file"):
            try:
                return parent_client._upload_file(file_path)
            except Exception as e:
                self.logger.warning(f"Parent client _upload_file failed: {e}")

        # Fallback to base client
        if hasattr(self.base_client, "_upload_file"):
            try:
                return self.base_client._upload_file(file_path)
            except Exception as e:
                self.logger.error(f"Base client _upload_file failed: {e}")
                return None

        self.logger.error("No _upload_file method available")
        return None

    def _get_knowledge_base_by_name(self, kb_name: str) -> Optional[Dict[str, Any]]:
        """
        Get knowledge base summary by name.

        Args:
            kb_name: Knowledge base name

        Returns:
            Knowledge base summary dict or None
        """
        parent_client = getattr(self.base_client, "_parent_client", None)

        # Try parent client first
        if parent_client and hasattr(parent_client, "get_knowledge_base_by_name"):
            try:
                return parent_client.get_knowledge_base_by_name(kb_name)
            except Exception as e:
                self.logger.warning(
                    f"Parent client get_knowledge_base_by_name failed: {e}"
                )

        # Try base client's parent
        if self.base_client._parent_client and hasattr(
            self.base_client._parent_client, "get_knowledge_base_by_name"
        ):
            try:
                return self.base_client._parent_client.get_knowledge_base_by_name(
                    kb_name
                )
            except Exception as e:
                self.logger.warning(
                    f"Base client parent get_knowledge_base_by_name failed: {e}"
                )

        return None

    def _get_knowledge_base_details(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed knowledge base information.

        Args:
            kb_id: Knowledge base ID

        Returns:
            Knowledge base details dict or None
        """
        parent_client = getattr(self.base_client, "_parent_client", None)

        # Try parent client first
        if parent_client and hasattr(parent_client, "_get_knowledge_base_details"):
            try:
                return parent_client._get_knowledge_base_details(kb_id)
            except Exception as e:
                self.logger.warning(
                    f"Parent client _get_knowledge_base_details failed: {e}"
                )

        # Try base client's parent
        if self.base_client._parent_client and hasattr(
            self.base_client._parent_client, "_get_knowledge_base_details"
        ):
            try:
                return self.base_client._parent_client._get_knowledge_base_details(
                    kb_id
                )
            except Exception as e:
                self.logger.warning(
                    f"Base client parent _get_knowledge_base_details failed: {e}"
                )

        return None
