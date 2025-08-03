#!/usr/bin/env python3
"""
RAG with file upload example for OpenWebUI Chat Client.

This example demonstrates Retrieval Augmented Generation (RAG) functionality
using uploaded files as the knowledge source.

Features demonstrated:
- RAG chat with single file
- RAG chat with multiple files
- Streaming RAG chat
- File upload and cleanup

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/rag_knowledge/file_rag.py
"""

import logging
import os
import sys
from typing import List, Optional

# Add the parent directory to path to import the client and utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv
from utils.file_helpers import TestFileManager, TestContent

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
RAG_MODEL = os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def single_file_rag_example(client: OpenWebUIClient) -> None:
    """Demonstrate RAG with a single file."""
    logger.info("📄 Single File RAG Example")
    logger.info("=" * 35)
    
    with TestFileManager() as file_manager:
        # Create a test file about blockchain
        file_path = file_manager.create_test_file(
            "blockchain_info.txt",
            TestContent.BLOCKCHAIN_CONTENT
        )
        
        if not file_path:
            logger.error("❌ Failed to create test file")
            return
        
        logger.info(f"📁 Created test file: {file_path}")
        
        # Ask a question about the content
        question = "Based on the document, what is the Ouroboros protocol and what makes it special?"
        
        logger.info(f"🎯 Question: {question}")
        
        try:
            result = client.chat(
                question=question,
                chat_title="Blockchain RAG Test",
                rag_files=[file_path],
                model_id=RAG_MODEL,
                folder_name="RAG Examples"
            )
            
            if result and result.get("response"):
                print("\n" + "=" * 60)
                print("🤖 RAG Response:")
                print("=" * 60)
                print(result["response"])
                print("=" * 60)
                logger.info("✅ Single file RAG completed successfully")
            else:
                logger.error("❌ No response received")
                
        except Exception as e:
            logger.error(f"❌ Single file RAG failed: {e}")


def multiple_files_rag_example(client: OpenWebUIClient) -> None:
    """Demonstrate RAG with multiple files."""
    logger.info("\n📚 Multiple Files RAG Example")
    logger.info("=" * 40)
    
    with TestFileManager() as file_manager:
        # Create multiple test files
        files_data = {
            "ai_basics.txt": TestContent.AI_CONTENT,
            "space_exploration.txt": TestContent.SPACE_CONTENT,
            "python_programming.txt": TestContent.PYTHON_CONTENT
        }
        
        created_files = file_manager.create_test_files_batch(files_data)
        file_paths = [path for path in created_files.values() if path]
        
        if not file_paths:
            logger.error("❌ Failed to create test files")
            return
        
        logger.info(f"📁 Created {len(file_paths)} test files")
        for path in file_paths:
            logger.info(f"   - {os.path.basename(path)}")
        
        # Ask a question that spans multiple documents
        question = "Based on the documents, compare artificial intelligence and space exploration in terms of their impact on human advancement."
        
        logger.info(f"🎯 Question: {question}")
        
        try:
            result = client.chat(
                question=question,
                chat_title="Multi-File RAG Analysis",
                rag_files=file_paths,
                model_id=RAG_MODEL,
                folder_name="RAG Examples",
                tags=["rag", "multi-file", "comparison"]
            )
            
            if result and result.get("response"):
                print("\n" + "=" * 60)
                print("🤖 Multi-File RAG Response:")
                print("=" * 60)
                print(result["response"])
                print("=" * 60)
                logger.info("✅ Multiple files RAG completed successfully")
            else:
                logger.error("❌ No response received")
                
        except Exception as e:
            logger.error(f"❌ Multiple files RAG failed: {e}")


def streaming_rag_example(client: OpenWebUIClient) -> None:
    """Demonstrate streaming RAG chat."""
    logger.info("\n📡 Streaming RAG Example")
    logger.info("=" * 35)
    
    with TestFileManager() as file_manager:
        # Create a test file about space exploration
        file_path = file_manager.create_test_file(
            "apollo_mission.txt",
            TestContent.SPACE_CONTENT
        )
        
        if not file_path:
            logger.error("❌ Failed to create test file")
            return
        
        logger.info(f"📁 Created test file: {file_path}")
        
        # Ask a detailed question for streaming response
        question = "Based on the Apollo mission document, provide a detailed explanation of the Apollo program's objectives, key missions, and lasting impact on space exploration."
        
        logger.info(f"🎯 Question: {question}")
        logger.info("💭 Streaming RAG response:")
        
        print("\n" + "=" * 60)
        print("🤖 Streaming RAG Response:")
        print("=" * 60)
        
        try:
            # Stream the RAG response
            for chunk in client.stream_chat(
                question=question,
                chat_title="Apollo Mission Streaming RAG",
                rag_files=[file_path],
                model_id=RAG_MODEL
            ):
                print(chunk, end="", flush=True)
            
            print("\n" + "=" * 60)
            logger.info("✅ Streaming RAG completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Streaming RAG failed: {e}")


