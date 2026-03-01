"""
Type definitions for Chat module - Official Open WebUI Schema Compliance.

This module defines TypedDict structures that strictly follow the official
Open WebUI backend models and API contracts.

Official Backend References:
    - backend/open_webui/models/chats.py (ChatModel, MessageStats)
    - backend/open_webui/models/messages.py (Message)
    - backend/open_webui/main.py (ChatCompletionForm, ChatCompletedForm)
    - backend/open_webui/routers/chats.py (ChatForm, ChatTitleForm, etc.)

Type Conventions:
    - Use TypedDict for structured data (JSON-like objects)
    - Use NotRequired for optional fields (Python 3.11+)
    - Use Literal for fixed value choices
    - Use Union for multiple possible types
    - All timestamp fields are int (Unix epoch seconds)
    - All ID fields are str (UUID format)
"""

from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import TypedDict, NotRequired

# =============================================================================
# Message Types
# =============================================================================


class MessageDict(TypedDict, total=False):
    """
    Message object following Open WebUI schema.

    Official Backend: backend/open_webui/models/chats.py (MessageStats)

    Message structure forms a tree/graph:
    - parentId: Links to parent message (forms chain)
    - childrenIds: List of child message IDs (branching)
    - currentId in history points to active leaf node

    Required fields:
        id: Unique message identifier (UUID)
        role: "user" | "assistant" | "system"
        content: Message content (string or content blocks)
        timestamp: Unix epoch timestamp (seconds)

    Optional fields:
        parentId: Parent message ID (None for root messages)
        childrenIds: List of child message IDs (empty array by default)
        model: Model identifier (required for assistant messages)
        files: Attached files (images, documents, etc.)
        sources: Citation sources (URLs, documents, etc.)
        info: Metadata (tokens, timing, model info, etc.)
        done: Completion status (for assistant messages)
        error: Error message if message failed
        statusHistory: Status change history
        annotation: User annotations/edits
        userContext: User-provided context
        context: System context
        code_executions: Code execution results
        tool_calls: Tool invocations (function calling)
        ... (additional fields as needed)
    """

    # Required fields
    id: str
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[Dict[str, Any]]]
    timestamp: int

    # Graph structure
    parentId: NotRequired[Optional[str]]
    childrenIds: NotRequired[List[str]]

    # Metadata
    model: NotRequired[str]
    files: NotRequired[List[Dict[str, Any]]]
    sources: NotRequired[List[str]]
    info: NotRequired[Dict[str, Any]]

    # Status
    done: NotRequired[bool]
    error: NotRequired[str]
    statusHistory: NotRequired[List[str]]

    # Annotations
    annotation: NotRequired[Dict[str, Any]]
    userContext: NotRequired[str]
    context: NotRequired[str]

    # Tool calling
    tool_calls: NotRequired[List[Dict[str, Any]]]
    code_executions: NotRequired[List[Dict[str, Any]]]


class ChatHistoryDict(TypedDict):
    """
    Chat history structure (graph-based message tree).

    Official Backend: backend/open_webui/models/chats.py (ChatBody.history)

    History is stored as a graph:
    - messages: Dict mapping message ID to message object
    - currentId: Points to the active leaf message

    This allows branching conversations where users can explore
    different conversation paths from any message.
    """

    currentId: str
    messages: Dict[str, MessageDict]


class ChatBodyDict(TypedDict, total=False):
    """
    Inner chat object (chat.chat field).

    Official Backend: backend/open_webui/models/chats.py (ChatBody)

    This is the core chat data structure that contains:
    - title: Chat title
    - history: Message tree structure
    - models: List of models used in chat
    - params: Model parameters
    """

    # Required
    title: str
    history: ChatHistoryDict

    # Optional
    models: NotRequired[List[str]]
    params: NotRequired[Dict[str, Any]]


# =============================================================================
# Chat Types
# =============================================================================


