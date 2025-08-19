"""
Example of using the deep_research feature in OpenWebUIClient.

This example demonstrates how to use the autonomous research agent to generate
a report on a given topic. The agent will perform a multi-step research process,
and the entire workflow will be visible as a conversation in the OpenWebUI interface.
"""
import os
from openwebui_chat_client import OpenWebUIClient

# --- Configuration ---
# Make sure to set the environment variables OPENWEBUI_BASE_URL and OPENWEBUI_TOKEN
# or replace the os.getenv calls with your actual base_url and token.
BASE_URL = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:8080")
TOKEN = os.getenv("OPENWEBUI_TOKEN", "your_token_here")

# --- Initialization ---
try:
    client = OpenWebUIClient(
        base_url=BASE_URL,
        token=TOKEN,
        default_model_id="llama3"  # Provide a default model for initialization
    )
except Exception as e:
    print(f"Error initializing client: {e}")
    exit(1)

# --- Deep Research Execution ---
if __name__ == "__main__":
    print("Starting deep research example...")

    # Define the research topic and number of steps
    research_topic = "The impact of generative AI on the software development industry"
    research_steps = 3  # The agent will perform 3 plan-and-execute cycles

    try:
        # Call the deep_research method with lists of models for routing.
        # The agent will decide whether to use a 'general' or 'search' model for each step.
        result = client.deep_research(
            topic=research_topic,
            num_steps=research_steps,
            general_models=["llama3", "gemma:7b"],
            search_models=["duckduckgo-search"]  # Assumes a model with search capabilities is configured
        )

        if result:
            print("\n" + "="*80)
            print("✅ Deep Research with Intelligent Routing Completed Successfully!")
            print("="*80)
            print(f"Topic: {result.get('topic')}")
            print(f"Chat ID: {result.get('chat_id')}")
            print(f"Chat Title: {result.get('chat_title')}")
            print("\n--- Research Log ---")
            for i, log_entry in enumerate(result.get('research_log', []), 1):
                print(f"{i}. {log_entry}")

            print("\n--- Final Report ---")
            print(result.get('final_report', 'No report was generated.'))
            print("\n" + "="*80)
            print(f"👉 You can now view the full research process in the OpenWebUI interface under the chat titled '{result.get('chat_title')}'.")

        else:
            print("\n❌ Deep Research failed. Check the logs for more details.")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