def rag_with_follow_up_example(client: OpenWebUIClient) -> None:
    """Demonstrate RAG with follow-up suggestions."""
    logger.info("\n🔄 RAG with Follow-up Suggestions")
    logger.info("=" * 45)
    
    with TestFileManager() as file_manager:
        # Create a test file about AI
        file_path = file_manager.create_test_file(
            "ai_overview.txt",
            TestContent.AI_CONTENT
        )
        
        if not file_path:
            logger.error("❌ Failed to create test file")
            return
        
        logger.info(f"📁 Created test file: {file_path}")
        
        # Ask a question that would benefit from follow-ups
        question = "What is artificial intelligence according to the document?"
        
        logger.info(f"🎯 Question: {question}")
        
        try:
            result = client.chat(
                question=question,
                chat_title="AI RAG with Follow-up",
                rag_files=[file_path],
                model_id=RAG_MODEL,
                enable_follow_up=True
            )
            
            if result and result.get("response"):
                print("\n" + "=" * 60)
                print("🤖 RAG Response:")
                print("=" * 60)
                print(result["response"])
                print("=" * 60)
                
                # Check for follow-up suggestions
                if result.get("follow_ups"):
                    logger.info("🤔 Follow-up suggestions:")
                    for i, follow_up in enumerate(result["follow_ups"], 1):
                        print(f"  {i}. {follow_up}")
                else:
                    logger.info("ℹ️ No follow-up suggestions generated")
                
                logger.info("✅ RAG with follow-up completed successfully")
            else:
                logger.error("❌ No response received")
                
        except Exception as e:
            logger.error(f"❌ RAG with follow-up failed: {e}")


def rag_error_handling_example(client: OpenWebUIClient) -> None:
    """Demonstrate error handling in RAG scenarios."""
    logger.info("\n⚠️ RAG Error Handling Example")
    logger.info("=" * 40)
    
    # Test with non-existent file
    logger.info("🧪 Testing with non-existent file...")
    
    try:
        result = client.chat(
            question="What does the document say?",
            chat_title="RAG Error Test",
            rag_files=["non_existent_file.txt"],
            model_id=RAG_MODEL
        )
        
        if result:
            logger.warning("⚠️ Unexpectedly received response with non-existent file")
        else:
            logger.info("✅ Correctly handled non-existent file")
            
    except Exception as e:
        logger.info(f"✅ Error handled correctly: {e}")
    
    # Test with empty file
    logger.info("🧪 Testing with empty file...")
    
    with TestFileManager() as file_manager:
        empty_file = file_manager.create_test_file("empty.txt", "")
        
        if empty_file:
            try:
                result = client.chat(
                    question="What information is in the document?",
                    chat_title="Empty File RAG Test",
                    rag_files=[empty_file],
                    model_id=RAG_MODEL
                )
                
                if result and result.get("response"):
                    logger.info("✅ Handled empty file gracefully")
                    print(f"Response: {result['response'][:100]}...")
                else:
                    logger.info("ℹ️ No response for empty file")
                    
            except Exception as e:
                logger.info(f"⚠️ Empty file caused error: {e}")


def main() -> None:
    """Main function demonstrating file RAG functionality."""
    logger.info("🚀 OpenWebUI Chat Client - File RAG Examples")
    logger.info("=" * 60)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        return
    
    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
        logger.info(f"🎯 Using RAG model: {RAG_MODEL}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Run RAG examples
    try:
        single_file_rag_example(client)
        multiple_files_rag_example(client)
        streaming_rag_example(client)
        rag_with_follow_up_example(client)
        rag_error_handling_example(client)
        
        logger.info("\n🎉 File RAG examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/rag_knowledge/knowledge_base.py")
        logger.info("   - Try: python examples/rag_knowledge/batch_knowledge_ops.py")
        
    except Exception as e:
        logger.error(f"❌ File RAG examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()