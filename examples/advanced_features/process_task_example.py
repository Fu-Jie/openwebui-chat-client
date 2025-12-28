"""
Example of using the process_task feature in OpenWebUIClient.

This example demonstrates how to use the autonomous task processing agent to solve
complex problems in a multi-step agentic loop. The agent will repeatedly plan and
execute steps until it reaches a final answer, and the entire workflow will be
visible as a conversation in the OpenWebUI interface.

Features demonstrated:
- Multi-step iterative problem-solving with tool integration
- Key Findings accumulation across iterations
- Optional decision model for automatic option selection
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


# --- Task Processing Execution ---
if __name__ == "__main__":
    logger.info("Starting process_task example...")

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
    task_question = "What is the square root of 144 plus the cube root of 27?"
    max_iterations = 10

    # If no tool server ID is provided, use a mock/empty string for demonstration
    # In a real scenario, you would need a valid tool server ID
    tool_id = TOOL_SERVER_ID if TOOL_SERVER_ID else "mock-tool-server"

    try:
        logger.info(f"🚀 Processing task: {task_question}")
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
        
        # 2. Call the process_task method with history summarization enabled
        result = client.process_task(
            question=task_question,
            model_id=selected_model,
            tool_server_ids=tool_id,
            max_iterations=max_iterations,
            summarize_history=True,  # Enable history summarization
            decision_model_id=decision_model_id  # Optional: Use decision model for automatic option selection
        )

        if result:
            print("\n" + "="*80)
            print("✅ Task Processing Completed Successfully!")
            print("="*80)
            print(f"Task: {task_question}")
            
            # Display the final to-do list
            print("\n--- Final To-Do List ---")
            todo_list = result.get('todo_list', [])
            if todo_list:
                for item in todo_list:
                    status_icon = "✅" if item['status'] == 'completed' else "⏳" if item['status'] == 'in_progress' else "📋"
                    print(f"{status_icon} {item['task']}")
            else:
                print("No to-do list available.")

            # Display the solution
            print("\n--- Solution ---")
            solution = result.get('solution', 'No solution found.')
            print(solution)
            
            # Display summarized conversation history
            print("\n--- Summarized Conversation History ---")
            summary = result.get('conversation_history', 'No summary available.')
            print(summary)
            
            print("\n" + "="*80)
            print(f"👉 You can view the full task processing conversation in OpenWebUI")
            print(f"   under the chat titled 'Task Processing: {task_question[:50]}'")
            print("="*80)

        else:
            print("\n❌ Task processing failed. Check the logs for more details.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
