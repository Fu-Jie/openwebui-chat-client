"""
Configuration and demo script for OpenWebUI Chat Client.
This module provides configuration settings and various demo functions
to showcase different features of the OpenWebUI Chat Client.
"""

import logging
import os
import sys
import time
from typing import List, Optional

# Add the project root to the Python path to ensure the local version is imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openwebui_chat_client import OpenWebUIClient
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# ===============================
# Configuration
# ===============================


class Config:
    """Configuration settings for the OpenWebUI Chat Client."""

    # Server Configuration
    BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

    # Model Configuration
    DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
    
    # Parse parallel models from environment variable (comma-separated)
    _parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
    PARALLEL_MODELS = [model.strip() for model in _parallel_models_str.split(",") if model.strip()]
    
    MULTIMODAL_MODEL = os.getenv("OUI_MULTIMODAL_MODEL", DEFAULT_MODEL)
    RAG_MODEL = os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash")


# ===============================
# Logging Configuration
# ===============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ===============================
# Helper Functions
# ===============================


class FileHelper:
    """Helper class for file operations."""

    @staticmethod
    def create_test_file(filename: str, content: str) -> Optional[str]:
        """Creates a local text file for testing RAG and KB features."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"✅ Created test file: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Failed to create test file {filename}: {e}")
            return None

    @staticmethod
    def create_test_image(text: str, filename: str) -> Optional[str]:
        """Helper function to create test images with text."""
        try:
            img = Image.new("RGB", (500, 100), color=(20, 40, 80))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except IOError:
                font = ImageFont.load_default()
            d.text((10, 10), text, fill=(255, 255, 200), font=font)
            img.save(filename)
            logging.info(f"✅ Created test image: {filename}")
            return filename
        except ImportError:
            logging.warning("Pillow library not installed. Cannot create test image.")
            return None

    @staticmethod
    def cleanup_files(filenames: List[str]) -> None:
        """Removes test files created during the demo."""
        for filename in filenames:
            if filename and os.path.exists(filename):
                os.remove(filename)
                logging.info(f"🧹 Cleaned up test file: {filename}")


# ===============================
# Demo Classes
# ===============================


class ChatDemos:
    """Demo functions for basic chat functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def basic_chat_demo(self) -> None:
        """Demonstrates basic chat functionality."""
        print("\n" + "#" * 20 + " Basic Chat Demo " + "#" * 20)

        result = self.client.chat(
            question="What is the capital of France?",
            chat_title="Basic Chat Test",
            folder_name="General",
        )

        if result and result.get("response"):
            print(f"\n🤖 Response:\n{result['response']}\n")

    def stream_chat_demo(self) -> None:
        """Demonstrates streaming chat functionality."""
        print("\n" + "#" * 20 + " Streaming Chat Demo " + "#" * 20)

        print("Streaming Chat Response:")
        for chunk in self.client.stream_chat(
            question="Who is the champion of the 2025 FIFA Club World Cup?",
            chat_title="Streaming Chat Demo",
        ):
            print(chunk, end="", flush=True)
        print("\n")

    def stream_chat_with_follow_up_demo(self) -> None:
        """Demonstrates streaming chat with follow-up suggestions."""
        print("\n" + "#" * 20 + " Streaming Chat with Follow-up Demo " + "#" * 20)

        print("Streaming Chat Response:")
        stream_gen = self.client.stream_chat(
            question="Tell me about the history of artificial intelligence",
            chat_title="Streaming Follow-up Demo",
            enable_follow_up=True,
        )
        
        # Process streaming chunks
        for chunk in stream_gen:
            print(chunk, end="", flush=True)
        
        # Get the return values (content, sources, follow_ups)
        try:
            final_content, sources, follow_ups = stream_gen.value
            print("\n")
            
            if follow_ups:
                print("Follow-up suggestions:")
                for suggestion in follow_ups:
                    print(f"  - {suggestion}")
                print()
        except AttributeError:
            # If stream_gen.value is not available, that's ok
            print("\n")

    def stream_image_chat_demo(self) -> None:
        """Demonstrates streaming chat with image input functionality."""
        print("\n" + "#" * 20 + " Streaming Image Chat Demo " + "#" * 20)

        # Create a test image
        test_image = FileHelper.create_test_image(
            "Test image for streaming chat", "streaming_image_test.png"
        )

        if not test_image:
            return

        try:
            print("Streaming response with image input:")
            for chunk in self.client.stream_chat(
                question="Describe this image in "
                "detail",
                chat_title="Streaming Image Chat Demo",
                image_paths=[test_image],
            ):
                print(chunk, end="", flush=True)
            print("\n")
        finally:
            FileHelper.cleanup_files([test_image])


    def chat_with_follow_up_demo(self) -> None:
        """Demonstrates chat with follow-up suggestions."""
        print("\n" + "#" * 20 + " Chat with Follow-up Demo " + "#" * 20)

        result = self.client.chat(
            question="Hi",
            chat_title="Simple Follow-up Demo", 
            enable_follow_up=True,
        )
        if result and result.get("response"):
            print(f"Response: {result['response']}")
            if result.get("follow_ups"):
                print(f"Follow-ups: {result['follow_ups']}")

    def parallel_chat_with_follow_up_demo(self) -> None:
        """Demonstrates parallel chat with follow-up suggestions."""
        print("\n" + "#" * 20 + " Parallel Chat with Follow-up Demo " + "#" * 20)

        result = self.client.parallel_chat(
            question="Tell me about the history of artificial intelligence.",
            chat_title="Parallel Follow-up Demo",
            model_ids=Config.PARALLEL_MODELS,
            enable_follow_up=True,
        )

        if result and result.get("responses"):
            print(f"\n🤖 Responses from multiple models:")
            for model_id, data in result["responses"].items():
                print(f"\n--- Model: {model_id} ---")
                print(data["content"])
                if data.get("follow_ups"):
                    print("\n  🤔 Follow-up suggestions:")
                    for suggestion in data["follow_ups"]:
                        print(f"    - {suggestion}")
                print()
        else:
            print("\n❌ No responses received for parallel chat.")


