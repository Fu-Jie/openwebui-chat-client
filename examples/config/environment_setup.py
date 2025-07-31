#!/usr/bin/env python3
"""
Environment setup guide for OpenWebUI Chat Client examples.

This module provides guidance and utilities for setting up the environment
variables required to run OpenWebUI Chat Client examples.

Features demonstrated:
- Environment variable validation
- Configuration setup guidance
- Connection testing

Requirements:
- OpenWebUI server running and accessible
- Valid API token for authentication

Usage:
    python examples/config/environment_setup.py
"""

import logging
import os
import sys
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv

# Add the parent directory to path to import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from openwebui_chat_client import OpenWebUIClient

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnvironmentSetup:
    """Helper class for environment setup and validation."""
    
    def __init__(self):
        """Initialize the environment setup validator."""
        self.required_vars = {
            "OUI_BASE_URL": {
                "description": "OpenWebUI server URL",
                "default": "http://localhost:3000",
                "example": "https://your-openwebui-instance.com"
            },
            "OUI_AUTH_TOKEN": {
                "description": "OpenWebUI API authentication token",
                "default": None,
                "example": "your_api_token_here"
            }
        }
        
        self.optional_vars = {
            "OUI_DEFAULT_MODEL": {
                "description": "Default model ID for chat operations",
                "default": "gpt-4.1",
                "example": "gpt-4.1"
            },
            "OUI_PARALLEL_MODELS": {
                "description": "Comma-separated model IDs for parallel chat examples",
                "default": "gpt-4.1,gemini-2.5-flash",
                "example": "gpt-4.1,claude-3,gemini-2.5-flash"
            },
            "OUI_RAG_MODEL": {
                "description": "Model ID optimized for RAG operations",
                "default": "gemini-2.5-flash",
                "example": "gemini-2.5-flash"
            },
            "OUI_MULTIMODAL_MODEL": {
                "description": "Model ID that supports images and multimodal input",
                "default": "gpt-4.1",
                "example": "gpt-4-vision-preview"
            }
        }
    
    def check_environment(self) -> Dict[str, Any]:
        """
        Check the current environment configuration.
        
        Returns:
            Dictionary with environment status information
        """
        status = {
            "required_missing": [],
            "required_present": [],
            "optional_present": [],
            "optional_missing": [],
            "warnings": [],
            "valid": True
        }
        
        # Check required variables
        for var_name, var_info in self.required_vars.items():
            value = os.getenv(var_name)
            if value:
                status["required_present"].append(var_name)
            else:
                status["required_missing"].append(var_name)
                status["valid"] = False
        
        # Check optional variables
        for var_name, var_info in self.optional_vars.items():
            value = os.getenv(var_name)
            if value:
                status["optional_present"].append(var_name)
            else:
                status["optional_missing"].append(var_name)
        
        return status
    
    def print_status(self) -> None:
        """Print the current environment status."""
        status = self.check_environment()
        
        print("🔍 Environment Variable Status")
        print("=" * 50)
        
        # Required variables
        print("\n📋 Required Variables:")
        for var_name in status["required_present"]:
            value = os.getenv(var_name)
            # Mask sensitive values
            display_value = value if var_name != "OUI_AUTH_TOKEN" else f"{value[:8]}..." if value else None
            print(f"  ✅ {var_name}: {display_value}")
        
        for var_name in status["required_missing"]:
            var_info = self.required_vars[var_name]
            print(f"  ❌ {var_name}: NOT SET")
            print(f"     Description: {var_info['description']}")
            if var_info['default']:
                print(f"     Default: {var_info['default']}")
            print(f"     Example: {var_info['example']}")
        
        # Optional variables
        print("\n🔧 Optional Variables:")
        for var_name in status["optional_present"]:
            value = os.getenv(var_name)
            print(f"  ✅ {var_name}: {value}")
        
        for var_name in status["optional_missing"]:
            var_info = self.optional_vars[var_name]
            print(f"  ⚪ {var_name}: Using default ({var_info['default']})")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  Required variables: {len(status['required_present'])}/{len(self.required_vars)} set")
        print(f"  Optional variables: {len(status['optional_present'])}/{len(self.optional_vars)} set")
        
        if status["valid"]:
            print(f"  Status: ✅ Ready to run examples")
        else:
            print(f"  Status: ❌ Missing required variables")
    
    def print_setup_instructions(self) -> None:
        """Print setup instructions for different operating systems."""
        print("\n🛠️ Setup Instructions")
        print("=" * 50)
        
        print("\n🐧 Linux / macOS (Bash/Zsh):")
        print("Add these lines to your ~/.bashrc or ~/.zshrc:")
        for var_name, var_info in {**self.required_vars, **self.optional_vars}.items():
            if var_info["default"]:
                print(f'export {var_name}="{var_info["example"]}"')
            else:
                print(f'export {var_name}="{var_info["example"]}"  # Required!')
        
        print("\n🪟 Windows (Command Prompt):")
        for var_name, var_info in {**self.required_vars, **self.optional_vars}.items():
            print(f'set {var_name}="{var_info["example"]}"')
        
        print("\n🪟 Windows (PowerShell):")
        for var_name, var_info in {**self.required_vars, **self.optional_vars}.items():
            print(f'$env:{var_name}="{var_info["example"]}"')
        
        print("\n📄 .env File (recommended):")
        print("Create a .env file in your project root:")
        for var_name, var_info in {**self.required_vars, **self.optional_vars}.items():
            comment = "  # Required!" if not var_info["default"] else ""
            print(f'{var_name}="{var_info["example"]}"{comment}')
    
    def test_connection(self) -> bool:
        """
        Test connection to OpenWebUI server.
        
        Returns:
            True if connection successful, False otherwise
        """
        base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
        auth_token = os.getenv("OUI_AUTH_TOKEN")
        
        if not auth_token:
            logger.error("❌ Cannot test connection: OUI_AUTH_TOKEN not set")
            return False
        
        try:
            logger.info(f"🔗 Testing connection to {base_url}...")
            client = OpenWebUIClient(base_url, auth_token)
            
            # Try to list models as a basic connectivity test
            models = client.list_models()
            if models is not None:
                logger.info(f"✅ Connection successful! Found {len(models)} models")
                
                # Show available models
                if models:
                    logger.info("📋 Available models:")
                    for model in models[:5]:  # Show first 5 models
                        model_name = model.get('name', 'Unknown')
                        model_id = model.get('id', 'Unknown')
                        logger.info(f"  - {model_name} ({model_id})")
                    if len(models) > 5:
                        logger.info(f"  ... and {len(models) - 5} more models")
                else:
                    logger.warning("⚠️ No models found in the OpenWebUI instance")
                
                return True
            else:
                logger.error("❌ Connection failed: Unable to retrieve models")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def validate_models(self) -> bool:
        """
        Validate that configured models are available.
        
        Returns:
            True if all configured models are available, False otherwise
        """
        auth_token = os.getenv("OUI_AUTH_TOKEN")
        if not auth_token:
            logger.error("❌ Cannot validate models: OUI_AUTH_TOKEN not set")
            return False
        
        try:
            base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
            client = OpenWebUIClient(base_url, auth_token)
            models = client.list_models()
            
            if not models:
                logger.error("❌ Cannot validate models: No models available")
                return False
            
            available_model_ids = [model.get('id', '') for model in models]
            
            # Check configured models
            models_to_check = {
                "OUI_DEFAULT_MODEL": os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1"),
                "OUI_RAG_MODEL": os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash"),
                "OUI_MULTIMODAL_MODEL": os.getenv("OUI_MULTIMODAL_MODEL", "gpt-4.1"),
            }
            
            # Check parallel models
            parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
            parallel_models = [model.strip() for model in parallel_models_str.split(",") if model.strip()]
            for i, model_id in enumerate(parallel_models):
                models_to_check[f"OUI_PARALLEL_MODELS[{i}]"] = model_id
            
            all_valid = True
            logger.info("🔍 Validating configured models...")
            
            for config_name, model_id in models_to_check.items():
                if model_id in available_model_ids:
                    logger.info(f"  ✅ {config_name}: {model_id}")
                else:
                    logger.warning(f"  ❌ {config_name}: {model_id} (NOT AVAILABLE)")
                    all_valid = False
            
            if all_valid:
                logger.info("✅ All configured models are available")
            else:
                logger.warning("⚠️ Some configured models are not available")
                logger.info("💡 Available models:")
                for model_id in available_model_ids[:10]:  # Show first 10
                    logger.info(f"     - {model_id}")
                if len(available_model_ids) > 10:
                    logger.info(f"     ... and {len(available_model_ids) - 10} more")
            
            return all_valid
            
        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
            return False


def main() -> None:
    """Main function to run environment setup and validation."""
    print("🚀 OpenWebUI Chat Client - Environment Setup")
    print("=" * 60)
    
    setup = EnvironmentSetup()
    
    # Check current environment status
    setup.print_status()
    
    # Check if we can proceed with connection test
    status = setup.check_environment()
    
    if not status["valid"]:
        print("\n⚠️ Required environment variables are missing!")
        setup.print_setup_instructions()
        return
    
    # Test connection
    print("\n🔗 Testing Connection")
    print("=" * 30)
    
    if setup.test_connection():
        # Validate models if connection successful
        print("\n🎯 Validating Models")
        print("=" * 25)
        setup.validate_models()
        
        print("\n🎉 Environment setup complete!")
        print("You can now run the examples:")
        print("  python examples/getting_started/hello_world.py")
        print("  python examples/getting_started/basic_chat.py")
    else:
        print("\n❌ Connection test failed!")
        print("Please check your OpenWebUI server and token configuration.")


if __name__ == "__main__":
    main()