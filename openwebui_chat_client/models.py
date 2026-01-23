"""
Data models for OpenWebUI Chat Client.
These models provide object-oriented access to API responses.
"""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Type, TypeVar

T = TypeVar("T", bound="BaseModel")


@dataclass
class BaseModel:
    """Base class for all data models."""

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from a dictionary."""
        if not data:
            return cls()

        # Get field names of the dataclass
        field_names = set(cls.__annotations__.keys())

        # Filter data to only include valid fields
        filtered_data = {k: v for k, v in data.items() if k in field_names}

        return cls(**filtered_data)


class ModelObject:
    """Generic model wrapper for arbitrary API responses."""

    def __init__(self, **data: Any) -> None:
        super().__setattr__("_data", {})
        for key, value in data.items():
            self._data[key] = to_model(value)

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_data":
            super().__setattr__(key, value)
            return
        self._data[key] = to_model(value)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = to_model(value)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def to_dict(self) -> Dict[str, Any]:
        """Recursively convert back to a plain dictionary."""

        def _convert(v: Any) -> Any:
            if isinstance(v, ModelObject):
                return v.to_dict()
            if isinstance(v, list):
                return [_convert(i) for i in v]
            if isinstance(v, tuple):
                return tuple(_convert(i) for i in v)
            if isinstance(v, dict):
                return {k: _convert(val) for k, val in v.items()}
            return v

        return {key: _convert(value) for key, value in self._data.items()}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModelObject):
            return self._data == other._data
        if isinstance(other, dict):
            return self.to_dict() == other
        return False

    def __hash__(self) -> int:
        # Make it hashable for use in sets/dict keys (uses id since _data is mutable)
        return id(self)

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"ModelObject({self._data})"


def to_model(value: Any) -> Any:
    """Recursively convert dictionaries to ModelObject for dot access."""
    if isinstance(value, BaseModel):
        return value
    if isinstance(value, ModelObject):
        return value
    if isinstance(value, Mapping):
        return ModelObject(**{k: to_model(v) for k, v in value.items()})
    if isinstance(value, list):
        return [to_model(v) for v in value]
    if isinstance(value, tuple):
        return tuple(to_model(v) for v in value)
    if isinstance(value, set):
        return {to_model(v) for v in value}
    return value


def _wrap_generator(
    gen: Generator[Any, None, None],
) -> Generator[Any, None, None]:
    for item in gen:
        yield to_model(item)


def _wrap_async_generator(
    gen: AsyncGenerator[Any, None],
) -> AsyncGenerator[Any, None]:
    async def _generator() -> AsyncGenerator[Any, None]:
        async for item in gen:
            yield to_model(item)

    return _generator()


def wrap_result(result: Any) -> Any:
    """Wrap a result so dictionaries support dot access, recursively."""
    if inspect.isasyncgen(result):
        return _wrap_async_generator(result)
    if inspect.isgenerator(result):
        return _wrap_generator(result)
    return to_model(result)


class ModelAccessMixin:
    """Mixin to wrap public method return values with model objects."""

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        # Skip private/dunder attributes
        if name.startswith("_"):
            return attr
        # Skip non-callable attributes
        if not callable(attr):
            return attr
        # Only wrap methods that belong to the instance's class hierarchy
        # Skip if this is not a method of the class (e.g., stored callable attributes)
        if not inspect.ismethod(attr) and not inspect.isfunction(attr):
            # Check if it's a bound method by looking for __self__
            if not hasattr(attr, "__self__"):
                return attr

        if inspect.iscoroutinefunction(attr):

            async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await attr(*args, **kwargs)
                return wrap_result(result)

            _async_wrapper.__name__ = getattr(attr, "__name__", name)
            _async_wrapper.__doc__ = getattr(attr, "__doc__")
            return _async_wrapper

        if inspect.isasyncgenfunction(attr):

            def _async_gen_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = attr(*args, **kwargs)
                return wrap_result(result)

            _async_gen_wrapper.__name__ = getattr(attr, "__name__", name)
            _async_gen_wrapper.__doc__ = getattr(attr, "__doc__")
            return _async_gen_wrapper

        if inspect.isgeneratorfunction(attr):

            def _gen_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = attr(*args, **kwargs)
                return wrap_result(result)

            _gen_wrapper.__name__ = getattr(attr, "__name__", name)
            _gen_wrapper.__doc__ = getattr(attr, "__doc__")
            return _gen_wrapper

        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            result = attr(*args, **kwargs)
            return wrap_result(result)

        _wrapper.__name__ = getattr(attr, "__name__", name)
        _wrapper.__doc__ = getattr(attr, "__doc__")
        return _wrapper


@dataclass
class ChatResponse(BaseModel):
    """Represents a response from a chat operation."""

    response: Optional[str] = None
    chat_id: Optional[str] = None
    message_id: Optional[str] = None
    suggested_tags: Optional[List[str]] = None
    suggested_title: Optional[str] = None
    follow_ups: Optional[List[str]] = None
    sources: Optional[List[Dict[str, Any]]] = None


@dataclass
class ParallelModelResponse(BaseModel):
    """Represents a response from a single model in parallel chat."""

    content: Optional[str] = None
    follow_ups: Optional[List[str]] = None
    sources: Optional[List[Dict[str, Any]]] = None


@dataclass
class ParallelChatResponse(BaseModel):
    """Represents a response from a parallel chat operation."""

    responses: Dict[str, Any] = field(
        default_factory=dict
    )  # values are dicts or ParallelModelResponse
    chat_id: Optional[str] = None
    message_ids: List[str] = field(default_factory=list)
    suggested_tags: Optional[List[str]] = None
    suggested_title: Optional[str] = None

    def __post_init__(self):
        """Convert response dictionaries to ParallelModelResponse objects if needed."""
        if self.responses:
            new_responses = {}
            for k, v in self.responses.items():
                if isinstance(v, dict):
                    new_responses[k] = ParallelModelResponse.from_dict(v)
                else:
                    new_responses[k] = v
            self.responses = new_responses


@dataclass
class ModelItem(BaseModel):
    """Represents a model item in chat data."""

    id: Optional[str] = None
    name: Optional[str] = None
    owned_by: Optional[str] = None
    info: Optional[Dict[str, Any]] = None


@dataclass
class Message(BaseModel):
    """Represents a chat message."""

    id: Optional[str] = None
    parentId: Optional[str] = None
    childrenIds: List[str] = field(default_factory=list)
    role: Optional[str] = None
    content: Optional[str] = None
    files: List[Dict[str, Any]] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    model: Optional[str] = None
    modelName: Optional[str] = None
    sources: List[Dict[str, Any]] = field(default_factory=list)
    originalContent: Optional[str] = None
    statusHistory: List[Dict[str, Any]] = field(default_factory=list)
    done: Optional[bool] = None
    timestamp: Optional[int] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


@dataclass
class ChatHistory(BaseModel):
    """Represents the history of a chat."""

    messages: Dict[str, Any] = field(
        default_factory=dict
    )  # values are dicts or Message
    currentId: Optional[str] = None

    def __post_init__(self):
        if self.messages:
            new_messages = {}
            for k, v in self.messages.items():
                if isinstance(v, dict):
                    new_messages[k] = Message.from_dict(v)
                else:
                    new_messages[k] = v
            self.messages = new_messages


@dataclass
class ChatData(BaseModel):
    """Represents the data of a chat."""

    id: Optional[str] = None
    title: Optional[str] = None
    models: List[str] = field(default_factory=list)
    model_item: Optional[Any] = None  # Dict or ModelItem
    history: Optional[Any] = None  # Dict or ChatHistory
    messages: List[Any] = field(default_factory=list)  # List of dicts or Message
    currentId: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if isinstance(self.model_item, dict):
            self.model_item = ModelItem.from_dict(self.model_item)
        if isinstance(self.history, dict):
            self.history = ChatHistory.from_dict(self.history)
        if self.messages:
            self.messages = [
                Message.from_dict(m) if isinstance(m, dict) else m
                for m in self.messages
            ]


@dataclass
class ChatDetails(BaseModel):
    """Represents the full details of a chat."""

    chat: Optional[Any] = None  # Dict or ChatData
    id: Optional[str] = None
    folder_id: Optional[str] = None
    user_id: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None
    archived: Optional[bool] = None
    pinned: Optional[bool] = None

    def __post_init__(self):
        if isinstance(self.chat, dict):
            self.chat = ChatData.from_dict(self.chat)


@dataclass
class Function(BaseModel):
    """Represents a function/tool."""

    id: Optional[str] = None
    name: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    type: Optional[str] = None
    # Add other fields as necessary, using Any for flexibility
    params: Optional[Dict[str, Any]] = None


@dataclass
class ActionResult(BaseModel):
    """Represents the result of an action."""

    messages: List[Any] = field(default_factory=list)  # List of dicts or Message
    message: Optional[Any] = None  # Dict or Message
    data: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    html: Optional[str] = None
    status: Optional[bool] = None
    success: Optional[bool] = None  # Added for compatibility
    id: Optional[str] = None

    def __post_init__(self):
        if self.messages:
            self.messages = [
                Message.from_dict(m) if isinstance(m, dict) else m
                for m in self.messages
            ]
        if isinstance(self.message, dict):
            self.message = Message.from_dict(self.message)
