"""
Prompts management module for OpenWebUI Chat Client.
Handles all prompts-related operations including CRUD operations and variable substitution.
"""

import json
import logging
import re
import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptsManager:
    """
    Handles all prompts-related operations for the OpenWebUI client.
    
    This class manages:
    - Prompts listing and retrieval
    - Prompts creation and updates
    - Prompts deletion
    - Variable substitution and parsing
    - Batch operations for prompt management
    """
    
    def __init__(self, base_client):
        """
        Initialize the prompts manager.
        
        Args:
            base_client: The base client instance for making API requests
        """
        self.base_client = base_client
    
    def get_prompts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all prompts for the current user.
        
        Returns:
            A list of prompt objects, or None if failed.
        """
        logger.info("Getting all prompts...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/prompts/",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            prompts = response.json()
            logger.info(f"Successfully retrieved {len(prompts)} prompts.")
            return prompts
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompts: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting prompts: {e}")
            return None

    def get_prompts_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get a detailed list of prompts with user information.
        
        Returns:
            A list of prompt objects with user details, or None if failed.
        """
        logger.info("Getting prompts list with user information...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/prompts/list",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            prompts_list = response.json()
            logger.info(f"Successfully retrieved prompts list with {len(prompts_list)} items.")
            return prompts_list
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompts list: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting prompts list: {e}")
            return None

    def create_prompt(
        self,
        command: str,
        title: str,
        content: str,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new prompt.
        
        Args:
            command: The command identifier (e.g., "/summarize", "/translate")
            title: The display title of the prompt
            content: The prompt content with optional variables
            access_control: Access control settings for the prompt
            
        Returns:
            The created prompt object, or None if creation failed.
        """
        logger.info(f"Creating new prompt with command '{command}'...")
        
        # Validate command format
        if not command.startswith("/"):
            command = f"/{command}"
        
        payload = {
            "command": command,
            "title": title,
            "content": content
        }
        
        if access_control is not None:
            payload["access_control"] = access_control
        
        try:
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/prompts/create",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            prompt = response.json()
            logger.info(f"Successfully created prompt '{command}' with title '{title}'.")
            return prompt
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create prompt '{command}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating prompt '{command}': {e}")
            return None

    def get_prompt_by_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific prompt by its command.
        
        Args:
            command: The command identifier (e.g., "/summarize")
            
        Returns:
            The prompt object, or None if not found or failed.
        """
        logger.info(f"Getting prompt by command '{command}'...")
        
        # Ensure command starts with "/" for consistency but remove it for API call
        if not command.startswith("/"):
            command = f"/{command}"
        
        # Remove leading "/" for API call as the endpoint expects command without it
        api_command = command[1:] if command.startswith("/") else command
        
        try:
            # URL encode the command to handle special characters
            encoded_command = requests.utils.quote(api_command, safe='')
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/prompts/command/{encoded_command}",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            prompt = response.json()
            logger.info(f"Successfully retrieved prompt for command '{command}'.")
            return prompt
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Prompt with command '{command}' not found.")
                return None
            logger.error(f"Failed to get prompt by command '{command}': {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompt by command '{command}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting prompt by command '{command}': {e}")
            return None

    def update_prompt_by_command(
        self,
        command: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing prompt by its command.
        
        Note: This method can only update title and content, not the command itself.
        To change the command, use replace_prompt_by_command() instead.
        
        Args:
            command: The command identifier (e.g., "/summarize")
            title: New title for the prompt (optional)
            content: New content for the prompt (optional)
            access_control: New access control settings (optional)
            
        Returns:
            The updated prompt object, or None if update failed.
        """
        logger.info(f"Updating prompt with command '{command}'...")
        
        # Ensure command starts with "/" for consistency but remove it for API call
        if not command.startswith("/"):
            command = f"/{command}"
        
        # Get current prompt to preserve existing values
        current_prompt = self.get_prompt_by_command(command)
        if not current_prompt:
            logger.error(f"Cannot update prompt '{command}': prompt not found.")
            return None
        
        # Build update payload with provided values or existing ones
        payload = {
            "command": command,
            "title": title if title is not None else current_prompt.get("title", ""),
            "content": content if content is not None else current_prompt.get("content", "")
        }
        
        if access_control is not None:
            payload["access_control"] = access_control
        elif "access_control" in current_prompt:
            payload["access_control"] = current_prompt["access_control"]
        
        # Remove leading "/" for API call as the endpoint expects command without it
        api_command = command[1:] if command.startswith("/") else command
        
        try:
            # URL encode the command to handle special characters
            encoded_command = requests.utils.quote(api_command, safe='')
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/prompts/command/{encoded_command}/update",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            prompt = response.json()
            logger.info(f"Successfully updated prompt '{command}'.")
            return prompt
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update prompt '{command}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating prompt '{command}': {e}")
            return None

    def replace_prompt_by_command(
        self,
        old_command: str,
        new_command: str,
        title: str,
        content: str,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Replace an existing prompt completely (including command) by deleting and recreating.
        
        This method is needed when you want to change the command itself, since the update
        API doesn't allow changing the command identifier.
        
        Args:
            old_command: The existing command identifier (e.g., "/old_summarize")
            new_command: The new command identifier (e.g., "/new_summarize")
            title: New title for the prompt
            content: New content for the prompt
            access_control: New access control settings (optional)
            
        Returns:
            The newly created prompt object, or None if replacement failed.
        """
        logger.info(f"Replacing prompt '{old_command}' with '{new_command}'...")
        
        # First, check if the old prompt exists
        old_prompt = self.get_prompt_by_command(old_command)
        if not old_prompt:
            logger.error(f"Cannot replace prompt '{old_command}': prompt not found.")
            return None
        
        # Check if new command already exists
        if old_command != new_command:
            existing_new = self.get_prompt_by_command(new_command)
            if existing_new:
                logger.error(f"Cannot replace prompt: new command '{new_command}' already exists.")
                return None
        
        # Delete the old prompt
        logger.info(f"Deleting old prompt '{old_command}'...")
        delete_success = self.delete_prompt_by_command(old_command)
        if not delete_success:
            logger.error(f"Failed to delete old prompt '{old_command}'. Replacement aborted.")
            return None
        
        # Create the new prompt
        logger.info(f"Creating new prompt '{new_command}'...")
        new_prompt = self.create_prompt(new_command, title, content, access_control)
        if new_prompt:
            logger.info(f"Successfully replaced prompt '{old_command}' with '{new_command}'.")
            return new_prompt
        else:
            logger.error(f"Failed to create new prompt '{new_command}'. Original prompt was deleted!")
            # Try to restore the original prompt if possible
            logger.info("Attempting to restore original prompt...")
            restored = self.create_prompt(
                old_command,
                old_prompt.get("title", "Restored Prompt"),
                old_prompt.get("content", "Original content was lost during replacement failure"),
                old_prompt.get("access_control")
            )
            if restored:
                logger.info(f"Successfully restored original prompt '{old_command}'.")
            else:
                logger.error(f"Failed to restore original prompt '{old_command}'. Data may be lost!")
            return None

    def delete_prompt_by_command(self, command: str) -> bool:
        """
        Delete a prompt by its command.
        
        Args:
            command: The command identifier (e.g., "/summarize")
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.info(f"Deleting prompt with command '{command}'...")
        
        # Ensure command starts with "/" for consistency but remove it for API call
        if not command.startswith("/"):
            command = f"/{command}"
        
        # Remove leading "/" for API call as the endpoint expects command without it
        api_command = command[1:] if command.startswith("/") else command
        
        try:
            # URL encode the command to handle special characters
            encoded_command = requests.utils.quote(api_command, safe='')
            response = self.base_client.session.delete(
                f"{self.base_client.base_url}/api/v1/prompts/command/{encoded_command}/delete",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result is True:
                logger.info(f"Successfully deleted prompt '{command}'.")
                return True
            else:
                logger.warning(f"Deletion of prompt '{command}' returned: {result}")
                return False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Prompt with command '{command}' not found for deletion.")
                return False
            logger.error(f"Failed to delete prompt '{command}': {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete prompt '{command}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting prompt '{command}': {e}")
            return False

    def search_prompts(
        self, 
        query: Optional[str] = None,
        by_command: bool = False,
        by_title: bool = True,
        by_content: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search prompts by various criteria.
        
        Args:
            query: Search query string
            by_command: Whether to search in command field
            by_title: Whether to search in title field (default: True)
            by_content: Whether to search in content field
            
        Returns:
            List of matching prompt objects.
        """
        logger.info(f"Searching prompts with query '{query}'...")
        
        prompts = self.get_prompts()
        if not prompts:
            return []
        
        if not query:
            return prompts
        
        query_lower = query.lower()
        matching_prompts = []
        
        for prompt in prompts:
            match = False
            
            if by_command and query_lower in prompt.get("command", "").lower():
                match = True
            elif by_title and query_lower in prompt.get("title", "").lower():
                match = True
            elif by_content and query_lower in prompt.get("content", "").lower():
                match = True
            
            if match:
                matching_prompts.append(prompt)
        
        logger.info(f"Found {len(matching_prompts)} prompts matching query '{query}'.")
        return matching_prompts

    def extract_variables(self, content: str) -> List[str]:
        """
        Extract variable names from prompt content.
        
        Args:
            content: The prompt content string
            
        Returns:
            List of variable names found in the content.
        """
        # Pattern to match {{variable_name}} or {{variable_name | type:options}}
        pattern = r'\{\{([^}|]+)(?:\s*\|\s*[^}]+)?\}\}'
        matches = re.findall(pattern, content)
        
        # Clean up variable names (remove whitespace)
        variables = [var.strip() for var in matches]
        return list(set(variables))  # Remove duplicates

    def substitute_variables(
        self, 
        content: str, 
        variables: Dict[str, Any],
        system_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Substitute variables in prompt content.
        
        Args:
            content: The prompt content with variables
            variables: Dictionary of variable name to value mappings
            system_variables: Dictionary of system variables (e.g., USER_NAME, CURRENT_DATE)
            
        Returns:
            Content with variables substituted.
        """
        result = content
        
        # Handle system variables first
        if system_variables:
            for var_name, value in system_variables.items():
                pattern = f"{{{{{var_name}}}}}"
                result = result.replace(pattern, str(value))
        
        # Handle user variables
        for var_name, value in variables.items():
            # Match both simple {{var}} and typed {{var | type:options}} formats
            patterns = [
                f"{{{{{var_name}}}}}",  # Simple format
                f"{{{{{var_name}\\s*\\|[^}}]+}}}}"  # Typed format
            ]
            
            for pattern in patterns:
                result = re.sub(pattern, str(value), result)
        
        return result

    def get_system_variables(self) -> Dict[str, Any]:
        """
        Get current system variables for substitution.
        
        Returns:
            Dictionary of system variable names to current values.
        """
        now = datetime.now()
        
        system_vars = {
            "CURRENT_DATE": now.strftime("%Y-%m-%d"),
            "CURRENT_DATETIME": now.strftime("%Y-%m-%d %H:%M:%S"),
            "CURRENT_TIME": now.strftime("%H:%M:%S"),
            "CURRENT_TIMEZONE": str(now.astimezone().tzinfo),
            "CURRENT_WEEKDAY": now.strftime("%A"),
        }
        
        # Note: USER_NAME, USER_LANGUAGE, USER_LOCATION, CLIPBOARD would need
        # to be provided by the client application as they require context
        
        return system_vars

    def batch_create_prompts(
        self, 
        prompts_data: List[Dict[str, Any]],
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Create multiple prompts in batch.
        
        Args:
            prompts_data: List of prompt data dictionaries
            continue_on_error: Whether to continue creating other prompts if one fails
            
        Returns:
            Dictionary with success/failure results.
        """
        logger.info(f"Batch creating {len(prompts_data)} prompts...")
        
        results = {
            "success": [],
            "failed": [],
            "total": len(prompts_data)
        }
        
        for prompt_data in prompts_data:
            try:
                command = prompt_data.get("command")
                title = prompt_data.get("title")
                content = prompt_data.get("content")
                access_control = prompt_data.get("access_control")
                
                if not all([command, title, content]):
                    logger.error(f"Missing required fields in prompt data: {prompt_data}")
                    results["failed"].append({
                        "data": prompt_data,
                        "error": "Missing required fields (command, title, content)"
                    })
                    continue
                
                created_prompt = self.create_prompt(command, title, content, access_control)
                if created_prompt:
                    results["success"].append(created_prompt)
                else:
                    results["failed"].append({
                        "data": prompt_data,
                        "error": "Failed to create prompt"
                    })
                
            except Exception as e:
                logger.error(f"Error creating prompt from data {prompt_data}: {e}")
                results["failed"].append({
                    "data": prompt_data,
                    "error": str(e)
                })
                
                if not continue_on_error:
                    break
        
        logger.info(f"Batch creation completed. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        return results

    def batch_delete_prompts(
        self, 
        commands: List[str],
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Delete multiple prompts by their commands.
        
        Args:
            commands: List of command identifiers
            continue_on_error: Whether to continue deleting other prompts if one fails
            
        Returns:
            Dictionary with success/failure results.
        """
        logger.info(f"Batch deleting {len(commands)} prompts...")
        
        results = {
            "success": [],
            "failed": [],
            "total": len(commands)
        }
        
        for command in commands:
            try:
                success = self.delete_prompt_by_command(command)
                if success:
                    results["success"].append(command)
                else:
                    results["failed"].append({
                        "command": command,
                        "error": "Failed to delete prompt"
                    })
                    
            except Exception as e:
                logger.error(f"Error deleting prompt '{command}': {e}")
                results["failed"].append({
                    "command": command,
                    "error": str(e)
                })
                
                if not continue_on_error:
                    break
        
        logger.info(f"Batch deletion completed. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        return results