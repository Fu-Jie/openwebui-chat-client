"""
Example of using the stream_process_task feature in OpenWebUIClient.

This example demonstrates how to use the streaming version of the autonomous task
processing agent. The agent will stream real-time updates as it works through the
multi-step problem-solving process, providing visibility into each iteration.

Requirements:
- A tool server configured in OpenWebUI (e.g., web search, calculator, etc.)
- Set OUI_TOOL_SERVER_ID environment variable with your tool server ID
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
        
        print("\n" + "="*80)
        print("Streaming Task Processing - Real-time Updates")
        print("="*80)
        print(f"Task: {task_question}\n")
        
        # 2. Call the stream_process_task method
        result = None
        current_iteration = 0
        
        for chunk in client.stream_process_task(
            question=task_question,
            model_id=selected_model,
            tool_server_ids=tool_id,
            max_iterations=max_iterations
        ):
            # Handle different chunk types
            chunk_type = chunk.get("type")
            
            if chunk_type == "iteration_start":
                current_iteration = chunk.get("iteration", 0)
                total = chunk.get("total_iterations", max_iterations)
                print(f"\n--- Iteration {current_iteration}/{total} ---")
                
            elif chunk_type == "content":
                # Stream content as it arrives
                content = chunk.get("content", "")
                print(content, end="", flush=True)
                
            elif chunk_type == "iteration_complete":
                iteration_num = chunk.get("iteration", 0)
                is_final = chunk.get("is_final", False)
                if is_final:
                    print("\n\n✅ Final answer reached!")
                else:
                    print(f"\n[Iteration {iteration_num} complete]")
                    
            elif chunk_type == "complete":
                result = chunk.get("result")
                print("\n\n" + "="*80)
                print("Task Processing Complete!")
                print("="*80)
                
            elif chunk_type == "error":
                error_msg = chunk.get("message", "Unknown error")
                print(f"\n❌ Error: {error_msg}")

        # Display final result
        if result:
            print(f"\n--- Final Solution ---")
            solution = result.get('solution', 'No solution found.')
            print(solution)
            
            print(f"\n--- Statistics ---")
            print(f"Total Iterations: {result.get('total_iterations', 0)}")
            print(f"Conversation Turns: {len(result.get('conversation_history', []))}")
            
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
