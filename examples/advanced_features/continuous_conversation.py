#!/usr/bin/env python3
"""
Continuous Conversation Example for OpenWebUI Chat Client.

This example demonstrates the new continuous conversation features that allow
automated multi-turn conversations using follow-up suggestions.

Features demonstrated:
- Continuous single-model conversations
- Continuous parallel-model conversations  
- Continuous streaming conversations
- Automatic follow-up question selection
- Generic fallback questions when no follow-ups available
- Error handling and conversation management

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_DEFAULT_MODEL (optional)
- Environment variable: OUI_PARALLEL_MODELS (optional)

Usage:
    python examples/advanced_features/continuous_conversation.py
"""

import logging
import os
import sys
from typing import Optional, List

# Add the parent directory to path to import the client and utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
PARALLEL_MODELS = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash").split(",")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def continuous_single_model_example(client: OpenWebUIClient) -> bool:
    """Demonstrate continuous conversation with a single model."""
    logger.info("🔄 Continuous Single-Model Conversation Example")
    logger.info("=" * 60)
    
    initial_question = "Explain the concept of artificial intelligence"
    num_questions = 3
    chat_title = "AI Deep Dive - Continuous"
    
    logger.info(f"🎯 Starting conversation: {initial_question}")
    logger.info(f"📊 Target rounds: {num_questions}")
    
    try:
        result = client.continuous_chat(
            initial_question=initial_question,
            num_questions=num_questions,
            chat_title=chat_title,
            model_id=DEFAULT_MODEL,
            folder_name="Continuous Conversations",
            tags=["ai", "continuous", "deep-dive"],
            enable_auto_tagging=True,
            enable_auto_titling=True
        )
        
        if result:
            logger.info(f"✅ Conversation completed: {result['total_rounds']} rounds")
            logger.info(f"💬 Chat ID: {result['chat_id']}")
            
            # Strict validation: check if we actually got meaningful results
            if not result.get('total_rounds') or result['total_rounds'] != num_questions:
                logger.error(f"❌ Continuous conversation failed: Expected {num_questions} rounds, got {result.get('total_rounds', 0)}")
                return False
            
            if not result.get('conversation_history'):
                logger.error("❌ Continuous conversation failed: No conversation history returned")
                return False
            
            # Validate each round has proper structure
            for round_data in result['conversation_history']:
                if not round_data.get('response') or len(round_data.get('response', '').strip()) < 10:
                    logger.error(f"❌ Round {round_data.get('round', '?')} failed: Invalid or empty response")
                    return False
                    
            print("\n" + "=" * 60)
            print("📚 CONVERSATION SUMMARY")
            print("=" * 60)
            
            for round_data in result['conversation_history']:
                print(f"\n🔹 Round {round_data['round']}:")
                print(f"❓ Question: {round_data['question']}")
                print(f"🤖 Response: {round_data['response'][:200]}...")
                
                if 'follow_ups' in round_data:
                    print(f"🤔 Follow-ups suggested: {len(round_data['follow_ups'])}")
                    for i, follow_up in enumerate(round_data['follow_ups'][:3], 1):
                        print(f"   {i}. {follow_up}")
            
            if 'suggested_tags' in result:
                print(f"\n🏷️ Auto-generated tags: {result['suggested_tags']}")
            if 'suggested_title' in result:
                print(f"📝 Auto-generated title: {result['suggested_title']}")
                
            return True
                
        else:
            logger.error("❌ Continuous conversation failed: No result returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Continuous single-model conversation failed: {e}")
        raise  # Re-raise to be handled by main function