class StreamChatDemos:
    """Demo functions for advanced streaming chat functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def stream_chat_realtime_update_demo(self) -> None:
        """
        Demonstrates real-time incremental updates with stream_chat.

        This demo showcases how the optimized stream_chat method pushes incremental content
        to the Open WebUI frontend in real-time, achieving a typewriter effect.
        """
        print("\n" + "#" * 20 + " Real-time Streaming Chat Update Demo " + "#" * 20)
        print("=" * 50)

        # Get configuration from Config class
        model_id = Config.DEFAULT_MODEL

        # Test questions
        test_questions = [
            "Please write a short poem about spring, around 500 words.",
            "Explain what artificial intelligence is in simple terms, around 500 words.",
            "Tell me an interesting science fact.",
        ]

        chat_title = f"Streaming Chat Demo - {int(time.time())}"

        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Question {i}: {question}")
            print("-" * 40)
            print("💭 AI Response (Real-time Streaming Output):")

            try:
                # Use streaming chat and display content in real-time
                stream_generator = self.client.stream_chat(
                    question=question,
                    chat_title=chat_title,
                    model_id=model_id,
                    enable_follow_up=True,  # Enable follow-up suggestions
                    cleanup_placeholder_messages=True,  # Clean up unused placeholder messages before each request
                    placeholder_pool_size=30,  # Maintain a pool of 30 placeholder message pairs
                    min_available_messages=10,  # Ensure at least 10 available placeholder message pairs
                    wait_before_request=5.0,  # Wait 5 seconds before the first streaming request for frontend loading
                )

                full_response = ""
                chunk_count = 0
                final_content = None
                sources = []
                follow_ups = None

                # Correctly handle the generator: using a while loop and StopIteration exception
                try:
                    while True:
                        chunk = next(stream_generator)
                        full_response += chunk
                        chunk_count += 1
                        print(chunk, end="", flush=True)  # Display in real-time, no newline
                except StopIteration as e:
                    # When the generator finishes, get the return value from the exception
                    final_content, sources, follow_ups = e.value

                print(f"\n\n✅ Streaming output complete!")
                print(f"📊 Statistics:")
                print(f"   - Received {chunk_count} content chunks")
                print(f"   - Total characters: {len(full_response)}")

                if sources:
                    print(f"   - Sources: {len(sources)} ")

                if follow_ups:
                    print(f"   - Follow-up suggestions: {len(follow_ups)} ")
                    for j, follow_up in enumerate(follow_ups, 1):
                        print(f"     {j}. {follow_up}")

                # Pause briefly between questions
                if i < len(test_questions):
                    print(f"\n⏳ Waiting 2 seconds before the next question...")
                    time.sleep(2)

            except Exception as e:
                print(f"\n❌ Streaming chat error: {e}")

        print(f"\n🎉 Demo completed!")
        print(f"💡 Tip: You can view the chat history '{chat_title}' in the Open WebUI frontend.")
        print("    All streaming content should have been updated in real-time to the corresponding messages.")


class RAGDemos:
    """Demo functions for RAG (Retrieval Augmented Generation) functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def rag_chat_demo(self) -> None:
        """Demonstrates RAG chat with a file."""
        print("\n" + "#" * 20 + " RAG Chat Demo " + "#" * 20)

        file_content = (
            "The Ouroboros protocol is a family of proof-of-stake "
            "blockchain protocols that provide verifiable security guarantees."
        )
        test_file = FileHelper.create_test_file("blockchain_protocol.txt", file_content)

        if not test_file:
            return

        try:
            result = self.client.chat(
                question="Based on the document, what is the Ouroboros protocol?",
                chat_title="Blockchain RAG Test",
                rag_files=[test_file],
                model_id=Config.RAG_MODEL,
            )

            if result and result.get("response"):
                print(f"\n🤖 [RAG Response]:\n{result['response']}\n")
        finally:
            FileHelper.cleanup_files([test_file])

    def stream_rag_chat_demo(self) -> None:
        """Demonstrates streaming RAG chat with a file."""
        print("\n" + "#" * 20 + " Streaming RAG Chat Demo " + "#" * 20)

        file_content = "The 2025 FIFA Club World Cup champion is Chelsea."
        test_file = FileHelper.create_test_file("world_cup_2025.txt", file_content)

        if not test_file:
            return

        try:
            print("Streaming RAG Response:")
            for chunk in self.client.stream_chat(
                question="Based on the document, who is the champion of the 2025 FIFA Club World Cup?",
                chat_title="World Cup 2025 Streaming RAG Test",
                rag_files=[test_file],
                model_id=Config.RAG_MODEL,
            ):
                print(chunk, end="", flush=True)
            print("\n")
        finally:
            FileHelper.cleanup_files([test_file])


