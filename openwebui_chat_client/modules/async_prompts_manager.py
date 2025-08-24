"""
Asynchronous prompts management module for OpenWebUI Chat Client.
Handles all async prompts-related operations including CRUD and variable substitution.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncPromptsManager:
    """
    Handles all asynchronous prompts-related operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        """
        Initialize the async prompts manager.

        Args:
            base_client: The async base client instance for making API requests.
        """
        self.base_client = base_client

    async def get_prompts(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously get all prompts for the current user."""
        logger.info("Async getting all prompts...")
        return await self.base_client._get_json_response("GET", "/api/v1/prompts/")

    async def create_prompt(
        self,
        command: str,
        title: str,
        content: str,
        access_control: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Asynchronously create a new prompt."""
        if not command.startswith("/"):
            command = f"/{command}"

        payload = {"command": command, "title": title, "content": content}
        if access_control:
            payload["access_control"] = access_control

        logger.info(f"Async creating new prompt with command '{command}'...")
        return await self.base_client._get_json_response(
            "POST", "/api/v1/prompts/create", json_data=payload
        )

    async def delete_prompt_by_command(self, command: str) -> bool:
        """Asynchronously delete a prompt by its command."""
        if not command.startswith("/"):
            command = f"/{command}"
        api_command = command[1:]

        logger.info(f"Async deleting prompt with command '{command}'...")
        response = await self.base_client._make_request(
            "DELETE", f"/api/v1/prompts/command/{api_command}/delete"
        )
        return response is not None and response.status_code == 200

    async def batch_delete_prompts(
        self,
        commands: List[str],
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """Asynchronously delete multiple prompts by their commands."""
        logger.info(f"Async batch deleting {len(commands)} prompts...")

        tasks = [self.delete_prompt_by_command(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_commands = [commands[i] for i, r in enumerate(results) if r is True]
        failed_commands = [
            {"command": commands[i], "error": str(r)}
            for i, r in enumerate(results) if r is not True
        ]

        return {
            "success": success_commands,
            "failed": failed_commands,
            "total": len(commands)
        }

    # --- Synchronous/Static Helper Methods ---

    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract variable names from prompt content."""
        pattern = r'\{\{([^}|]+)(?:\s*\|\s*[^}]+)?\}\}'
        matches = re.findall(pattern, content)
        variables = [var.strip() for var in matches]
        return list(set(variables))

    @staticmethod
    def substitute_variables(
        content: str,
        variables: Dict[str, Any],
        system_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Substitute variables in prompt content."""
        result = content
        if system_variables:
            for var_name, value in system_variables.items():
                result = result.replace(f"{{{{{var_name}}}}}", str(value))

        for var_name, value in variables.items():
            patterns = [
                f"{{{{{var_name}}}}}",
                f"{{{{{var_name}\\s*\\|[^}}]+}}}}"
            ]
            for pattern in patterns:
                result = re.sub(pattern, str(value), result)
        return result

    @staticmethod
    def get_system_variables() -> Dict[str, Any]:
        """Get current system variables for substitution."""
        now = datetime.now()
        return {
            "CURRENT_DATE": now.strftime("%Y-%m-%d"),
            "CURRENT_DATETIME": now.strftime("%Y-%m-%d %H:%M:%S"),
            "CURRENT_TIME": now.strftime("%H:%M:%S"),
            "CURRENT_TIMEZONE": str(now.astimezone().tzinfo),
            "CURRENT_WEEKDAY": now.strftime("%A"),
        }
