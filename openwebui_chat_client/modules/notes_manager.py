"""
Notes management module for OpenWebUI Chat Client.
Handles all notes-related operations including CRUD operations.
"""

import json
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class NotesManager:
    """
    Handles all notes-related operations for the OpenWebUI client.
    
    This class manages:
    - Notes listing and retrieval
    - Notes creation and updates
    - Notes deletion
    - Notes metadata management
    """
    
    def __init__(self, base_client):
        """
        Initialize the notes manager.
        
        Args:
            base_client: The base client instance for making API requests
        """
        self.base_client = base_client
    
    def get_notes(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all notes for the current user.
        
        Returns:
            A list of note objects with user information, or None if failed.
        """
        logger.info("Getting all notes...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/notes/",
                headers=self.base_client.json_headers
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
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/notes/list",
                headers=self.base_client.json_headers
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
            title: The title of the note
            data: The note content data (e.g., {"text": "content"})
            meta: Additional metadata for the note
            access_control: Access control settings for the note
            
        Returns:
            The created note object, or None if creation failed.
        """
        logger.info(f"Creating note with title: '{title}'...")
        
        if not title:
            logger.error("Note title cannot be empty.")
            return None
        
        note_data = {"title": title}
        
        if data is not None:
            note_data["data"] = data
        if meta is not None:
            note_data["meta"] = meta
        if access_control is not None:
            note_data["access_control"] = access_control
        
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/notes/create",
                json=note_data,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            created_note = response.json()
            logger.info(f"Successfully created note: {created_note.get('id', 'unknown')}")
            return created_note
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create note '{title}': {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating note '{title}': {e}")
            return None

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific note by its ID.
        
        Args:
            note_id: The ID of the note to retrieve
            
        Returns:
            The note object, or None if not found or failed.
        """
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return None
        
        logger.info(f"Getting note by ID: {note_id}")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/notes/{note_id}",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            note = response.json()
            logger.info(f"Successfully retrieved note: {note_id}")
            return note
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get note {note_id}: {e}")
            if e.response is not None and e.response.status_code == 404:
                logger.error(f"Note {note_id} not found.")
            elif e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting note {note_id}: {e}")
            return None

    def update_note_by_id(
        self,
        note_id: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing note by its ID.
        
        Args:
            note_id: The ID of the note to update
            title: New title for the note (optional)
            data: New content data for the note (optional)
            meta: New metadata for the note (optional)
            access_control: New access control settings (optional)
            
        Returns:
            The updated note object, or None if update failed.
        """
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return None
        
        logger.info(f"Updating note: {note_id}")
        
        # Build update data with only provided fields
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
            logger.warning("No update data provided for note update.")
            return None
        
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/notes/{note_id}/update",
                json=update_data,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            updated_note = response.json()
            logger.info(f"Successfully updated note: {note_id}")
            return updated_note
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update note {note_id}: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating note {note_id}: {e}")
            return None

    def delete_note_by_id(self, note_id: str) -> bool:
        """
        Delete a note by its ID.
        
        Args:
            note_id: The ID of the note to delete
            
        Returns:
            True if the note was successfully deleted, False otherwise.
        """
        if not note_id:
            logger.error("Note ID cannot be empty.")
            return False
        
        logger.info(f"Deleting note: {note_id}")
        try:
            response = self.base_client.session.delete(
                f"{self.base_client.base_url}/api/v1/notes/{note_id}/delete",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            
            # Check response content for success indication
            try:
                response_data = response.json()
                # If the response explicitly indicates failure, return False
                if response_data is False:
                    logger.warning(f"Server returned failure status for note deletion: {note_id}")
                    return False
            except (ValueError, TypeError):
                # Response might not be JSON, which is fine for delete operations
                pass
            
            logger.info(f"Successfully deleted note: {note_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete note {note_id}: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting note {note_id}: {e}")
            return False
            return False