import pytest
from unittest.mock import MagicMock, patch, call

from openwebui_chat_client import OpenWebUIClient

BASE_URL = "http://localhost:8080"
TOKEN = "test_token"
DEFAULT_MODEL = "test_model"

@pytest.fixture
def client():
    """Fixture for OpenWebUIClient."""
    with patch('requests.Session', MagicMock()):
        client = OpenWebUIClient(base_url=BASE_URL, token=TOKEN, default_model_id=DEFAULT_MODEL, skip_model_refresh=True)
        # Mock the internal client/manager methods that make network calls
        client._base_client._parent_client = client
        client._chat_manager.base_client._parent_client = client
        client._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
        client._chat_manager._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
        client.chat_id = "test_chat_id"
        yield client

def test_process_task_success(client):
    """Test the process_task function for a successful multi-step task."""
    # Mock the chat method to simulate a two-step process
    client._chat_manager.chat = MagicMock(side_effect=[
        {"response": "First step is to use the tool."},
        {"response": "Final Answer: The task is complete."},
    ])

    result = client.process_task(
        question="Solve this complex problem.",
        model_id="test_model",
        tool_server_ids="test_tool"
    )

    assert client._chat_manager.chat.call_count == 2
    assert "solution" in result
    assert result["solution"] == "Final Answer: The task is complete."
    assert len(result["conversation_history"]) == 2

def test_process_task_max_iterations(client):
    """Test that process_task stops after max_iterations."""
    # Mock the chat method to always return an intermediate step
    client._chat_manager.chat = MagicMock(return_value={"response": "Still working..."})

    result = client.process_task(
        question="Solve this complex problem.",
        model_id="test_model",
        tool_server_ids="test_tool",
        max_iterations=3
    )

    assert client._chat_manager.chat.call_count == 3
    assert result["solution"] == "Max iterations reached."

def test_stream_process_task_success(client):
    """Test the stream_process_task function for a successful multi-step task."""
    # Mock the stream_chat method
    # This needs to be a function that returns a new generator each time
    def get_stream_chat_side_effect():
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                def gen1():
                    yield "Thinking... "
                    yield "tool call needed."
                return gen1()
            else:
                def gen2():
                    yield "Final Answer: "
                    yield "Streamed task complete."
                return gen2()
        return MagicMock(side_effect=side_effect)

    client._chat_manager.stream_chat = get_stream_chat_side_effect()

    full_response = []
    for chunk in client.stream_process_task(
        question="Solve this complex problem.",
        model_id="test_model",
        tool_server_ids="test_tool"
    ):
        full_response.append(chunk)

    assert client._chat_manager.stream_chat.call_count == 2

    iteration_starts = [r for r in full_response if r.get("type") == "iteration_start"]
    assert len(iteration_starts) == 2

    content_chunks = [r.get("content", "") for r in full_response if r.get("type") == "content"]
    final_content = "".join(content_chunks)
    assert "Final Answer: Streamed task complete." in final_content

    completion_events = [r for r in full_response if r.get("type") == "complete"]
    assert len(completion_events) == 1
    assert "solution" in completion_events[0]["result"]
