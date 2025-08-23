#!/usr/bin/env python3
"""
Model management operations example for OpenWebUI Chat Client.

This example demonstrates comprehensive model management functionality including
listing, creating, updating, and deleting models.

Features demonstrated:
- Listing available models and base models
- Getting model details with retry logic
- Creating custom models with configuration
- Updating existing model parameters
- Deleting models safely
- Model validation and error handling

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Admin permissions for model creation/deletion

Usage:
    python examples/model_management/model_operations.py
"""

import logging
import os
import sys
import json
import time
from typing import Optional, Dict, Any, List

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

# Test model configuration
TEST_MODEL_ID = "example-test-model-2024"
TEST_MODEL_NAME = "Example Test Model"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def list_models_example(client: OpenWebUIClient) -> None:
    """Demonstrate listing available models."""
    logger.info("📋 Listing Available Models")
    logger.info("=" * 35)
    
    try:
        # List all models
        models = client.list_models()
        if models:
            logger.info(f"✅ Found {len(models)} models:")
            for i, model in enumerate(models[:10], 1):  # Show first 10
                model_name = model.get('name', 'Unknown')
                model_id = model.get('id', 'Unknown')
                logger.info(f"   {i:2d}. {model_name} ({model_id})")
            
            if len(models) > 10:
                logger.info(f"   ... and {len(models) - 10} more models")
        else:
            logger.warning("⚠️ No models found")
    
    except Exception as e:
        logger.error(f"❌ Failed to list models: {e}")


def list_base_models_example(client: OpenWebUIClient) -> None:
    """Demonstrate listing base models."""
    logger.info("\n🏗️ Listing Base Models")
    logger.info("=" * 30)
    
    try:
        # List base models
        base_models = client.list_base_models()
        if base_models:
            logger.info(f"✅ Found {len(base_models)} base models:")
            for i, model in enumerate(base_models[:5], 1):  # Show first 5
                model_name = model.get('name', 'Unknown')
                model_id = model.get('id', 'Unknown')
                logger.info(f"   {i}. {model_name} ({model_id})")
            
            if len(base_models) > 5:
                logger.info(f"   ... and {len(base_models) - 5} more base models")
                
            return base_models[0]["id"] if base_models else None
        else:
            logger.warning("⚠️ No base models found")
            return None
    
    except Exception as e:
        logger.error(f"❌ Failed to list base models: {e}")
        return None


def get_model_details_example(client: OpenWebUIClient, model_id: str) -> None:
    """Demonstrate getting detailed model information."""
    logger.info(f"\n🔍 Getting Model Details: {model_id}")
    logger.info("=" * 50)
    
    try:
        model_details = client.get_model(model_id)
        if model_details:
            logger.info("✅ Model details retrieved:")
            
            # Display key information
            print("\n" + "=" * 60)
            print("📊 Model Information:")
            print("=" * 60)
            print(json.dumps(model_details, indent=2, ensure_ascii=False))
            print("=" * 60)
            
        else:
            logger.warning(f"⚠️ Could not retrieve details for model: {model_id}")
    
    except Exception as e:
        logger.error(f"❌ Failed to get model details: {e}")


def create_model_example(client: OpenWebUIClient, base_model_id: str) -> bool:
    """Demonstrate creating a custom model."""
    logger.info(f"\n🎨 Creating Custom Model: {TEST_MODEL_ID}")
    logger.info("=" * 55)
    
    try:
        # Check if model already exists
        existing_model = client.get_model(TEST_MODEL_ID)
        if existing_model:
            logger.warning(f"⚠️ Model {TEST_MODEL_ID} already exists - deleting first")
            client.delete_model(TEST_MODEL_ID)
            time.sleep(1)  # Brief pause
        
        # Create the model
        created_model = client.create_model(
            model_id=TEST_MODEL_ID,
            name=TEST_MODEL_NAME,
            base_model_id=base_model_id,
            description="This is a test model created to demonstrate the OpenWebUI Chat Client model management capabilities.",
            params={
                "system_prompt": "You are a helpful test assistant created via the OpenWebUI Chat Client API. You provide clear, concise, and factual responses.",
                "temperature": 0.7,
            },
            suggestion_prompts=[
                "What is OpenWebUI?",
                "How does the Chat Client work?",
                "What are your capabilities?"
            ],
            tags=["test", "api-created", "demo"],
            capabilities={"vision": False, "web_search": True}
        )
        
        if created_model:
            logger.info("✅ Model creation successful!")
            logger.info(f"   Model ID: {created_model.get('id', 'Unknown')}")
            logger.info(f"   Model Name: {created_model.get('name', 'Unknown')}")
            
            # Verify the model was created with a polling mechanism
            logger.info("Verifying model creation with polling...")
            is_verified = False
            for attempt in range(5): # Poll for up to 10 seconds
                time.sleep(2)
                logger.info(f"  ... verification attempt {attempt + 1}")
                verification = client.get_model(TEST_MODEL_ID)
                if verification:
                    logger.info("✅ Model creation verified")
                    is_verified = True
                    break

            if not is_verified:
                logger.error("❌ Model creation verification failed after multiple attempts")
            return is_verified
        else:
            logger.error("❌ Model creation failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Model creation failed: {e}")
        return False


