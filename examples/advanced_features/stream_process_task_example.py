"""
Example of using the stream_process_task feature in OpenWebUIClient.

This example demonstrates how to use the streaming version of the autonomous task
processing agent. The agent will stream real-time updates as it works through the
multi-step problem-solving process, providing visibility into each iteration.

Features demonstrated:
- Streaming multi-step iterative problem-solving
- Key Findings accumulation across iterations
- Optional decision model for automatic option selection
- Real-time visibility into the agent's thought process
- History summarization

Requirements:
- A tool server configured in OpenWebUI (e.g., web search, calculator, etc.)
- Set OUI_TOOL_SERVER_ID environment variable with your tool server ID
- (Optional) Set OUI_DECISION_MODEL environment variable for automatic decision-making
"""
import os
import sys
import logging
from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "llama3")
TOOL_SERVER_ID = os.getenv("OUI_TOOL_SERVER_ID", "")
# Optional: Decision model for automatic option selection
DECISION_MODEL = os.getenv("OUI_DECISION_MODEL", "")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# --- Initialization ---
if not TOKEN:
    logger.error("❌ OUI_AUTH_TOKEN environment variable not set.")
    sys.exit(1)

if not TOOL_SERVER_ID:
    logger.warning("⚠️ OUI_TOOL_SERVER_ID not set. The example may not work without a tool server.")

try:
    client = OpenWebUIClient(
        base_url=BASE_URL,
        token=TOKEN,
        default_model_id=DEFAULT_MODEL
    )
    logger.info("✅ Client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize client: {e}")
    sys.exit(1)


# --- Streaming Task Processing Execution ---
if __name__ == "__main__":
    logger.info("Starting stream_process_task example...")

    # 1. Find available models
    logger.info("Discovering available models...")
    all_models = client.list_models()
    if not all_models:
        logger.error("❌ No models found. Cannot proceed with the example.")
        sys.exit(1)

    # Use the first available model or the default one
    available_model_ids = [m['id'] for m in all_models]
    selected_model = DEFAULT_MODEL if DEFAULT_MODEL in available_model_ids else available_model_ids[0]
    
    logger.info(f"✅ Using model: {selected_model}")

    # Define the task to process
    task_question = "Calculate the factorial of 5 and then multiply it by 3"
    max_iterations = 10

    # If no tool server ID is provided, use a mock/empty string for demonstration
    tool_id = TOOL_SERVER_ID if TOOL_SERVER_ID else "mock-tool-server"

    try:
        logger.info(f"🚀 Streaming task processing: {task_question}")
        logger.info(f"   Model: {selected_model}")
        logger.info(f"   Tool Server: {tool_id}")
        logger.info(f"   Max Iterations: {max_iterations}")
        
        # Check if decision model is configured
        decision_model_id = None
        if DECISION_MODEL:
            # Verify decision model is available
            if DECISION_MODEL in available_model_ids:
                decision_model_id = DECISION_MODEL
                logger.info(f"   Decision Model: {decision_model_id}")
            else:
                logger.warning(f"⚠️ Decision model '{DECISION_MODEL}' not found. Proceeding without automatic option selection.")
        
        print("\n" + "="*80)
        print("Streaming Task Processing - Real-time Updates")
        print("="*80)
        print(f"Task: {task_question}")
        if decision_model_id:
            print(f"Decision Model: {decision_model_id} (auto-selects when options arise)")
        print()
        
        # 2. Call the stream_process_task method with history summarization
        final_result = None
        
        # This generator yields real-time events and returns the final result
        stream_generator = client.stream_process_task(
            question=task_question,
            model_id=selected_model,
            tool_server_ids=tool_id,
            max_iterations=max_iterations,
            summarize_history=True,  # Enable history summarization
            decision_model_id=decision_model_id  # Optional: Use decision model for automatic option selection
        )

        try:
            while True:
                chunk = next(stream_generator)
                
                # Handle different event types from the stream
                chunk_type = chunk.get("type")
                content = chunk.get("content")

                if chunk_type == "iteration_start":
                    print(f"\n--- Iteration {chunk.get('iteration')} ---")
                elif chunk_type == "thought":
                    print(f"🤔 Thought: {content}")
                elif chunk_type == "todo_list_update":
                    print("\n📋 To-Do List Updated:")
                    for item in content:
                        status_icon = "✅" if item['status'] == 'completed' else "⏳" if item['status'] == 'in_progress' else "📋"
                        print(f"   {status_icon} {item['task']}")
                elif chunk_type == "tool_call":
                    print(f"   🛠️  Calling Tool: {content.get('tool')} with args: {content.get('args')}")
                elif chunk_type == "observation":
                    print(f"   👀 Observation: {content}")
                elif chunk_type == "decision":
                    # New: Handle decision model selection events
                    print(f"   🎯 Decision Model selected option {chunk.get('selected_option')}")
                elif chunk_type == "final_answer":
                    print(f"\n✅ Final Answer: {content}")
                elif chunk_type == "error":
                    print(f"\n❌ Error: {content}")

        except StopIteration as e:
            # The generator is exhausted, and the return value is in e.value
            final_result = e.value
            print("\n\n" + "="*80)
            print("Task Processing Complete!")
            print("="*80)

        # Display final result
        if final_result:
            print(f"\n--- Final Solution ---")
            solution = final_result.get('solution', 'No solution found.')
            print(solution)
            
            print(f"\n--- Summarized History ---")
            summary = final_result.get('conversation_history', 'No summary available.')
            print(summary)
            
            print("\n" + "="*80)
            print(f"👉 You can view the full task processing conversation in OpenWebUI")
            print(f"   under the chat titled 'Task Processing: {task_question[:50]}'")
            print("="*80)
        else:
            print("\n❌ Task processing did not return a result. Check the logs.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
