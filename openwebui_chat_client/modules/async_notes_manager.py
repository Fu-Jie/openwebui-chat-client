"""
Asynchronous notes management module for OpenWebUI Chat Client.
Handles all async notes-related operations including CRUD operations.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncNotesManager:
    """
    Handles all asynchronous notes-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        """
        Initialize the async notes manager.

        Args:
            base_client: The async base client instance for making API requests.
        """
        self.base_client = base_client

    async def get_notes(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously get all notes for the current user."""
        logger.info("Async getting all notes...")
        return await self.base_client._get_json_response("GET", "/api/v1/notes/")

    async def get_notes_list(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously get a simplified list of notes."""
        logger.info("Async getting notes list...")
        return await self.base_client._get_json_response("GET", "/api/v1/notes/list")

    async def create_note(
        self,
        title: str,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Asynchronously create a new note."""
        if not title:
            logger.error("Note title cannot be empty.")
            return None

        logger.info(f"Async creating note with title: '{title}'...")
        note_data = {"title": title}
        if data is not None:
            note_data["data"] = data
        if meta is not None:
            note_data["meta"] = meta
        if access_control is not None:
            note_data["access_control"] = access_control

        return await self.base_client._get_json_response(
            "POST", "/api/v1/notes/create", json_data=note_data
        )

    async def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Asynchronously get a specific note by its ID."""
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return None

        logger.info(f"Async getting note by ID: {note_id}")
        return await self.base_client._get_json_response("GET", f"/api/v1/notes/{note_id}")

    async def update_note_by_id(
        self,
        note_id: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Asynchronously update an existing note by its ID."""
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return None

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if data is not None:
            update_data["data"] = data
        if meta is not None:
            update_data["meta"] = meta
        if access_control is not None:
            update_data["access_control"] = access_control

        if not update_data:
            logger.warning("No update data provided for async note update.")
            # Return the existing note data without making a request
            return await self.get_note_by_id(note_id)

        logger.info(f"Async updating note: {note_id}")
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/notes/{note_id}/update", json_data=update_data
        )

    async def delete_note_by_id(self, note_id: str) -> bool:
        """Asynchronously delete a note by its ID."""
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return False

        logger.info(f"Async deleting note: {note_id}")
        response = await self.base_client._make_request(
            "DELETE", f"/api/v1/notes/{note_id}/delete"
        )

        if response and response.status_code == 200:
            try:
                # Check if response body is `false`
                if response.json() is False:
                    logger.warning(f"Server returned failure status for note deletion: {note_id}")
                    return False
            except Exception:
                # No JSON body, or other content, assume success on 200
                pass
            return True
        return False
