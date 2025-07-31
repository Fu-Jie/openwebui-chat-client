#!/usr/bin/env python3
"""
Basic client configuration example for OpenWebUI Chat Client.

This example demonstrates how to configure and initialize the OpenWebUI Chat Client
with different options and settings.

Features demonstrated:
- Basic client initialization
- Configuration options
- Client validation
- Error handling for configuration

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/config/basic_config.py
"""

import logging
import os
import sys
from typing import Optional, Dict, Any

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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def basic_configuration_example() -> None:
    """Demonstrate basic client configuration."""
    logger.info("📋 Basic Client Configuration Example")
    logger.info("=" * 50)
    
    # Basic initialization
    try:
        client = OpenWebUIClient(
            base_url=BASE_URL,
            token=AUTH_TOKEN,
            default_model_id=DEFAULT_MODEL
        )
        logger.info("✅ Client initialized with basic configuration")
        logger.info(f"   Base URL: {BASE_URL}")
        logger.info(f"   Default Model: {DEFAULT_MODEL}")
        
        # Test basic functionality
        models = client.list_models()
        if models:
            logger.info(f"✅ Successfully connected - {len(models)} models available")
        else:
            logger.warning("⚠️ Connected but no models found")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")


def advanced_configuration_example() -> None:
    """Demonstrate advanced client configuration options."""
    logger.info("\n🔧 Advanced Configuration Options")
    logger.info("=" * 50)
    
    # Show different ways to configure the client
    configurations = [
        {
            "name": "Development Configuration",
            "base_url": "http://localhost:3000",
            "timeout": 30,
            "description": "Local development setup with short timeout"
        },
        {
            "name": "Production Configuration", 
            "base_url": "https://openwebui.company.com",
            "timeout": 60,
            "description": "Production setup with longer timeout"
        },
        {
            "name": "High-Performance Configuration",
            "base_url": BASE_URL,
            "timeout": 120,
            "description": "Configuration optimized for long-running operations"
        }
    ]
    
    for config in configurations:
        logger.info(f"\n📝 {config['name']}:")
        logger.info(f"   Description: {config['description']}")
        logger.info(f"   Base URL: {config['base_url']}")
        logger.info(f"   Timeout: {config['timeout']} seconds")
        
        # Note: We don't actually create clients for all configs since
        # we only have one valid token/URL combo
        if config["base_url"] == BASE_URL:
            try:
                # Example of how you might configure with custom settings
                # Note: The actual OpenWebUIClient might not support all these parameters
                # This is just to show the pattern
                client = OpenWebUIClient(
                    base_url=config["base_url"],
                    token=AUTH_TOKEN,
                    default_model_id=DEFAULT_MODEL
                )
                logger.info(f"   ✅ Successfully initialized")
            except Exception as e:
                logger.info(f"   ❌ Failed to initialize: {e}")
        else:
            logger.info(f"   ⏭️ Skipped (different base URL)")


