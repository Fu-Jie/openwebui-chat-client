"""
Data models for OpenWebUI Chat Client.
Built on Pydantic V2 to strictly align with OpenWebUI Backend.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class BaseWebUIModel(BaseModel):
    """
    Base model for all OpenWebUI responses.
    Configured to allow extra fields natively, replacing the old ModelObject.
    """

    model_config = ConfigDict(
        extra="allow", populate_by_name=True, protected_namespaces=()
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if not data:
            return None
        # Support legacy 'response' field for backward compatibility
        if "response" in data and "content" not in data:
            data = data.copy()
            data["content"] = data.pop("response")
        return cls.model_validate(data)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def setdefault(self, key, default=None):
        if not hasattr(self, key):
            setattr(self, key, default)
        return getattr(self, key)


class ChatMessage(BaseWebUIModel):
    id: Optional[str] = None
    parentId: Optional[str] = None
    childrenIds: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    content: Optional[str] = None
    files: List[Dict[str, Any]] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    modelName: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    originalContent: Optional[str] = None
    statusHistory: List[Dict[str, Any]] = Field(default_factory=list)
    done: Optional[bool] = None
    timestamp: Optional[int] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatHistory(BaseWebUIModel):
    messages: Dict[str, ChatMessage] = Field(default_factory=dict)
    currentId: Optional[str] = None


class ChatData(BaseWebUIModel):
    id: Optional[str] = None
    title: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    system: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    messages: List[ChatMessage] = Field(default_factory=list)
    history: Optional[ChatHistory] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class ChatDetails(BaseWebUIModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: Optional[str] = None
    chat: Optional[ChatData] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    archived: Optional[bool] = None
    pinned: Optional[bool] = None


class ChatCompletionMessage(BaseWebUIModel):
    role: str
    content: Optional[str] = None


class ChatCompletionChoice(BaseWebUIModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = None


class ChatCompletionResult(BaseWebUIModel):
    """
    Represents the output of the /api/chat/completions endpoint (OpenAI standard shape)
    """

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Dict[str, Any]] = None


class ModelMeta(BaseWebUIModel):
    profile_image_url: Optional[str] = None
    description: Optional[str] = None
    suggestion_prompts: Optional[List[Dict[str, str]]] = None
    tags: Optional[List[Dict[str, str]]] = None
    capabilities: Optional[Dict[str, Any]] = None


class ModelResponse(BaseWebUIModel):
    id: str
    name: str
    meta: Optional[ModelMeta] = None
    base_model_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    access_control: Optional[Dict[str, Any]] = None
    is_active: bool = True
    user_id: Optional[str] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None


class UserResponse(BaseWebUIModel):
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    profile_image_url: Optional[str] = None
    last_active_at: Optional[int] = None
    created_at: Optional[int] = None


class FolderResponse(BaseWebUIModel):
    id: str
    name: str
    user_id: str
    parent_id: Optional[str] = None
    is_expanded: bool = False
    updated_at: Optional[int] = None
    created_at: Optional[int] = None


class FileResponse(BaseWebUIModel):
    id: str
    user_id: Optional[str] = None
    filename: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    created_at: Optional[int] = None


class PromptResponse(BaseWebUIModel):
    command: str
    title: str
    content: str
    user_id: Optional[str] = None
    timestamp: Optional[int] = None
    access_control: Optional[Dict[str, Any]] = None


class NoteResponse(BaseWebUIModel):
    id: str
    user_id: Optional[str] = None
    title: str
    content: str
    data: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    access_control: Optional[Dict[str, Any]] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None


class KnowledgeResponse(BaseWebUIModel):
    id: str
    user_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None


class ChatResponse(BaseWebUIModel):
    """
    Standard response returned by chat operations.
    """

    content: str
    chat_id: str
    message_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

    @property
    def text(self) -> str:
        """
        Alias for content to provide a more intuitive API.
        """
        return self.content or ""


class ActionResult(BaseWebUIModel):
    status: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ParallelChatResponse(BaseWebUIModel):
    responses: Dict[str, ChatResponse]
    chat_id: str
    message_ids: Dict[str, str]
    suggested_tags: Optional[List[str]] = None
    suggested_title: Optional[str] = None


class Function(BaseWebUIModel):
    """
    Function/Action/Tool representation.
    In Open WebUI, functions can be of type 'action', 'filter', or 'pipe'.
    """

    id: str
    name: Optional[str] = None
    type: Optional[str] = "action"  # 'action', 'filter', or 'pipe'
    meta: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    @property
    def is_action(self) -> bool:
        """Check if this function is an action."""
        return self.type == "action"

    @property
    def is_filter(self) -> bool:
        """Check if this function is a filter."""
        return self.type == "filter"

    @property
    def is_pipe(self) -> bool:
        """Check if this function is a pipe."""
        return self.type == "pipe"