class ChatDict(TypedDict, total=False):
    """
    Complete chat object (database model).

    Official Backend: backend/open_webui/models/chats.py (ChatModel)

    Top-level chat object stored in database with:
    - id: Chat identifier
    - user_id: Owner user ID
    - title: Chat title
    - chat: Inner chat body (ChatBodyDict)
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - share_id: Public share identifier (if shared)
    - archived: Archive status
    - pinned: Pin status
    - meta: Metadata (tags, etc.)
    - folder_id: Folder assignment
    """

    # Identifiers
    id: str
    user_id: NotRequired[str]

    # Content
    title: str
    chat: ChatBodyDict

    # Timestamps
    created_at: NotRequired[int]
    updated_at: NotRequired[int]

    # State
    share_id: NotRequired[Optional[str]]
    archived: NotRequired[bool]
    pinned: NotRequired[bool]

    # Organization
    meta: NotRequired[Dict[str, Any]]
    folder_id: NotRequired[Optional[str]]


class ChatFormDict(TypedDict, total=False):
    """
    Chat form for creation/update.

    Official Backend: backend/open_webui/routers/chats.py (ChatForm)

    Used in POST /api/v1/chats/new and POST /api/v1/chats/{id}
    """

    chat: ChatBodyDict
    folder_id: NotRequired[Optional[str]]


# =============================================================================
# API Request/Response Types
# =============================================================================


class CompletionPayloadDict(TypedDict, total=False):
    """
    Chat completion request payload.

    Official Backend: backend/open_webui/main.py (ChatCompletionForm)

    Used in POST /api/chat/completions

    Required:
        model: Model identifier
        messages: Conversation messages (OpenAI format)

    Optional:
        stream: Enable streaming
        chat_id: Chat ID for persistence
        metadata: Tracking metadata
        files: File attachments
        tool_ids: Enabled tool IDs
        temperature, max_tokens, etc.: Model parameters
    """

    # Required
    model: str
    messages: List[Dict[str, Any]]

    # Streaming
    stream: NotRequired[bool]

    # Metadata
    chat_id: NotRequired[Optional[str]]
    message_id: NotRequired[str]
    parent_message_id: NotRequired[Optional[str]]
    session_id: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]

    # Attachments
    files: NotRequired[List[Dict[str, Any]]]
    tool_ids: NotRequired[List[str]]
    knowledge_base_name: NotRequired[str]

    # Model parameters
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    top_p: NotRequired[float]
    frequency_penalty: NotRequired[float]
    presence_penalty: NotRequired[float]
    stop: NotRequired[Union[str, List[str]]]

    # Additional features
    filter_ids: NotRequired[List[str]]
    features: NotRequired[Dict[str, Any]]
    variables: NotRequired[Dict[str, Any]]


class CompletedPayloadDict(TypedDict, total=False):
    """
    Chat completed request payload.

    Official Backend: backend/open_webui/main.py (ChatCompletedForm)

    Used in POST /api/chat/completed

    Sent after completion to trigger outlet filters and background tasks.

    Note: Backend uses 'id' field for chat_id, not 'chat_id'.
    """

    # Required
    id: str  # Chat ID (note: field name is 'id', not 'chat_id')
    message_id: str

    # Optional
    model: NotRequired[str]
    messages: NotRequired[List[Dict[str, Any]]]
    session_id: NotRequired[str]


class MetadataDict(TypedDict, total=False):
    """
    Metadata for completion requests.

    Tracks chat context and session information.
    """

    chat_id: str
    message_id: str
    parent_message_id: NotRequired[Optional[str]]
    session_id: NotRequired[str]
    filter_ids: NotRequired[List[str]]
    tool_ids: NotRequired[Optional[List[str]]]
    files: NotRequired[Optional[List[Dict[str, Any]]]]
    features: NotRequired[Dict[str, Any]]
    variables: NotRequired[Dict[str, Any]]


class ResponseDict(TypedDict, total=False):
    """
    Completion API response (OpenAI format).

    Standard OpenAI Chat Completion response structure.
    """

    id: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: NotRequired[Dict[str, int]]
    system_fingerprint: NotRequired[str]


class ChoiceDict(TypedDict, total=False):
    """
    Single choice in completion response.
    """

    index: int
    message: MessageDict
    finish_reason: NotRequired[
        Literal["stop", "length", "tool_calls", "content_filter"]
    ]
    logprobs: NotRequired[Optional[Dict[str, Any]]]