def configuration_validation_example() -> None:
    """Demonstrate configuration validation."""
    logger.info("\n🔍 Configuration Validation")
    logger.info("=" * 40)
    
    # Test different configuration scenarios
    test_cases = [
        {
            "name": "Valid Configuration",
            "base_url": BASE_URL,
            "token": AUTH_TOKEN,
            "model": DEFAULT_MODEL,
            "should_succeed": True
        },
        {
            "name": "Missing Token",
            "base_url": BASE_URL,
            "token": None,
            "model": DEFAULT_MODEL,
            "should_succeed": False
        },
        {
            "name": "Invalid URL",
            "base_url": "http://invalid-url:9999",
            "token": AUTH_TOKEN,
            "model": DEFAULT_MODEL,
            "should_succeed": False
        },
        {
            "name": "Empty Model ID",
            "base_url": BASE_URL,
            "token": AUTH_TOKEN,
            "model": "",
            "should_succeed": True  # Should work, might use server default
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n🧪 Testing: {test_case['name']}")
        
        if not test_case["token"]:
            logger.info("   ❌ Skipped - No token provided")
            continue
            
        try:
            client = OpenWebUIClient(
                base_url=test_case["base_url"],
                token=test_case["token"],
                default_model_id=test_case["model"]
            )
            
            # Quick validation by trying to list models
            models = client.list_models()
            
            if test_case["should_succeed"]:
                logger.info("   ✅ Succeeded as expected")
                if models:
                    logger.info(f"      Found {len(models)} models")
            else:
                logger.info("   ⚠️ Succeeded but failure was expected")
                
        except Exception as e:
            if test_case["should_succeed"]:
                logger.info(f"   ❌ Failed unexpectedly: {e}")
            else:
                logger.info(f"   ✅ Failed as expected: {e}")


def environment_variables_example() -> None:
    """Demonstrate environment variable usage."""
    logger.info("\n🌍 Environment Variables Configuration")
    logger.info("=" * 50)
    
    # Show current environment variable configuration
    env_vars = {
        "OUI_BASE_URL": os.getenv("OUI_BASE_URL"),
        "OUI_AUTH_TOKEN": os.getenv("OUI_AUTH_TOKEN"),
        "OUI_DEFAULT_MODEL": os.getenv("OUI_DEFAULT_MODEL"),
        "OUI_PARALLEL_MODELS": os.getenv("OUI_PARALLEL_MODELS"),
        "OUI_RAG_MODEL": os.getenv("OUI_RAG_MODEL"),
        "OUI_MULTIMODAL_MODEL": os.getenv("OUI_MULTIMODAL_MODEL"),
    }
    
    logger.info("📋 Current environment variables:")
    for var_name, var_value in env_vars.items():
        if var_value:
            # Mask sensitive information
            if "TOKEN" in var_name and var_value:
                display_value = f"{var_value[:8]}..." if len(var_value) > 8 else "***"
            else:
                display_value = var_value
            logger.info(f"   ✅ {var_name}: {display_value}")
        else:
            logger.info(f"   ❌ {var_name}: Not set")
    
    # Show how to use environment variables with fallbacks
    logger.info("\n🔄 Using environment variables with fallbacks:")
    
    config = {
        "base_url": os.getenv("OUI_BASE_URL", "http://localhost:3000"),
        "token": os.getenv("OUI_AUTH_TOKEN", "your_token_here"),
        "default_model": os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1"),
        "rag_model": os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash"),
    }
    
    for key, value in config.items():
        logger.info(f"   {key}: {value}")


def client_info_example() -> None:
    """Demonstrate getting client and server information."""
    logger.info("\n📊 Client and Server Information")
    logger.info("=" * 45)
    
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        
        # Get basic information
        logger.info("🔗 Connection Information:")
        logger.info(f"   Server URL: {BASE_URL}")
        logger.info(f"   Default Model: {DEFAULT_MODEL}")
        
        # List available models
        models = client.list_models()
        if models:
            logger.info(f"\n📋 Available Models ({len(models)} total):")
            for i, model in enumerate(models[:5]):  # Show first 5
                model_name = model.get('name', 'Unknown')
                model_id = model.get('id', 'Unknown')
                logger.info(f"   {i+1}. {model_name} ({model_id})")
            
            if len(models) > 5:
                logger.info(f"   ... and {len(models) - 5} more models")
        
        # Try to get specific model info
        try:
            model_info = client.get_model(DEFAULT_MODEL)
            if model_info:
                logger.info(f"\n🎯 Default Model Information:")
                logger.info(f"   Name: {model_info.get('name', 'Unknown')}")
                logger.info(f"   ID: {model_info.get('id', 'Unknown')}")
                # Add other relevant model information here
            else:
                logger.warning(f"⚠️ Could not get information for model: {DEFAULT_MODEL}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to get model info: {e}")
            
    except Exception as e:
        logger.error(f"❌ Failed to get client information: {e}")


def main() -> None:
    """Main function demonstrating client configuration."""
    logger.info("🚀 OpenWebUI Chat Client - Basic Configuration Examples")
    logger.info("=" * 70)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        return
    
    # Run configuration examples
    try:
        basic_configuration_example()
        advanced_configuration_example()
        configuration_validation_example()
        environment_variables_example()
        client_info_example()
        
        logger.info("\n🎉 Configuration examples completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   - Try: python examples/getting_started/hello_world.py")
        logger.info("   - Try: python examples/getting_started/basic_chat.py")
        
    except Exception as e:
        logger.error(f"❌ Configuration examples failed: {e}")


if __name__ == "__main__":
    main()