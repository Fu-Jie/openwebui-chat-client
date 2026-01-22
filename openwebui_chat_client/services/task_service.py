"""
Task Service for OpenWebUI Chat Client.

Handles:
- Autonomous task processing with Thought-Action-Observation loop
- Deep research workflows
- Decision making and option selection
- Conversation history management
"""

import json
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openwebui_chat_client.core.base_manager import BaseManager

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)

# Constants
DECISION_CONTEXT_MAX_LENGTH = 10000
DEFAULT_MAX_ITERATIONS = 25


class TaskService(BaseManager):
    """
    Service for handling autonomous task processing.
    
    Extracted from TaskProcessingMixin to provide cleaner architecture
    and better testability.
    """
    
    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the task service.
        
        Args:
            base_client: The base client instance
        """
        super().__init__(base_client)
    
    def get_task_processing_prompt(self) -> str:
        """
        Get the system prompt for task processing.
        
        Returns:
            System prompt string for Thought-Action-Observation loop
        """
        return """You are an advanced AI assistant capable of solving complex tasks through structured reasoning.

**Your Process:**
1. **Thought**: Analyze the current situation and plan your next step
2. **Action**: Take a concrete action (use a tool, ask a question, research)
3. **Observation**: Review the results of your action

**Important Guidelines:**
- Break complex tasks into smaller steps
- Use available tools when appropriate
- Be explicit about your reasoning
- When you have enough information, provide your final answer in this format:

```json
{
    "final_answer": "Your complete answer here",
    "todo_list": [
        {"task": "Task description", "status": "complete|in_progress|pending"}
    ]
}
```

**If you need to present options for the user to choose:**
```json
{
    "decision_needed": "yes",
    "question": "Your question here",
    "options": ["Option 1", "Option 2", "Option 3"]
}
```

Always maintain a TODO list to track your progress through complex tasks."""
    
    def extract_final_answer(self, response_text: str) -> Optional[str]:
        """
        Extract final answer from model response.
        
        Args:
            response_text: Model's response text
            
        Returns:
            Final answer string or None if not found
        """
        final_answer_match = re.search(
            r'```json\s*(\{.*?"final_answer":.*?\})\s*```',
            response_text,
            re.DOTALL,
        )
        
        if final_answer_match:
            try:
                final_json = json.loads(final_answer_match.group(1))
                return final_json.get("final_answer")
            except json.JSONDecodeError:
                self.logger.warning("Found final_answer block but failed to parse JSON")
                return None
        
        return None
    
    def extract_todo_list(self, response_text: str) -> List[Dict[str, str]]:
        """
        Extract TODO list from model response.
        
        Args:
            response_text: Model's response text
            
        Returns:
            List of TODO items with task and status
        """
        # Try to find JSON block with todo_list
        todo_match = re.search(
            r'```json\s*(\{.*?"todo_list":.*?\})\s*```',
            response_text,
            re.DOTALL,
        )
        
        if todo_match:
            try:
                todo_json = json.loads(todo_match.group(1))
                return todo_json.get("todo_list", [])
            except json.JSONDecodeError:
                self.logger.debug("Failed to parse TODO list JSON")
        
        return []
    
    def has_decision_options(self, response_text: str) -> bool:
        """
        Check if response contains decision options.
        
        Args:
            response_text: Model's response text
            
        Returns:
            True if decision options are present
        """
        # Look for decision_needed field
        decision_match = re.search(
            r'```json\s*(\{.*?"decision_needed":.*?\})\s*```',
            response_text,
            re.DOTALL,
        )
        
        if decision_match:
            try:
                decision_json = json.loads(decision_match.group(1))
                return decision_json.get("decision_needed") == "yes"
            except json.JSONDecodeError:
                pass
        
        # Alternative: look for "Options:" pattern
        return bool(re.search(r'Options?:\s*\n', response_text, re.IGNORECASE))
    
    def extract_decision_options(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract decision options from model response.
        
        Args:
            response_text: Model's response text
            
        Returns:
            Dict with question and options, or None
        """
        decision_match = re.search(
            r'```json\s*(\{.*?"decision_needed":.*?\})\s*```',
            response_text,
            re.DOTALL,
        )
        
        if decision_match:
            try:
                decision_json = json.loads(decision_match.group(1))
                if decision_json.get("decision_needed") == "yes":
                    return {
                        "question": decision_json.get("question", "Please choose an option:"),
                        "options": decision_json.get("options", [])
                    }
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse decision options JSON")
        
        return None
    
    def summarize_history(
        self,
        messages: List[Dict[str, str]],
        max_length: int = DECISION_CONTEXT_MAX_LENGTH
    ) -> List[Dict[str, str]]:
        """
        Summarize conversation history to fit within length limit.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_length: Maximum total character length
            
        Returns:
            Summarized message list
        """
        # Calculate current length
        current_length = sum(len(msg.get("content", "")) for msg in messages)
        
        if current_length <= max_length:
            return messages
        
        self.logger.info(
            f"Summarizing history: {current_length} chars -> ~{max_length} chars"
        )
        
        # Keep system message and most recent messages
        summarized = []
        
        # Always keep system message
        if messages and messages[0].get("role") == "system":
            summarized.append(messages[0])
            messages = messages[1:]
        
        # Add recent messages until we approach the limit
        remaining_length = max_length - (
            len(summarized[0]["content"]) if summarized else 0
        )
        
        # Work backwards from most recent
        for msg in reversed(messages):
            msg_length = len(msg.get("content", ""))
            if msg_length < remaining_length:
                summarized.insert(1 if summarized and summarized[0].get("role") == "system" else 0, msg)
                remaining_length -= msg_length
            else:
                # Truncate this message and stop
                truncated_content = msg.get("content", "")[:remaining_length]
                truncated_msg = {
                    "role": msg["role"],
                    "content": f"[Truncated] {truncated_content}..."
                }
                summarized.insert(1 if summarized and summarized[0].get("role") == "system" else 0, truncated_msg)
                break
        
        return summarized
    
    def log_todo_list(self, todo_list: List[Dict[str, str]]) -> None:
        """
        Log the current TODO list in a formatted way.
        
        Args:
            todo_list: List of TODO items
        """
        if not todo_list:
            return
        
        self.logger.info("📋 Current TODO List:")
        for idx, item in enumerate(todo_list, 1):
            task = item.get("task", "Unknown task")
            status = item.get("status", "unknown")
            status_icon = {
                "complete": "✅",
                "in_progress": "🔄",
                "pending": "⏳"
            }.get(status, "❓")
            
            self.logger.info(f"  {idx}. {status_icon} {task} ({status})")