class KnowledgeBaseDemos:
    """Demo functions for knowledge base functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def knowledge_base_chat_demo(self) -> None:
        """Demonstrates creating a knowledge base and chatting with it."""
        print("\n" + "#" * 20 + " Knowledge Base Chat Demo " + "#" * 20)

        # Use a unique name for the KB to avoid conflicts during testing
        kb_name = f"ProjectApolloDocs-{int(time.time())}"
        file_content = (
            "Project Apollo's primary objective was to land humans on the Moon "
            "and bring them back safely to Earth. The program, which ran from "
            "1961 to 1972, was one of the most ambitious scientific undertakings "
            "in history. The Apollo 11 mission, in 1969, was the first to achieve this."
        )
        test_file = FileHelper.create_test_file(
            "apollo_mission_brief.txt", file_content
        )

        if not test_file:
            return

        try:
            # Step 1: Create Knowledge Base and Add File
            print("\n" + "#" * 20 + " Populating Knowledge Base " + "#" * 20)
            success = self.client.add_file_to_knowledge_base(
                file_path=test_file, knowledge_base_name=kb_name
            )

            if not success:
                logging.error("Failed to set up the knowledge base. Aborting demo.")
                return

            logging.info("Knowledge base is ready. Waiting a moment for processing...")
            time.sleep(5)  # Give the backend a moment to process the file

            # Step 2: Chat with the Knowledge Base
            print("\n" + "#" * 20 + " Chatting with Knowledge Base " + "#" * 20)

            result = self.client.chat(
                question="According to the documents, what was the primary objective of Project Apollo?",
                chat_title=f"Inquiry about {kb_name}",
                rag_collections=[kb_name],
            )

            if result and result.get("response"):
                print(f"\n🤖 [RAG Response from Knowledge Base]:\n{result['response']}\n")

        finally:
            FileHelper.cleanup_files([test_file])

        print("\n🎉 Knowledge base chat demo completed.")

    def batch_create_knowledge_bases_demo(self) -> None:
        """Demonstrates batch creation of knowledge bases with associated files."""
        print("\n" + "#" * 20 + " Batch Create Knowledge Bases Demo " + "#" * 20)

        # Create dummy files for testing
        file1_path = FileHelper.create_test_file(
            "batch_kb_file1.txt", "Content for batch KB file 1."
        )
        file2_path = FileHelper.create_test_file(
            "batch_kb_file2.txt", "Content for batch KB file 2."
        )

        if not file1_path or not file2_path:
            logging.error("Failed to create dummy files for batch KB demo. Aborting.")
            return

        try:
            # Define knowledge bases to create and their associated files
            knowledge_bases_to_create = {
                f"BatchKB-ProjectX-{int(time.time())}": [file1_path],
                f"BatchKB-ProjectY-{int(time.time())}": [file2_path],
                f"BatchKB-Combined-{int(time.time())}": [file1_path, file2_path],
            }

            print("\n--- Starting Batch Creation ---")
            results = self.client.create_knowledge_bases_with_files(
                knowledge_bases_to_create
            )

            print("\n--- Batch Creation Results ---")
            print(f"Successfully created KBs: {results['success']}")
            if results["failed"]:
                print("Failed KBs:")
                for kb_name, error_msg in results["failed"].items():
                    print(f"  - {kb_name}: {error_msg}")
        finally:
            FileHelper.cleanup_files([file1_path, file2_path])
        print("\n🎉 Batch create knowledge bases demo completed.")

    def batch_delete_knowledge_bases_demo(self) -> None:
        """Demonstrates batch deletion of knowledge bases."""
        print("\n" + "#" * 20 + " Batch Delete Knowledge Bases Demo " + "#" * 20)

        # First, create some knowledge bases to delete
        temp_kb_name_prefix = f"TempDeleteKB-{int(time.time())}"
        kb_names_to_create = [
            f"{temp_kb_name_prefix}-A",
            f"{temp_kb_name_prefix}-B",
            f"{temp_kb_name_prefix}-C",
            f"{temp_kb_name_prefix}-KeywordMatch-1",
            f"{temp_kb_name_prefix}-KeywordMatch-2",
        ]

        created_kb_ids = []
        print("\n--- Creating temporary KBs for deletion demo ---")
        for name in kb_names_to_create:
            kb = self.client.create_knowledge_base(name)
            if kb:
                created_kb_ids.append(kb["id"])
            time.sleep(0.5)  # Avoid hitting rate limits if any

        if not created_kb_ids:
            logging.warning(
                "No temporary knowledge bases created for deletion demo. Aborting."
            )
            return

        try:
            # Option 1: Delete by keyword
            keyword = "KeywordMatch"
            print(f"\n--- Deleting KBs with keyword '{keyword}' ---")
            success_count_kw, failed_count_kw, names_deleted_kw = (
                self.client.delete_knowledge_bases_by_keyword(keyword)
            )
            print(
                f"Result for keyword '{keyword}': Successful={success_count_kw}, Failed={failed_count_kw}"
            )
            print(f"Names deleted by keyword: {names_deleted_kw}")

            # Option 2: Delete all remaining knowledge bases
            print("\n--- Deleting all remaining KBs ---")
            success_count_all, failed_count_all = (
                self.client.delete_all_knowledge_bases()
            )
            print(
                f"Result for deleting all: Successful={success_count_all}, Failed={failed_count_all}"
            )

        except Exception as e:
            logging.error(f"Error during batch deletion demo: {e}")
        print("\n🎉 Batch delete knowledge bases demo completed.")


class ModelManagementDemos:
    """Demo functions for model management functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def models_management_demo(self) -> None:
        """Demonstrates the model management functionality."""
        print("\n" + "#" * 20 + " Models Management Demo " + "#" * 20)

        # List all models
        logging.info("--- Listing all available models ---")
        models = self.client.list_models()
        print("\nAvailable Models:")
        for model in models:
            print(f"- {model}")

        # Get details of a specific model
        logging.info("--- Getting details for the default model ---")
        model_details = self.client.get_model(Config.DEFAULT_MODEL)
        print(f"\nDetails for {Config.DEFAULT_MODEL}: {model_details}")


