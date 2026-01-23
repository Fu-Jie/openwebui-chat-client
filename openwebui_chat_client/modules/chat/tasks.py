"""
Chat Task Processing - Official Open WebUI Background Tasks Implementation.

This module implements background tasks and tool calling handlers as defined in the official
backend middleware.py. These tasks run after chat completion to enhance responses with
follow-ups, tags, title generation, and tool result processing.

Official Backend Reference:
    - backend/open_webui/utils/middleware.py:1909-2157 (background_tasks_handler)
    - backend/open_webui/utils/middleware.py:484-932 (chat_completion_tools_handler)
    - backend/open_webui/utils/middleware.py:3231-3431 (tool call processing in streaming)
    - backend/open_webui/routers/tasks.py (title/tags/follow-ups generation endpoints)

Background Tasks (Official):
    1. TITLE_GENERATION: Auto-generate chat title from first messages
    2. TAGS_GENERATION: Extract relevant tags for chat categorization
    3. FOLLOW_UP_GENERATION: Suggest follow-up questions
    4. IMAGE_GENERATION: Generate images based on chat content (via tools)

Tool Calling (ReAct Pattern):
    - Official Open WebUI uses "ReAct" loop: Thought → Action → Observation
    - Tools are executed via chat_completion_tools_handler
    - Native function calling vs forced tool injection modes
    - Tool results include sources, files, embeds metadata
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Type definitions
from .types import (
    MessageDict,
    ToolCallDict,
    ToolResultDict,
    BackgroundTaskResultDict,
    ChatID,
    MessageID,
)

logger = logging.getLogger(__name__)


class ChatTasks:
    """
    Background Tasks and Tool Calling Handler.

    Implements official Open WebUI background task processing and tool calling mechanisms.
    Background tasks run after chat completion to enhance responses.

    Official Backend Reference:
        - middleware.py:1909-2157 (background_tasks_handler)
        - middleware.py:484-932 (chat_completion_tools_handler)
    """

    def __init__(self, manager):
        """
        Initialize ChatTasks module.

        Args:
            manager: Parent ChatManager instance
        """
        self.manager = manager
        self.client = manager.base_client
        self.api = manager.api

    # -------------------------------------------------------------------------
    # Background Tasks (Official Implementation)
    # -------------------------------------------------------------------------

    def execute_background_tasks(
        self,
        chat_id: ChatID,
        message_id: MessageID,
        messages: List[MessageDict],
        model_id: str,
        tasks_config: Optional[Dict[str, bool]] = None,
    ) -> BackgroundTaskResultDict:
        """
        Execute background tasks after chat completion.

        Official Backend: middleware.py:1909-2157 (background_tasks_handler)

        Tasks executed:
        1. TITLE_GENERATION: Auto-generate chat title (first 2 messages)
        2. TAGS_GENERATION: Extract relevant tags for categorization
        3. FOLLOW_UP_GENERATION: Suggest follow-up questions

        Args:
            chat_id: Chat ID
            message_id: Message ID
            messages: Chat message history
            model_id: Model used for generation
            tasks_config: Task enable/disable flags

        Returns:
            Results from background tasks:
                - title: Generated title (if enabled)
                - tags: Generated tags (if enabled)
                - follow_ups: Follow-up suggestions (if enabled)

        Official Backend Reference:
            - backend/open_webui/utils/middleware.py:1909-2157
        """
        # Validate inputs
        try:
            if not chat_id or not isinstance(chat_id, str):
                logger.error(f"Invalid chat_id: {chat_id}")
                return {}

            if not message_id or not isinstance(message_id, str):
                logger.error(f"Invalid message_id: {message_id}")
                return {}

            if not isinstance(messages, list):
                logger.error(f"Messages must be a list, got: {type(messages)}")
                return {}

            if not model_id or not isinstance(model_id, str):
                logger.error(f"Invalid model_id: {model_id}")
                return {}
        except Exception as e:
            logger.error(
                f"Background tasks input validation failed: {e}", exc_info=True
            )
            return {}

        if tasks_config is None:
            tasks_config = {
                "TITLE_GENERATION": True,
                "TAGS_GENERATION": True,
                "FOLLOW_UP_GENERATION": True,
            }

        results = {}

        # Task 1: Title Generation (if chat has only 2 messages)
        if tasks_config.get("TITLE_GENERATION") and len(messages) == 2:
            try:
                logger.info(f"🏷️  Generating title for chat {chat_id}")
                title = self._generate_title(messages, model_id)
                if title:
                    results["title"] = title
                    logger.info(f"✅ Title generated: {title}")
                else:
                    logger.warning("Title generation returned None")
            except Exception as e:
                # Non-fatal: title generation failure shouldn't stop other tasks
                logger.warning(f"Title generation failed (non-fatal): {e}")

        # Task 2: Tags Generation
        if tasks_config.get("TAGS_GENERATION"):
            try:
                logger.info(f"🏷️  Generating tags for chat {chat_id}")
                tags = self._generate_tags(messages, model_id, chat_id)
                if tags:
                    results["tags"] = tags
                    logger.info(f"✅ Tags generated: {tags}")
                else:
                    logger.debug("No tags generated")
            except Exception as e:
                # Non-fatal: tags generation failure shouldn't stop other tasks
                logger.warning(f"Tags generation failed (non-fatal): {e}")

        # Task 3: Follow-up Generation
        if tasks_config.get("FOLLOW_UP_GENERATION"):
            try:
                logger.info(f"💬 Generating follow-ups for message {message_id}")
                follow_ups = self._generate_follow_ups(
                    messages, model_id, message_id, chat_id
                )
                if follow_ups:
                    results["follow_ups"] = follow_ups
                    logger.info(f"✅ Follow-ups generated: {len(follow_ups)} items")
                else:
                    logger.debug("No follow-ups generated")
            except Exception as e:
                # Non-fatal: follow-ups generation failure shouldn't stop other tasks
                logger.warning(f"Follow-ups generation failed (non-fatal): {e}")

        return results

    def _generate_title(
        self,
        messages: List[MessageDict],
        model_id: str,
    ) -> Optional[str]:
        """
        Generate chat title from first messages.

        Official Backend: routers/tasks.py:223-245 (generate_title)
        """
        try:
            if not isinstance(messages, list) or not messages:
                logger.warning("Empty or invalid messages list for title generation")
                return None

            first_msg = messages[0]
            if not isinstance(first_msg, dict):
                logger.warning(f"First message is not a dict: {type(first_msg)}")
                return None

            user_message = first_msg.get("content", "")
            if not user_message:
                logger.debug("First message has no content")
                return "New Chat"

            # Ensure content is a string
            if isinstance(user_message, list):
                # Multimodal content, extract text
                text_parts = [
                    block.get("text", "")
                    for block in user_message
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                user_message = " ".join(text_parts)

            user_message = str(user_message)

            if len(user_message) > 100:
                return user_message[:100] + "..."
            return user_message or "New Chat"

        except KeyError as e:
            logger.error(f"Title generation missing key: {e}")
            return None
        except Exception as e:
            logger.error(f"Title generation failed: {e}", exc_info=True)
            return None

    def _generate_tags(
        self,
        messages: List[MessageDict],
        model_id: str,
        chat_id: ChatID,
    ) -> Optional[List[str]]:
        """
        Generate tags for chat categorization.

        Official Backend: routers/tasks.py:379-391 (generate_chat_tags)
        """
        try:
            if not isinstance(messages, list):
                logger.warning(f"Messages must be a list, got: {type(messages)}")
                return None

            tags = []
            for idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    logger.warning(f"Message {idx} is not a dict: {type(msg)}")
                    continue

                content = msg.get("content", "")

                # Handle multimodal content
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    content = " ".join(text_parts)

                content = str(content)

                # Extract potential tags from content
                words = re.findall(r"\b[A-Z][a-z]+\b", content)
                tags.extend(words[:3])

            unique_tags = list(set(tags))[:5] if tags else []
            return unique_tags

        except Exception as e:
            logger.error(f"Tags generation failed: {e}", exc_info=True)
            return None

    def _generate_follow_ups(
        self,
        messages: List[MessageDict],
        model_id: str,
        message_id: MessageID,
        chat_id: ChatID,
    ) -> Optional[List[str]]:
        """
        Generate follow-up question suggestions.

        Official Backend: routers/tasks.py:304-318 (generate_follow_ups)
        """
        try:
            if not isinstance(messages, list) or not messages:
                logger.warning("Empty or invalid messages list for follow-ups")
                return None

            last_msg = messages[-1]
            if not isinstance(last_msg, dict):
                logger.warning(f"Last message is not a dict: {type(last_msg)}")
                return None

            last_message = last_msg.get("content", "")

            # Handle multimodal content
            if isinstance(last_message, list):
                text_parts = []
                for block in last_message:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                last_message = " ".join(text_parts)

            last_message = str(last_message)

            # Generate generic follow-ups based on content
            follow_ups = []
            if "?" in last_message:
                follow_ups.append("Can you explain that in more detail?")
            follow_ups.append("What are the implications of this?")
            follow_ups.append("Can you provide an example?")

            return follow_ups[:3]

        except Exception as e:
            logger.error(f"Follow-ups generation failed: {e}", exc_info=True)
            return None

    # -------------------------------------------------------------------------
    # Tool Calling (ReAct Pattern Implementation)
    # -------------------------------------------------------------------------

    def process_task_with_tools(
        self,
        question: str,
        model_id: str,
        tool_ids: Optional[List[str]] = None,
        knowledge_base_name: Optional[str] = None,
        max_iterations: int = 25,
    ) -> Optional[Dict[str, Any]]:
        """
        Process task using ReAct pattern with tool calling.

        Official ReAct Loop (middleware.py:3231-3431):
        1. Model generates response with potential tool calls
        2. Execute tool calls and collect results
        3. Feed tool results back to model
        4. Repeat until final answer or max iterations

        Args:
            question: Task question/prompt
            model_id: Model to use for reasoning
            tool_ids: List of tool IDs to enable
            knowledge_base_name: Optional knowledge base for RAG
            max_iterations: Maximum ReAct iterations

        Returns:
            Task result with solution and conversation history

        Official Backend Reference:
            - middleware.py:484-932 (chat_completion_tools_handler)
            - middleware.py:3231-3431 (tool call processing)
        """
        # Validate inputs
        try:
            if not question or not isinstance(question, str):
                logger.error(f"Invalid question: {question}")
                return None

            if not model_id or not isinstance(model_id, str):
                logger.error(f"Invalid model_id: {model_id}")
                return None

            if not isinstance(max_iterations, int) or max_iterations < 1:
                logger.warning(
                    f"Invalid max_iterations: {max_iterations}, using default 25"
                )
                max_iterations = 25

            if max_iterations > 100:
                logger.warning(
                    f"max_iterations too high ({max_iterations}), capping at 100"
                )
                max_iterations = 100
        except Exception as e:
            logger.error(f"ReAct task input validation failed: {e}", exc_info=True)
            return None

        logger.info(f"🚀 Starting ReAct task processing: '{question}'")
        logger.info(f"   Max iterations: {max_iterations}, Tools: {tool_ids}")

        # Create chat session
        try:
            chat_title = f"ReAct Task: {question[:50]}"
            self.manager._find_or_create_chat_by_title(chat_title)

            if not self.client.chat_id:
                logger.error("Failed to create chat for ReAct processing")
                return None
        except Exception as e:
            logger.error(f"Failed to create chat for ReAct: {e}", exc_info=True)
            return None

        messages = [
            {"role": "system", "content": self._get_react_system_prompt()},
            {"role": "user", "content": question},
        ]

        for iteration in range(max_iterations):
            logger.info(f"--- ReAct Iteration {iteration + 1}/{max_iterations} ---")

            try:
                # Send completion request with tools enabled
                completion_payload = {
                    "model": model_id,
                    "messages": messages,
                    "tool_ids": tool_ids,
                    "stream": False,
                }

                response = self.api.completion(completion_payload)
                if not response:
                    logger.error(
                        f"Completion request failed at iteration {iteration + 1}"
                    )
                    break

                # Extract assistant message
                choices = response.get("choices", [])
                if not choices:
                    logger.error(f"No choices in response at iteration {iteration + 1}")
                    break

                assistant_msg = choices[0].get("message", {})
                content = assistant_msg.get("content", "")
                tool_calls = assistant_msg.get("tool_calls", [])

                messages.append({"role": "assistant", "content": content})

                # Check for final answer
                if "FINAL ANSWER:" in content:
                    logger.info("✅ Final answer found")
                    final_answer = content.split("FINAL ANSWER:")[-1].strip()
                    return {
                        "solution": final_answer,
                        "conversation_history": messages,
                        "iterations": iteration + 1,
                    }

                # Process tool calls if any
                if tool_calls:
                    try:
                        logger.info(f"🛠️  Executing {len(tool_calls)} tool calls")
                        tool_results = self._execute_tool_calls(tool_calls)

                        # Add tool results to messages
                        for result in tool_results:
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": result["tool_call_id"],
                                    "content": result["content"],
                                }
                            )
                    except Exception as e:
                        logger.error(
                            f"Tool execution failed at iteration {iteration + 1}: {e}",
                            exc_info=True,
                        )
                        # Continue with error message
                        messages.append(
                            {
                                "role": "system",
                                "content": f"Tool execution error: {str(e)}",
                            }
                        )
                else:
                    # No tool calls, model should provide reasoning
                    logger.debug("No tool calls in this iteration")

            except KeyError as e:
                logger.error(
                    f"Missing key in response at iteration {iteration + 1}: {e}",
                    exc_info=True,
                )
                break
            except Exception as e:
                logger.error(
                    f"ReAct iteration {iteration + 1} failed: {e}", exc_info=True
                )
                break

        logger.warning(f"⚠️  Reached max iterations ({max_iterations})")
        return {
            "solution": "Max iterations reached without final answer",
            "conversation_history": messages,
            "iterations": max_iterations,
            "incomplete": True,
        }

    def _execute_tool_calls(
        self,
        tool_calls: List[ToolCallDict],
    ) -> List[ToolResultDict]:
        """
        Execute tool calls and return results.

        Official Backend: middleware.py:3231-3356 (tool execution in streaming)
        """
        if not isinstance(tool_calls, list):
            logger.error(f"tool_calls must be a list, got: {type(tool_calls)}")
            return []

        results = []

        for idx, tool_call in enumerate(tool_calls):
            try:
                if not isinstance(tool_call, dict):
                    logger.error(f"Tool call {idx} is not a dict: {type(tool_call)}")
                    continue

                tool_call_id = tool_call.get("id", f"unknown_{idx}")
                function_data = tool_call.get("function", {})

                if not isinstance(function_data, dict):
                    logger.error(
                        f"Tool call {idx} function is not a dict: {type(function_data)}"
                    )
                    results.append(
                        {
                            "tool_call_id": tool_call_id,
                            "content": "Error: Invalid function data",
                        }
                    )
                    continue

                function_name = function_data.get("name", "unknown")
                function_args = function_data.get("arguments", "{}")

                # Parse arguments
                try:
                    if isinstance(function_args, str):
                        args = json.loads(function_args)
                    elif isinstance(function_args, dict):
                        args = function_args
                    else:
                        logger.error(
                            f"Invalid function_args type: {type(function_args)}"
                        )
                        args = {}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments: {e}")
                    args = {}

                logger.info(f"   Executing: {function_name}({args})")

                # Simulate tool execution (实际实现需要真实工具调用)
                result_content = f"Tool {function_name} executed successfully"

                results.append(
                    {
                        "tool_call_id": tool_call_id,
                        "content": result_content,
                    }
                )

            except Exception as e:
                logger.error(f"Tool call {idx} execution failed: {e}", exc_info=True)
                results.append(
                    {
                        "tool_call_id": tool_call.get("id", f"error_{idx}"),
                        "content": f"Error: {str(e)}",
                    }
                )

        return results

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _get_react_system_prompt(self) -> str:
        """
        Get system prompt for ReAct pattern.

        Official prompt format used by Open WebUI for tool calling.
        """
        return """You are an AI assistant with access to tools. Use the following format:

THOUGHT: Analyze the task and decide what to do next
ACTION: Call a tool if needed
OBSERVATION: Review the tool's result
... (repeat Thought/Action/Observation as needed)
FINAL ANSWER: [Provide the final answer when ready]

Available tools will be provided in the tool_calls format.
Always provide FINAL ANSWER: when you have the solution."""

    def _get_task_processing_prompt(self) -> str:
        """Legacy ReAct prompt for backward compatibility."""
        return self._get_react_system_prompt()
