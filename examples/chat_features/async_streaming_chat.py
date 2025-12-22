#!/usr/bin/env python3
"""
Async streaming chat example for OpenWebUI Chat Client.

This example demonstrates real-time async streaming chat functionality, where responses
are received and displayed incrementally as they are generated using asyncio.

Features demonstrated:
- Async streaming chat with real-time output
- Multiple concurrent streaming sessions
- Async context management
- Error handling in async streaming

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_DEFAULT_MODEL (optional)

Usage:
    python examples/chat_features/async_streaming_chat.py
"""

import asyncio
import logging
import os
import sys
import time
from typing import Optional

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from openwebui_chat_client import AsyncOpenWebUIClient
from dotenv import load_dotenv

# Load environment variables from getting_started directory
env_path = os.path.join(os.path.dirname(__file__), '../getting_started/.env')
load_dotenv(env_path)

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
# Optional: Set to 'true' to clean up all chats before running tests
CLEANUP_BEFORE_TEST = os.getenv("OUI_CLEANUP_BEFORE_TEST", "false").lower() == "true"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def basic_streaming_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate basic async streaming chat functionality."""
    logger.info("🌊 Basic Async Streaming Example")
    logger.info("=" * 40)
    
    print("\n🤖 Streaming Response: ", end="", flush=True)
    
    start_time = time.time()
    full_response = ""
    chunk_count = 0
    
    async for chunk in client.stream_chat(
        question="Explain what makes Python a great programming language in 3 bullet points.",
        chat_title="Async Streaming Demo - Basic"
    ):
        print(chunk, end="", flush=True)
        full_response += chunk
        chunk_count += 1
    
    elapsed_time = time.time() - start_time
    print()  # New line after streaming completes
    
    if full_response:
        logger.info(f"✅ Streaming completed in {elapsed_time:.2f}s")
        logger.info(f"   Received {len(full_response)} characters in {chunk_count} chunks")
        logger.info(f"   Average: {len(full_response) / elapsed_time:.1f} chars/sec")
        return True
    else:
        logger.error("❌ Failed to get streaming response")
        return False


async def streaming_with_timing_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate streaming with timing analysis."""
    logger.info("\n⏱️ Streaming with Timing Analysis")
    logger.info("=" * 40)
    
    print("\n🤖 Response: ", end="", flush=True)
    
    start_time = time.time()
    first_chunk_time = None
    chunk_times = []
    full_response = ""
    
    async for chunk in client.stream_chat(
        question="What is machine learning? Give a brief explanation.",
        chat_title="Async Streaming Demo - Timing"
    ):
        current_time = time.time()
        
        if first_chunk_time is None:
            first_chunk_time = current_time - start_time
        
        chunk_times.append(current_time)
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print()  # New line
    
    if full_response and first_chunk_time is not None:
        total_time = time.time() - start_time
        
        logger.info(f"✅ Timing Analysis:")
        logger.info(f"   Time to first chunk: {first_chunk_time*1000:.0f}ms")
        logger.info(f"   Total streaming time: {total_time:.2f}s")
        logger.info(f"   Number of chunks: {len(chunk_times)}")
        
        if len(chunk_times) > 1:
            avg_interval = (chunk_times[-1] - chunk_times[0]) / (len(chunk_times) - 1)
            logger.info(f"   Average chunk interval: {avg_interval*1000:.0f}ms")
        
        return True
    else:
        logger.error("❌ Failed to get streaming response")
        return False


async def concurrent_streaming_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate multiple concurrent streaming sessions."""
    logger.info("\n⚡ Concurrent Streaming Example")
    logger.info("=" * 40)
    
    questions = [
        ("What is 10 * 10?", "Concurrent Stream - Math"),
        ("Name the largest ocean", "Concurrent Stream - Geography"),
    ]
    
    logger.info(f"📤 Starting {len(questions)} concurrent streaming sessions...")
    
    async def stream_question(question: str, title: str, index: int) -> tuple:
        """Stream a single question and collect the response."""
        response_text = ""
        start = time.time()
        
        async for chunk in client.stream_chat(question=question, chat_title=title):
            response_text += chunk
        
        elapsed = time.time() - start
        return (index, question, response_text, elapsed)
    
    # Create tasks for concurrent streaming
    tasks = [
        stream_question(q, t, i) 
        for i, (q, t) in enumerate(questions)
    ]
    
    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = 0
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"   ❌ Stream failed: {result}")
        else:
            idx, question, response, elapsed = result
            short_response = response[:60] + "..." if len(response) > 60 else response
            short_response = short_response.replace('\n', ' ')
            print(f"   ✅ Q{idx+1}: {question[:30]}...")
            print(f"      A: {short_response} ({elapsed:.2f}s)")
            success_count += 1
    
    logger.info(f"🎯 Completed {success_count}/{len(questions)} concurrent streams")
    return success_count > 0


async def streaming_error_handling_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate error handling in async streaming scenarios."""
    logger.info("\n🛡️ Streaming Error Handling Example")
    logger.info("=" * 40)
    
    # Test 1: Normal streaming with error handling
    logger.info("Test 1: Streaming with try-except...")
    try:
        chunk_count = 0
        async for chunk in client.stream_chat(
            question="Say hello in three languages",
            chat_title="Async Streaming Demo - Error Handling"
        ):
            chunk_count += 1
        
        if chunk_count > 0:
            logger.info(f"   ✅ Received {chunk_count} chunks successfully")
        else:
            logger.warning("   ⚠️ Received 0 chunks")
            
    except Exception as e:
        logger.error(f"   ❌ Streaming error: {e}")
        return False
    
    # Test 2: Demonstrate graceful handling of potential issues
    logger.info("Test 2: Streaming with timeout awareness...")
    try:
        start_time = time.time()
        response_parts = []
        
        async for chunk in client.stream_chat(
            question="What's 2+2?",
            chat_title="Async Streaming Demo - Timeout Test"
        ):
            elapsed = time.time() - start_time
            response_parts.append(chunk)
            
            # Demonstrate timeout awareness (not actually timing out)
            if elapsed > 30:  # 30 second warning threshold
                logger.warning("   ⚠️ Response taking longer than expected")
        
        full_response = "".join(response_parts)
        logger.info(f"   ✅ Completed in {time.time() - start_time:.2f}s: {full_response[:50]}...")
        
    except Exception as e:
        logger.error(f"   ❌ Error during streaming: {e}")
        return False
    
    return True