class ChatManagementDemos:
    """Demo functions for chat management functionality."""

    def __init__(self, client: OpenWebUIClient):
        self.client = client

    def rename_chat_demo(self) -> None:
        """Demonstrates renaming a chat."""
        print("\n" + "#" * 20 + " Rename Chat Demo " + "#" * 20)

        # First create a chat
        old_title = "Old Chat Title"
        new_title = "New Chat Title"

        # Create a new chat
        result = self.client.chat(
            question="What is the capital of France?",
            chat_title=old_title,
        )

        if result and result.get("chat_id"):
            success = self.client.rename_chat(result["chat_id"], new_title)

            if success:
                print(
                    f"✅ Successfully renamed chat from '{old_title}' to '{new_title}'"
                )
            else:
                print(f"❌ Failed to rename chat from '{old_title}' to '{new_title}'")

    def automatic_metadata_demo(self) -> None:
        """Demonstrates automatic tagging and titling, and updating metadata."""
        print("\n" + "#" * 20 + " Automatic Metadata Demo " + "#" * 20)

        # Step 1: Create a chat with automatic titling and tagging enabled
        print("\n--- Step 1: Creating a chat with auto-metadata ---")
        chat_result = self.client.chat(
            question="What are the key principles of functional programming?",
            chat_title="New FP Discussion",
            enable_auto_tagging=True,
            enable_auto_titling=True,
        )

        if not chat_result or not chat_result.get("chat_id"):
            print("❌ Failed to create chat for metadata demo.")
            return

        chat_id = chat_result["chat_id"]
        print(f"✅ Chat created with ID: {chat_id[:8]}...")
        if chat_result.get("suggested_title"):
            print(f"   - Auto-generated Title: '{chat_result['suggested_title']}'")
        if chat_result.get("suggested_tags"):
            print(f"   - Auto-generated Tags: {chat_result['suggested_tags']}")

        # Add another message to the chat
        print("\n--- Step 2: Adding another message to the chat ---")
        self.client.chat(
            question="Can you give an example in Python?",
            chat_title=chat_result.get("suggested_title", "New FP Discussion"),
        )
        print("✅ Added a second message.")
        time.sleep(2)

        # Step 2: Manually trigger a metadata update
        print("\n--- Step 3: Manually regenerating tags and title for the chat ---")
        update_result = self.client.update_chat_metadata(
            chat_id=chat_id,
            regenerate_tags=True,
            regenerate_title=True,
        )

        if update_result:
            print("✅ Metadata update successful.")
            if update_result.get("suggested_title"):
                print(f"   - New Regenerated Title: '{update_result['suggested_title']}'")
            if update_result.get("suggested_tags"):
                print(f"   - New Regenerated Tags: {update_result['suggested_tags']}")
        else:
            print("❌ Failed to update metadata.")

        print("\n🎉 Automatic metadata demo completed.")


