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
        
        if not result:
            logger.error("❌ Continuous conversation returned None")
            return False
            
        # Type check the result
        if not isinstance(result, dict):
            logger.error(f"❌ Continuous conversation returned unexpected type: {type(result)}")
            return False
        
        logger.info(f"✅ Conversation completed: {result.get('total_rounds', 0)} rounds")
        logger.info(f"💬 Chat ID: {result.get('chat_id', 'N/A')}")
        
        # Strict validation: check if we actually got meaningful results
        total_rounds = result.get('total_rounds', 0)
        if not total_rounds or total_rounds != num_questions:
            logger.error(f"❌ Continuous conversation failed: Expected {num_questions} rounds, got {total_rounds}")
            return False
        
        conversation_history = result.get('conversation_history', [])
        if not conversation_history:
            logger.error("❌ Continuous conversation failed: No conversation history returned")
            return False
        
        if len(conversation_history) != num_questions:
            logger.error(f"❌ Continuous conversation failed: Expected {num_questions} history entries, got {len(conversation_history)}")
            return False
        
        # Validate each round has proper structure
        for round_data in conversation_history:
            if not isinstance(round_data, dict):
                logger.error(f"❌ Round data is not a dictionary: {type(round_data)}")
                return False
                
            round_num = round_data.get('round', '?')
            response = round_data.get('response', '')
            
            if not response or not isinstance(response, str) or len(response.strip()) < 10:
                logger.error(f"❌ Round {round_num} failed: Invalid or empty response: {response[:50] if response else 'None'}...")
                return False
                
        print("\n" + "=" * 60)
        print("📚 CONVERSATION SUMMARY")
        print("=" * 60)
        
        for round_data in conversation_history:
            print(f"\n🔹 Round {round_data.get('round', '?')}:")
            print(f"❓ Question: {round_data.get('question', 'N/A')}")
            print(f"🤖 Response: {round_data.get('response', 'N/A')[:200]}...")
            
            follow_ups = round_data.get('follow_ups', [])
            if follow_ups and isinstance(follow_ups, list):
                print(f"🤔 Follow-ups suggested: {len(follow_ups)}")
                for i, follow_up in enumerate(follow_ups[:3], 1):
                    print(f"   {i}. {follow_up}")
        
        suggested_tags = result.get('suggested_tags', [])
        if suggested_tags:
            print(f"\n🏷️ Auto-generated tags: {suggested_tags}")
        
        suggested_title = result.get('suggested_title')
        if suggested_title:
            print(f"📝 Auto-generated title: {suggested_title}")
            
        return True
                
    except ValueError as e:
        logger.error(f"❌ Continuous single-model conversation validation error: {e}")
        return False
    except TypeError as e:
        logger.error(f"❌ Continuous single-model conversation type error: {e}")
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
    
    # Validate parallel models
    if not PARALLEL_MODELS or len(PARALLEL_MODELS) == 0:
        logger.error("❌ PARALLEL_MODELS is empty or not set")
        return False
    
    # Clean up model names (remove empty strings)
    cleaned_models = [model.strip() for model in PARALLEL_MODELS if model.strip()]
    if not cleaned_models:
        logger.error("❌ No valid models in PARALLEL_MODELS after cleanup")
        return False
    
    logger.info(f"🎯 Starting parallel conversation: {initial_question}")
    logger.info(f"🤖 Models: {cleaned_models}")
    logger.info(f"📊 Target rounds: {num_questions}")
    
    try:
        result = client.continuous_parallel_chat(
            initial_question=initial_question,
            num_questions=num_questions,
            chat_title=chat_title,
            model_ids=cleaned_models,
            folder_name="Continuous Conversations",
            tags=["web-dev", "parallel", "analysis"],
        )
        
        if not result:
            logger.error("❌ Continuous parallel conversation returned None")
            return False
            
        # Type check the result
        if not isinstance(result, dict):
            logger.error(f"❌ Continuous parallel conversation returned unexpected type: {type(result)}")
            return False
        
        logger.info(f"✅ Parallel conversation completed: {result.get('total_rounds', 0)} rounds")
        logger.info(f"💬 Chat ID: {result.get('chat_id', 'N/A')}")
        
        # Strict validation: check if we actually got meaningful results
        total_rounds = result.get('total_rounds', 0)
        if not total_rounds or total_rounds != num_questions:
            logger.error(f"❌ Continuous parallel conversation failed: Expected {num_questions} rounds, got {total_rounds}")
            return False
        
        conversation_history = result.get('conversation_history', [])
        if not conversation_history:
            logger.error("❌ Continuous parallel conversation failed: No conversation history returned")
            return False
            
        if len(conversation_history) != num_questions:
            logger.error(f"❌ Continuous parallel conversation failed: Expected {num_questions} history entries, got {len(conversation_history)}")
            return False
            
        # Validate each round has responses from all models
        for round_data in conversation_history:
            if not isinstance(round_data, dict):
                logger.error(f"❌ Round data is not a dictionary: {type(round_data)}")
                return False
                
            round_num = round_data.get('round', '?')
            responses = round_data.get('responses')
            
            if not responses:
                logger.error(f"❌ Round {round_num} failed: No model responses")
                return False
            
            # Check if responses is a dictionary as expected
            if not isinstance(responses, dict):
                logger.error(f"❌ Round {round_num} failed: Unexpected type for responses: {type(responses)}")
                return False
            
            # Check that we got responses from all expected models
            expected_models = set(cleaned_models)
            actual_models = set(responses.keys())
            if not expected_models.issubset(actual_models):
                missing_models = expected_models - actual_models
                logger.error(f"❌ Round {round_num} failed: Missing responses from models: {missing_models}")
                return False
            
            # Validate response quality with robust type checking
            for model_id, response_data in responses.items():
                if not isinstance(response_data, dict):
                    logger.error(f"❌ Round {round_num} failed: Invalid response data type for {model_id}: {type(response_data)}")
                    logger.error(f"   Response data: {str(response_data)[:100]}...")
                    return False
                    
                content = response_data.get('content', '')
                if not content or not isinstance(content, str) or len(content.strip()) < 10:
                    logger.error(f"❌ Round {round_num} failed: Invalid response from {model_id}: {content[:50] if content else 'None'}...")
                    return False
                    
                # Check follow_ups if present
                follow_ups = response_data.get('follow_ups')
                if follow_ups is not None and not isinstance(follow_ups, (list, type(None))):
                    logger.warning(f"⚠️ Round {round_num}: Unexpected follow_ups type for {model_id}: {type(follow_ups)}")
                    # Convert to None to avoid issues downstream
                    response_data['follow_ups'] = None
                        
        print("\n" + "=" * 60)
        print("🌐 PARALLEL CONVERSATION SUMMARY")
        print("=" * 60)
        
        for round_data in conversation_history:
            print(f"\n🔹 Round {round_data.get('round', '?')}:")
            print(f"❓ Question: {round_data.get('question', 'N/A')}")
            
            responses = round_data.get('responses', {})
            if isinstance(responses, dict):
                for model_id, response_data in responses.items():
                    print(f"\n🤖 {model_id}:")
                    if isinstance(response_data, dict):
                        content = response_data.get('content', 'No response')
                    else:
                        content = str(response_data)
                    print(f"   {content[:150]}...")
            else:
                print(f"   ⚠️ Unexpected response format: {type(responses)}")
            
            follow_ups = round_data.get('follow_ups', [])
            if follow_ups and isinstance(follow_ups, list):
                print(f"\n🤔 Combined follow-ups: {len(follow_ups)}")
                for i, follow_up in enumerate(follow_ups[:3], 1):
                    print(f"   {i}. {follow_up}")
                    
        return True
                
    except ValueError as e:
        logger.error(f"❌ Continuous parallel conversation validation error: {e}")
        return False
    except TypeError as e:
        logger.error(f"❌ Continuous parallel conversation type error: {e}")
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
        error_count = 0
        
        try:
            stream_generator = client.continuous_stream_chat(
                initial_question=initial_question,
                num_questions=num_questions,
                chat_title=chat_title,
                model_id=DEFAULT_MODEL,
                folder_name="Continuous Conversations",
                tags=["quantum", "streaming", "educational"]
            )
            
            for chunk in stream_generator:
                if not isinstance(chunk, dict):
                    logger.warning(f"Unexpected chunk type: {type(chunk)}")
                    continue
                    
                chunk_type = chunk.get("type")
                
                if chunk_type == "round_start":
                    current_round = chunk.get("round", 0)
                    print(f"\n🔹 Round {current_round} Starting...")
                    question = chunk.get('question', 'N/A')
                    print(f"❓ Question: {question}")
                    print("🤖 Response: ", end="", flush=True)
                    
                elif chunk_type == "round_complete":
                    completed_rounds += 1
                    round_num = chunk.get('round', '?')
                    print(f"\n✅ Round {round_num} completed")
                    follow_ups = chunk.get("follow_ups", [])
                    if follow_ups and isinstance(follow_ups, list):
                        print(f"🤔 Follow-ups available: {len(follow_ups)}")
                        for i, follow_up in enumerate(follow_ups[:2], 1):
                            if isinstance(follow_up, str):
                                print(f"   {i}. {follow_up}")
                            
                elif chunk_type == "conversation_complete":
                    summary = chunk.get("summary")
                    if isinstance(summary, dict):
                        final_result = summary
                        print(f"\n🎉 Streaming conversation completed!")
                    else:
                        logger.warning(f"Unexpected summary type: {type(summary)}")
                        
                elif chunk_type == "round_error":
                    error_count += 1
                    round_num = chunk.get('round', '?')
                    error_msg = chunk.get('error', 'Unknown error')
                    print(f"\n❌ Error in round {round_num}: {error_msg}")
                    logger.error(f"Streaming conversation round error: {error_msg}")
                    
                elif chunk_type == "content":
                    # Handle streaming content chunks
                    content = chunk.get("content", "")
                    if isinstance(content, str):
                        print(content, end="", flush=True)
                        
        except Exception as stream_error:
            logger.error(f"Streaming generator error: {stream_error}")
            return False
        
        if final_result:
            if not isinstance(final_result, dict):
                logger.error(f"Final result is not a dictionary: {type(final_result)}")
                return False
                
            logger.info(f"✅ Streaming conversation summary:")
            
            total_rounds = final_result.get('total_rounds', 0)
            chat_id = final_result.get('chat_id', 'N/A')
            
            logger.info(f"   Total rounds: {total_rounds}")
            logger.info(f"   Chat ID: {chat_id}")
            
            # Strict validation: check if we actually got meaningful results
            if not total_rounds or total_rounds != num_questions:
                logger.error(f"❌ Streaming conversation failed: Expected {num_questions} rounds, got {total_rounds}")
                return False
            
            if completed_rounds != num_questions:
                logger.error(f"❌ Streaming conversation failed: Expected {num_questions} completed rounds, got {completed_rounds}")
                return False
            
            if error_count > 0:
                logger.warning(f"⚠️ Streaming conversation had {error_count} errors but completed")
                
            return True
        else:
            logger.error("❌ Streaming conversation failed: No final result returned")
            return False
            
    except ValueError as e:
        logger.error(f"❌ Continuous streaming conversation validation error: {e}")
        return False
    except TypeError as e:
        logger.error(f"❌ Continuous streaming conversation type error: {e}")
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