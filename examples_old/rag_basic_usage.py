import logging
import os
import time
from openwebui_chat_client import OpenWebUIClient
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration from Environment Variables ---
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

# *** Models for Testing ***
# Ensure these models are available in your Open WebUI instance.
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Parse parallel models from environment variable (comma-separated)
_parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
PARALLEL_MODELS = [model.strip() for model in _parallel_models_str.split(",") if model.strip()]

MULTIMODAL_MODEL = os.getenv("OUI_MULTIMODAL_MODEL", DEFAULT_MODEL)
RAG_MODEL = os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash")  # A good model for RAG tasks

# --- Configure Logging for the Application ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper function to create test files ---
def create_test_file(filename: str, content: str):
    """Creates a local text file for testing RAG and KB features."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"✅ Created test file: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to create test file {filename}: {e}")
        return None

def cleanup_files(filenames: list):
    """Removes test files created during the demo."""
    for filename in filenames:
        if filename and os.path.exists(filename):
            os.remove(filename)
            logging.info(f"🧹 Cleaned up test file: {filename}")

# --- Demo Scenarios ---

def demo_knowledge_base(client: OpenWebUIClient):
    print("\n" + "#"*20 + " SCENE 1: Knowledge Base Management " + "#"*20)
    kb_name = "Project Apollo Documents"
    file_content = "Project Apollo's primary objective was to land humans on the Moon and bring them back safely to Earth. The Apollo 11 mission was the first to achieve this in 1969."
    test_file = create_test_file("apollo_brief.txt", file_content)
    
    if not test_file:
        return

    success = client.add_file_to_knowledge_base(
        file_path=test_file,
        knowledge_base_name=kb_name
    )

    if success:
        logging.info(f"Successfully added '{test_file}' to the '{kb_name}' knowledge base.")
        # Note: Chatting with the collection would be the next step.
        # This can be implemented by passing `rag_collections=[kb_name]` to the chat method.
    else:
        logging.error("Failed to complete the knowledge base operation.")
    
    cleanup_files([test_file])

def demo_rag_chat(client: OpenWebUIClient):
    print("\n" + "#"*20 + " SCENE 2: RAG Chat with a File " + "#"*20)
    file_content = "The Ouroboros protocol is a family of proof-of-stake blockchain protocols that provide verifiable security guarantees."
    test_file = create_test_file("blockchain_protocol.txt", file_content)

    if not test_file:
        return
        
    result = client.chat(
        question="Based on the document, what is the Ouroboros protocol?",
        chat_title="Blockchain RAG Test",
        rag_files=[test_file],
        model_id=RAG_MODEL
    )
    if result and result.get("response"):
        print(f"\n🤖 [RAG Response]:\n{result['response']}\n")

    cleanup_files([test_file])


def demo_parallel_chat(client: OpenWebUIClient):
    print("\n" + "#"*20 + " SCENE 3: Multi-Model Parallel Chat " + "#"*20)
    result = client.parallel_chat(
        question="What is the most exciting thing about space exploration in one sentence?",
        chat_title="Space Exploration Insights",
        model_ids=PARALLEL_MODELS,
        folder_name="Science",
        tags=["space", "exploration", "multi-model"]
    )
    if result and result.get("responses"):
        for model, content in result["responses"].items():
            print(f"\n🤖 [{model}'s Response]:\n{content}\n")

def main():
    """Runs all demo scenarios."""
    if not AUTH_TOKEN:
        logging.error("🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key.")
        return
        
    # Initialize the client with a default model
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # Run the demos sequentially
    demo_knowledge_base(client)
    time.sleep(2) # Pause between demos for clarity
    demo_rag_chat(client)
    time.sleep(2)
    demo_parallel_chat(client)

    print("\n🎉 All demo scenarios completed. Please check your Open WebUI interface to see the results.")

if __name__ == "__main__":
    main()