# =============================================================================
# File Types
# =============================================================================


class FileDict(TypedDict, total=False):
    """
    File object for attachments.

    Official Backend: backend/open_webui/models/files.py (FileModel)
    """

    # Required
    id: str
    filename: str

    # Metadata
    user_id: NotRequired[str]
    hash: NotRequired[str]
    meta: NotRequired[Dict[str, Any]]

    # Timestamps
    created_at: NotRequired[int]
    updated_at: NotRequired[int]

    # File properties
    type: NotRequired[str]
    size: NotRequired[int]
    path: NotRequired[str]
    data: NotRequired[Dict[str, Any]]


# =============================================================================
# Knowledge Base Types
# =============================================================================


class KnowledgeDict(TypedDict, total=False):
    """
    Knowledge base object.

    Official Backend: backend/open_webui/models/knowledge.py (KnowledgeModel)
    """

    # Required
    id: str
    name: str

    # Optional
    description: NotRequired[str]
    data: NotRequired[Dict[str, Any]]
    meta: NotRequired[Dict[str, Any]]
    user_id: NotRequired[str]
    created_at: NotRequired[int]
    updated_at: NotRequired[int]


# =============================================================================
# Tool Calling Types
# =============================================================================


class ToolCallDict(TypedDict):
    """
    Tool call object (function calling).

    Official: OpenAI function calling format
    """

    id: str
    type: Literal["function"]
    function: "FunctionCallDict"


class FunctionCallDict(TypedDict):
    """Function call details."""

    name: str
    arguments: str  # JSON string


class ToolResultDict(TypedDict):
    """Tool execution result."""

    tool_call_id: str
    content: str


# =============================================================================
# Tag Types
# =============================================================================


class TagDict(TypedDict):
    """
    Tag object.

    Official Backend: backend/open_webui/models/tags.py (TagModel)
    """

    id: str
    name: str
    user_id: str
    data: NotRequired[Dict[str, Any]]


# =============================================================================
# Folder Types
# =============================================================================


class FolderDict(TypedDict, total=False):
    """
    Folder object.

    Official Backend: backend/open_webui/models/folders.py (FolderModel)
    """

    id: str
    name: str
    user_id: str
    parent_id: NotRequired[Optional[str]]
    items: NotRequired[List[str]]
    meta: NotRequired[Dict[str, Any]]
    is_expanded: NotRequired[bool]
    created_at: NotRequired[int]
    updated_at: NotRequired[int]


# =============================================================================
# Background Task Types
# =============================================================================


class BackgroundTaskResultDict(TypedDict, total=False):
    """
    Background task execution results.

    Results from post-completion background tasks.
    """

    title: NotRequired[str]
    tags: NotRequired[List[str]]
    follow_ups: NotRequired[List[str]]
    images: NotRequired[List[Dict[str, Any]]]


# =============================================================================
# Workflow Types
# =============================================================================


class WorkflowResultDict(TypedDict, total=False):
    """
    Complete workflow execution result.

    Returned by execute_full_turn() with all steps combined.
    """

    success: bool
    chat_id: str
    metadata: MetadataDict
    user_message: MessageDict
    assistant_message: NotRequired[Dict[str, Any]]
    completion_response: NotRequired[ResponseDict]
    completed_response: NotRequired[Optional[Dict[str, Any]]]
    chat_state: NotRequired[ChatDict]
    error: NotRequired[str]
    workflow_step_failed: NotRequired[str]


# =============================================================================
# Type Aliases
# =============================================================================

# Message content can be string or multimodal blocks
MessageContent = Union[str, List[Dict[str, Any]]]

# Message role types
MessageRole = Literal["user", "assistant", "system", "tool"]

# Finish reasons
FinishReason = Literal["stop", "length", "tool_calls", "content_filter"]

# Model parameter types
Temperature = float  # 0.0 to 2.0
MaxTokens = int  # Positive integer
TopP = float  # 0.0 to 1.0

# ID types for clarity
ChatID = str
MessageID = str
FileID = str
KnowledgeID = str
FolderID = str
SessionID = str