def continuous_parallel_model_example(client: OpenWebUIClient) -> bool:
    """Demonstrate continuous conversation with multiple models in parallel."""
    logger.info("\n🔄 Continuous Parallel-Model Conversation Example")
    logger.info("=" * 60)
    
    initial_question = "What are the most significant challenges in modern web development?"
    num_questions = 2
    chat_title = "Web Dev Challenges - Multi-Model Analysis"
    
    logger.info(f"🎯 Starting parallel conversation: {initial_question}")
    logger.info(f"🤖 Models: {PARALLEL_MODELS}")
    logger.info(f"📊 Target rounds: {num_questions}")
    
    try:
        result = client.continuous_parallel_chat(
            initial_question=initial_question,
            num_questions=num_questions,
            chat_title=chat_title,
            model_ids=PARALLEL_MODELS,
            folder_name="Continuous Conversations",
            tags=["web-dev", "parallel", "analysis"],
        )
        
        if result:
            logger.info(f"✅ Parallel conversation completed: {result['total_rounds']} rounds")
            logger.info(f"💬 Chat ID: {result['chat_id']}")
            
            # Strict validation: check if we actually got meaningful results
            if not result.get('total_rounds') or result['total_rounds'] != num_questions:
                logger.error(f"❌ Continuous parallel conversation failed: Expected {num_questions} rounds, got {result.get('total_rounds', 0)}")
                return False
            
            if not result.get('conversation_history'):
                logger.error("❌ Continuous parallel conversation failed: No conversation history returned")
                return False
                
            # Validate each round has responses from all models
            for round_data in result['conversation_history']:
                if not round_data.get('responses'):
                    logger.error(f"❌ Round {round_data.get('round', '?')} failed: No model responses")
                    return False
                
                # Check that we got responses from all expected models
                expected_models = set(PARALLEL_MODELS)
                actual_models = set(round_data['responses'].keys())
                if not expected_models.issubset(actual_models):
                    missing_models = expected_models - actual_models
                    logger.error(f"❌ Round {round_data.get('round', '?')} failed: Missing responses from models: {missing_models}")
                    return False
                
                # Validate response quality
                for model_id, response_data in round_data['responses'].items():
                    if not response_data.get('content') or len(response_data.get('content', '').strip()) < 10:
                        logger.error(f"❌ Round {round_data.get('round', '?')} failed: Invalid response from {model_id}")
                        return False
                        
            print("\n" + "=" * 60)
            print("🌐 PARALLEL CONVERSATION SUMMARY")
            print("=" * 60)
            
            for round_data in result['conversation_history']:
                print(f"\n🔹 Round {round_data['round']}:")
                print(f"❓ Question: {round_data['question']}")
                
                for model_id, response_data in round_data['responses'].items():
                    print(f"\n🤖 {model_id}:")
                    print(f"   {response_data.get('content', 'No response')[:150]}...")
                
                if 'follow_ups' in round_data:
                    print(f"\n🤔 Combined follow-ups: {len(round_data['follow_ups'])}")
                    for i, follow_up in enumerate(round_data['follow_ups'][:3], 1):
                        print(f"   {i}. {follow_up}")
                        
            return True
                
        else:
            logger.error("❌ Continuous parallel conversation failed: No result returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Continuous parallel conversation failed: {e}")
        raise  # Re-raise to be handled by main function


def continuous_streaming_example(client: OpenWebUIClient) -> bool:
    """Demonstrate continuous conversation with streaming responses."""
    logger.info("\n🔄 Continuous Streaming Conversation Example")
    logger.info("=" * 60)
    
    initial_question = "Explain quantum computing in simple terms"
    num_questions = 2
    chat_title = "Quantum Computing - Streaming Discovery"
    
    logger.info(f"🎯 Starting streaming conversation: {initial_question}")
    logger.info(f"📊 Target rounds: {num_questions}")
    
    try:
        print("\n" + "=" * 60)
        print("📡 STREAMING CONVERSATION")
        print("=" * 60)
        
        final_result = None
        current_round = 0
        completed_rounds = 0
        
        for chunk in client.continuous_stream_chat(
            initial_question=initial_question,
            num_questions=num_questions,
            chat_title=chat_title,
            model_id=DEFAULT_MODEL,
            folder_name="Continuous Conversations",
            tags=["quantum", "streaming", "educational"]
        ):
            chunk_type = chunk.get("type")
            
            if chunk_type == "round_start":
                current_round = chunk["round"]
                print(f"\n🔹 Round {current_round} Starting...")
                print(f"❓ Question: {chunk['question']}")
                print("🤖 Response: ", end="", flush=True)
                
            elif chunk_type == "round_complete":
                completed_rounds += 1
                print(f"\n✅ Round {chunk['round']} completed")
                if chunk.get("follow_ups"):
                    print(f"🤔 Follow-ups available: {len(chunk['follow_ups'])}")
                    for i, follow_up in enumerate(chunk['follow_ups'][:2], 1):
                        print(f"   {i}. {follow_up}")
                        
            elif chunk_type == "conversation_complete":
                final_result = chunk["summary"]
                print(f"\n🎉 Streaming conversation completed!")
                
            elif chunk_type == "round_error":
                print(f"\n❌ Error in round {chunk['round']}: {chunk['error']}")
                logger.error(f"Streaming conversation round error: {chunk['error']}")
        
        if final_result:
            logger.info(f"✅ Streaming conversation summary:")
            logger.info(f"   Total rounds: {final_result['total_rounds']}")
            logger.info(f"   Chat ID: {final_result['chat_id']}")
            
            # Strict validation: check if we actually got meaningful results
            if not final_result.get('total_rounds') or final_result['total_rounds'] != num_questions:
                logger.error(f"❌ Streaming conversation failed: Expected {num_questions} rounds, got {final_result.get('total_rounds', 0)}")
                return False
            
            if completed_rounds != num_questions:
                logger.error(f"❌ Streaming conversation failed: Expected {num_questions} completed rounds, got {completed_rounds}")
                return False
                
            return True
        else:
            logger.error("❌ Streaming conversation failed: No final result returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Continuous streaming conversation failed: {e}")
        raise  # Re-raise to be handled by main function