async def streaming_with_context_manager_example() -> bool:
    """Demonstrate streaming with async context manager."""
    logger.info("\n🔒 Streaming with Context Manager")
    logger.info("=" * 40)
    
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return False
    
    # Using async with ensures proper cleanup even if streaming is interrupted
    async with AsyncOpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
        logger.info("✅ Client created with context manager")
        
        print("\n🤖 Streaming: ", end="", flush=True)
        
        full_response = ""
        async for chunk in client.stream_chat(
            question="What is Pi?",
            chat_title="Async Streaming Demo - Context Manager"
        ):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print()  # New line
        
        if full_response:
            logger.info(f"   ✅ Received {len(full_response)} characters")
        
    # Client is automatically closed here
    logger.info("✅ Client automatically closed after context exit")
    return True


async def multi_turn_streaming_example(client: AsyncOpenWebUIClient) -> bool:
    """
    Demonstrate multi-turn conversation with streaming on the same chat.
    
    This example shows how to:
    1. Start a conversation with an initial question
    2. Continue the conversation with follow-up questions in the same chat
    3. Stream responses for each turn
    
    Note: The chat_title uniqueness is used to maintain conversation context.
    """
    logger.info("\n💬 Multi-Turn Streaming Conversation Example")
    logger.info("=" * 50)
    
    # Use a unique chat_title to maintain conversation context
    chat_title = "Async Streaming Demo - Multi-Turn Conversation"
    
    # Define conversation turns
    conversation = [
        "What is Python? Give a brief answer.",
        "What are its main advantages?",
        "Can you give me a simple code example?",
    ]
    
    logger.info(f"📋 Starting {len(conversation)}-turn conversation...")
    logger.info(f"   Chat title: '{chat_title}'")
    
    try:
        for turn, question in enumerate(conversation, 1):
            logger.info(f"\n🔹 Turn {turn}/{len(conversation)}")
            logger.info(f"   ❓ Question: {question}")
            print(f"\n   🤖 Response: ", end="", flush=True)
            
            full_response = ""
            
            # Stream the response
            # Using same chat_title ensures continuation in the same chat
            async for chunk in client.stream_chat(
                question=question,
                chat_title=chat_title
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after streaming
            logger.info(f"   ✅ Received {len(full_response)} characters")
        
        logger.info(f"\n🎉 Multi-turn conversation completed!")
        logger.info(f"   Total turns: {len(conversation)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Multi-turn streaming failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main() -> None:
    """Main async function demonstrating streaming functionality."""
    logger.info("🚀 AsyncOpenWebUIClient - Streaming Examples")
    logger.info("=" * 60)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Client initialization
    client: Optional[AsyncOpenWebUIClient] = None
    try:
        client = AsyncOpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        
        # Verify connectivity
        models = await client.list_models()
        if not models:
            logger.error("❌ Failed to connect to OpenWebUI")
            sys.exit(1)
        logger.info(f"✅ Connected. Found {len(models)} models")
        
        # 🧹 Optional: Clean up all existing chats before running tests
        # Enable by setting OUI_CLEANUP_BEFORE_TEST=true
        if CLEANUP_BEFORE_TEST:
            logger.info("🧹 Cleaning up existing chats for clean test environment...")
            cleanup_success = await client.delete_all_chats()
            if cleanup_success:
                logger.info("✅ Test environment cleaned (all previous chats deleted)")
            else:
                logger.warning("⚠️ Could not clean up previous chats, continuing anyway...")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Run streaming examples
    # Format: (name, func, needs_client)
    # If needs_client is False, the function creates its own client
    examples = [
        # ("basic_streaming", basic_streaming_example, True),
        # ("streaming_with_timing", streaming_with_timing_example, True),
        # ("concurrent_streaming", concurrent_streaming_example, True),
        # ("streaming_error_handling", streaming_error_handling_example, True),
        ("multi_turn_streaming", multi_turn_streaming_example, True),
        # ("streaming_with_context_manager", streaming_with_context_manager_example, False),
    ]
    
    success_count = 0
    try:
        for example_name, example_func, needs_client in examples:
            try:
                logger.info("\n" + "=" * 60)
                if needs_client:
                    result = await example_func(client)
                else:
                    result = await example_func()
                
                if result:
                    success_count += 1
                    logger.info(f"✅ {example_name} completed successfully")
                else:
                    logger.error(f"❌ {example_name} failed")
            except Exception as e:
                logger.error(f"❌ {example_name} failed with exception: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        total_examples = len(examples)
        logger.info(f"\n🎉 Streaming examples completed: {success_count}/{total_examples}")
        
        if success_count < total_examples // 2:
            logger.error("❌ Too many examples failed")
            sys.exit(1)
            
    finally:
        if client:
            await client.close()
            logger.info("🔌 Client connection closed")


if __name__ == "__main__":
    asyncio.run(main())