# ===============================
# Main Demo Runner
# ===============================


class DemoRunner:
    """Main class to run all demos."""

    def __init__(self):
        self.client = None
        self._validate_config()
        self._initialize_client()

    def _validate_config(self) -> None:
        """Validates the configuration."""
        if not Config.AUTH_TOKEN:
            logging.error(
                "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
            )
            raise ValueError("Missing AUTH_TOKEN")

    def _initialize_client(self) -> None:
        """Initializes the OpenWebUI client."""
        self.client = OpenWebUIClient(
            Config.BASE_URL, Config.AUTH_TOKEN, default_model_id=Config.DEFAULT_MODEL
        )

    def run_all_demos(self) -> None:
        """Runs all available demos."""
        print("🚀 Starting OpenWebUI Chat Client Demos\n")

        # Initialize demo classes
        chat_demos = ChatDemos(self.client)
        rag_demos = RAGDemos(self.client)
        kb_demos = KnowledgeBaseDemos(self.client)
        model_demos = ModelManagementDemos(self.client)
        chat_mgmt_demos = ChatManagementDemos(self.client)
        stream_chat_demos = StreamChatDemos(self.client)

        # Run demos
        try:
            chat_demos.basic_chat_demo()
            time.sleep(2)

            chat_demos.stream_chat_demo()
            time.sleep(2)

            rag_demos.rag_chat_demo()
            time.sleep(2)

            rag_demos.stream_rag_chat_demo()
            time.sleep(2)

            kb_demos.knowledge_base_chat_demo()
            time.sleep(2)

            model_demos.models_management_demo()
            time.sleep(2)

            chat_mgmt_demos.rename_chat_demo()
            time.sleep(2)

            chat_mgmt_demos.automatic_metadata_demo()
            time.sleep(2)

            stream_chat_demos.stream_chat_realtime_update_demo()

        except Exception as e:
            logging.error(f"Error during demo execution: {e}")

        print(
            "\n🎉 All demo scenarios completed. Please check your Open WebUI interface to see the results."
        )

    def run_specific_demo(self, demo_name: str) -> None:
        """Runs a specific demo by name."""
        demo_mapping = {
            "basic_chat": lambda: ChatDemos(self.client).basic_chat_demo(),
            "stream_chat": lambda: ChatDemos(self.client).stream_chat_demo(),
            "stream_chat_follow_up": lambda: ChatDemos(self.client).stream_chat_with_follow_up_demo(),
            "rag_chat": lambda: RAGDemos(self.client).rag_chat_demo(),
            "stream_rag": lambda: RAGDemos(self.client).stream_rag_chat_demo(),
            "knowledge_base": lambda: KnowledgeBaseDemos(
                self.client
            ).knowledge_base_chat_demo(),
            "batch_create_kb": lambda: KnowledgeBaseDemos(
                self.client
            ).batch_create_knowledge_bases_demo(),
            "batch_delete_kb": lambda: KnowledgeBaseDemos(
                self.client
            ).batch_delete_knowledge_bases_demo(),
            "models": lambda: ModelManagementDemos(
                self.client
            ).models_management_demo(),
            "rename_chat": lambda: ChatManagementDemos(self.client).rename_chat_demo(),
            "metadata": lambda: ChatManagementDemos(self.client).automatic_metadata_demo(),
            "stream_image_chat": lambda: ChatDemos(
                self.client
            ).stream_image_chat_demo(),
            "follow_up": lambda: ChatDemos(self.client).chat_with_follow_up_demo(),
            "parallel_follow_up": lambda: ChatDemos(self.client).parallel_chat_with_follow_up_demo(),
            "stream_chat_realtime_update": lambda: StreamChatDemos(self.client).stream_chat_realtime_update_demo(),
        }

        if demo_name in demo_mapping:
            demo_mapping[demo_name]()
        else:
            print(f"Unknown demo: {demo_name}")
            print(f"Available demos: {', '.join(demo_mapping.keys())}")


# ===============================
# Main Execution
# ===============================

if __name__ == "__main__":
    try:
        runner = DemoRunner()

        # Run a specific demo
        # runner.run_specific_demo("parallel_follow_up")
        # runner.run_specific_demo("stream_chat_realtime_update")
        # runner.run_specific_demo("stream_rag")
        # runner.run_specific_demo("batch_delete_kb")
        runner.run_specific_demo("metadata")

        # Or run all demos
        # runner.run_all_demos()

    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