def update_model_example(client: OpenWebUIClient) -> None:
    """Demonstrate updating an existing model."""
    logger.info(f"\n✏️ Updating Model: {TEST_MODEL_ID}")
    logger.info("=" * 45)
    
    try:
        # Update the model with new parameters
        updated_model = client.update_model(
            model_id=TEST_MODEL_ID,
            name=f"{TEST_MODEL_NAME} (Updated)",
            description="This test model has been updated via the OpenWebUI Chat Client API to demonstrate update functionality.",
            params={"temperature": 0.5},
            tags=["test", "api-updated", "demo", "modified"],
            is_active=False
        )
        
        if updated_model:
            logger.info("✅ Model update successful!")
            logger.info(f"   Updated Name: {updated_model.get('name', 'Unknown')}")
            logger.info(f"   New Temperature: {updated_model.get('params', {}).get('temperature', 'Unknown')}")
            logger.info(f"   Active Status: {updated_model.get('is_active', 'Unknown')}")
            
            # Verify the update
            verification = client.get_model(TEST_MODEL_ID)
            if verification:
                logger.info("✅ Model update verified")
                logger.info(f"   Verified Name: {verification.get('name', 'Unknown')}")
            else:
                logger.warning("⚠️ Could not verify model update")
        else:
            logger.error("❌ Model update failed")
    
    except Exception as e:
        logger.error(f"❌ Model update failed: {e}")


def delete_model_example(client: OpenWebUIClient) -> None:
    """Demonstrate deleting a model."""
    logger.info(f"\n🗑️ Deleting Model: {TEST_MODEL_ID}")
    logger.info("=" * 45)
    
    try:
        # Check if model exists before deleting
        existing_model = client.get_model(TEST_MODEL_ID)
        if not existing_model:
            logger.info("ℹ️ Model does not exist - no deletion needed")
            return
        
        # Delete the model
        deleted = client.delete_model(TEST_MODEL_ID)
        
        if deleted:
            logger.info("✅ Model deletion successful!")
            
            # Verify deletion
            time.sleep(2)  # Give the server time to process
            verification = client.get_model(TEST_MODEL_ID)
            if not verification:
                logger.info("✅ Model deletion verified")
            else:
                logger.warning("⚠️ Model still exists after deletion attempt")
        else:
            logger.error("❌ Model deletion failed")
    
    except Exception as e:
        logger.error(f"❌ Model deletion failed: {e}")


def model_validation_example(client: OpenWebUIClient) -> None:
    """Demonstrate model validation and error handling."""
    logger.info("\n🔍 Model Validation Example")
    logger.info("=" * 40)
    
    # Test cases for validation
    test_cases = [
        {
            "name": "Valid Model",
            "model_id": DEFAULT_MODEL,
            "should_exist": True
        },
        {
            "name": "Non-existent Model",
            "model_id": "non-existent-model-12345",
            "should_exist": False
        },
        {
            "name": "Empty Model ID",
            "model_id": "",
            "should_exist": False
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"🧪 Testing: {test_case['name']}")
        
        try:
            model = client.get_model(test_case["model_id"])
            
            if model and test_case["should_exist"]:
                logger.info(f"   ✅ Found model as expected: {model.get('name', 'Unknown')}")
            elif not model and not test_case["should_exist"]:
                logger.info("   ✅ Model not found as expected")
            elif model and not test_case["should_exist"]:
                logger.warning("   ⚠️ Unexpectedly found model")
            else:
                logger.warning("   ⚠️ Expected model not found")
                
        except Exception as e:
            logger.info(f"   ⚠️ Exception occurred: {e}")


def main() -> None:
    """Main function demonstrating model management operations."""
    logger.info("🚀 OpenWebUI Chat Client - Model Management Examples")
    logger.info("=" * 70)
    
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
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Run model management examples
    try:
        # List models
        list_models_example(client)
        
        # Get base models for creation example
        base_model_id = list_base_models_example(client)
        
        # Get model details
        get_model_details_example(client, DEFAULT_MODEL)
        
        # Model validation
        model_validation_example(client)
        
        # Create, update, and delete model (if base model available)
        if base_model_id:
            logger.info(f"\n🔧 Using base model '{base_model_id}' for CRUD operations")
            
            if create_model_example(client, base_model_id):
                update_model_example(client)
                delete_model_example(client)
        else:
            logger.warning("⚠️ No base models available - skipping create/update/delete examples")
        
        logger.info("\n🎉 Model management examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/model_management/model_switching.py")
        logger.info("   - Try: python examples/chat_features/parallel_chat.py")
        
    except Exception as e:
        logger.error(f"❌ Model management examples failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()