#!/usr/bin/env python3
"""
Model switching functionality example for OpenWebUI Chat Client.

This example demonstrates how to switch models within the same chat conversation,
allowing users to leverage different models for different types of responses.

Features demonstrated:
- Starting a chat with one model
- Switching to a different model mid-conversation
- Maintaining chat context across model switches
- Error handling for model switching

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Multiple models available in OpenWebUI instance

Usage:
    python examples/chat_features/model_switching.py
"""

import logging
import os
import sys
import time
from typing import Optional, List

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Parse parallel models for switching
parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
AVAILABLE_MODELS = [model.strip() for model in parallel_models_str.split(",") if model.strip()]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demonstrate_model_switching(client: OpenWebUIClient, available_models: List[str]) -> None:
    """Demonstrate switching models within a chat."""
    logger.info("🔄 Model Switching Demonstration")
    logger.info("=" * 40)
    
    if len(available_models) < 2:
        logger.warning("⚠️ Need at least 2 models for switching demonstration")
        logger.info(f"Available models: {available_models}")
        return
    
    model1 = available_models[0]
    model2 = available_models[1]
    
    logger.info(f"📋 Starting chat with model: {model1}")
    logger.info(f"📋 Will switch to model: {model2}")
    
    try:
        # Start chat with first model
        chat_title = f"Model Switching Demo - {int(time.time())}"
        question1 = "Hello! What's your name and what are you good at?"
        
        result1 = client.chat(
            question=question1,
            chat_title=chat_title,
            model_id=model1
        )
        
        if result1:
            logger.info(f"✅ First response from {model1}:")
            logger.info(f"   Question: {question1}")
            logger.info(f"   Response: {result1['response'][:100]}...")
            chat_id = result1['chat_id']
            
            # Switch to second model
            logger.info(f"\n🔄 Switching to model: {model2}")
            switch_result = client.switch_chat_model(chat_id, model2)
            
            if switch_result:
                logger.info(f"✅ Successfully switched to {model2}")
                
                # Continue conversation with new model
                question2 = "Now that you've switched, can you tell me about your capabilities in a different style?"
                
                result2 = client.chat(
                    question=question2,
                    chat_title=chat_title,
                    model_id=model2  # Explicitly use new model
                )
                
                if result2:
                    logger.info(f"✅ Second response from {model2}:")
                    logger.info(f"   Question: {question2}")
                    logger.info(f"   Response: {result2['response'][:100]}...")
                    
                    logger.info("\n📊 Model Switching Summary:")
                    logger.info(f"   Chat ID: {chat_id}")
                    logger.info(f"   Initial Model: {model1}")
                    logger.info(f"   Switched Model: {model2}")
                    logger.info(f"   Total Messages: 2")
                else:
                    logger.error("❌ Failed to get response from switched model")
            else:
                logger.error(f"❌ Failed to switch to model {model2}")
        else:
            logger.error(f"❌ Failed to get initial response from {model1}")
            
    except Exception as e:
        logger.error(f"❌ Model switching demonstration failed: {e}")


def main() -> None:
    """Main function demonstrating model switching."""
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        return
    
    # Client initialization
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Get available models
    try:
        server_models = client.list_models()
        if server_models:
            server_model_ids = [model.get('id', '') for model in server_models]
            # Filter available models to only those on the server
            valid_models = [model for model in AVAILABLE_MODELS if model in server_model_ids]
            
            if len(valid_models) >= 2:
                demonstrate_model_switching(client, valid_models)
            else:
                logger.warning(f"⚠️ Only {len(valid_models)} of the specified models are available on server")
                logger.info(f"Specified models: {AVAILABLE_MODELS}")
                logger.info(f"Available on server: {valid_models}")
                
                # Try with first two available models from server
                if len(server_model_ids) >= 2:
                    logger.info("Using first two available models from server")
                    demonstrate_model_switching(client, server_model_ids[:2])
                else:
                    logger.error("❌ Need at least 2 models on server for switching demonstration")
        else:
            logger.error("❌ No models found on server")
            
    except Exception as e:
        logger.error(f"❌ Failed to get models from server: {e}")
        sys.exit(1)
    
    logger.info("🎉 Model switching demonstration completed")


if __name__ == "__main__":
    main()