def error_handling_example(client: OpenWebUIClient) -> None:
    """Demonstrate error handling in continuous conversations."""
    logger.info("\n⚠️ Error Handling Example")
    logger.info("=" * 40)
    
    # Test with invalid parameters
    logger.info("🧪 Testing invalid parameters...")
    
    # Test with zero questions
    result = client.continuous_chat(
        initial_question="Test",
        num_questions=0,  # Invalid
        chat_title="Error Test"
    )
    logger.info(f"Zero questions result: {result}")
    
    # Test parallel chat with empty model list
    result = client.continuous_parallel_chat(
        initial_question="Test", 
        num_questions=1,
        chat_title="Error Test",
        model_ids=[]  # Invalid
    )
    logger.info(f"Empty models result: {result}")
    
    logger.info("✅ Error handling examples completed")


def main() -> None:
    """Main function demonstrating continuous conversation features."""
    logger.info("🚀 OpenWebUI Chat Client - Continuous Conversation Examples")
    logger.info("=" * 80)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        # Test basic connectivity with model listing
        models = client.list_models()
        if not models:
            logger.error("❌ Failed to list models - connectivity or authentication issue")
            sys.exit(1)
        logger.info(f"Successfully listed {len(models)} models.")
        logger.info("✅ Client initialized successfully")
        logger.info(f"🔗 Base URL: {BASE_URL}")
        logger.info(f"🤖 Default model: {DEFAULT_MODEL}")
        logger.info(f"🔄 Parallel models: {PARALLEL_MODELS}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Run functional examples and track success
    functional_success_count = 0
    functional_examples = [
        ("single_model", continuous_single_model_example),
        ("parallel_model", continuous_parallel_model_example),
        ("streaming", continuous_streaming_example)
    ]
    
    try:
        # Run functional examples
        for example_name, example_func in functional_examples:
            try:
                if example_func(client):
                    functional_success_count += 1
                    logger.info(f"✅ {example_name} example completed successfully")
                else:
                    logger.error(f"❌ {example_name} example failed")
            except Exception as e:
                logger.error(f"❌ {example_name} example failed with exception: {e}")
                # Don't increment success count for exceptions
        
        # Run error handling example (doesn't count toward functional success)
        try:
            error_handling_example(client)
            logger.info("✅ Error handling example completed")
        except Exception as e:
            logger.warning(f"⚠️ Error handling example failed: {e}")
        
        # Strict validation: require ALL functional examples to succeed
        total_functional = len(functional_examples)
        if functional_success_count == 0:
            logger.error("❌ All continuous conversation examples failed to complete successfully")
            logger.error("This indicates a serious connectivity, authentication, or functionality issue")
            sys.exit(1)
        elif functional_success_count < total_functional:
            logger.error(f"❌ Only {functional_success_count}/{total_functional} functional examples succeeded")
            logger.error("Integration test requires all functional examples to work properly")
            logger.error("This indicates issues with continuous conversation functionality")
            sys.exit(1)
        
        # All functional examples succeeded
        logger.info(f"\n🎉 All continuous conversation examples completed successfully: {functional_success_count}/{total_functional}!")
        logger.info("💡 Key features demonstrated:")
        logger.info("   ✓ Automatic follow-up question generation and selection")
        logger.info("   ✓ Single, parallel, and streaming conversation modes")
        logger.info("   ✓ Generic fallback questions when follow-ups unavailable")
        logger.info("   ✓ Conversation organization with folders and tags")
        logger.info("   ✓ Auto-tagging and auto-titling capabilities")
        logger.info("   ✓ Comprehensive error handling")
        
        logger.info("\n📚 Next steps:")
        logger.info("   - Check your OpenWebUI interface to see the created conversations")
        logger.info("   - Try: python examples/chat_features/streaming_chat.py")
        logger.info("   - Try: python examples/rag_knowledge/file_rag.py")
        
    except Exception as e:
        logger.error(f"❌ Continuous conversation examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()