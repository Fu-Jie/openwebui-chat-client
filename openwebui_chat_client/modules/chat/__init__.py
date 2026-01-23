"""
Chat module - Core chat functionality.

This package contains all chat-related components organized by responsibility:
- manager: High-level ChatManager facade
- api: HTTP communication layer
- workflow: 3-step chat workflow orchestration
- payloads: Message and payload construction
- rag: RAG (Retrieval-Augmented Generation) logic
- parallel: Parallel multi-model execution
- tasks: Task processing (ReAct & Deep Research)
- actions: Action triggering
"""

from .manager import ChatManager

__all__ = ["ChatManager"]
