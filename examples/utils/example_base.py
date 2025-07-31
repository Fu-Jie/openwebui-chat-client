#!/usr/bin/env python3
"""
Base class and utilities for OpenWebUI Chat Client examples.

This module provides a common base class and utility functions that can be used
across all example scripts to ensure consistency and reduce code duplication.

Features provided:
- Standardized client initialization
- Environment variable validation
- Logging setup
- Error handling patterns
- Common configuration management

Usage:
    from utils.example_base import ExampleBase
    
    class MyExample(ExampleBase):
        def run_example(self):
            # Your example implementation
            pass
"""

import logging
import os
import sys
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv


class ExampleBase(ABC):
    """Base class for all OpenWebUI Chat Client examples."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the example base.
        
        Args:
            name: Name of the example
            description: Description of what the example demonstrates
        """
        self.name = name
        self.description = description
        self.logger = self._setup_logging()
        self.client: Optional[OpenWebUIClient] = None
        
        # Load environment variables
        load_dotenv()
        
        # Configuration
        self.base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
        self.auth_token = os.getenv("OUI_AUTH_TOKEN")
        self.default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
        
        # Parse parallel models
        parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
        self.parallel_models = [model.strip() for model in parallel_models_str.split(",") if model.strip()]
        
        # Other common configurations
        self.rag_model = os.getenv("OUI_RAG_MODEL", "gemini-2.5-flash")
        self.multimodal_model = os.getenv("OUI_MULTIMODAL_MODEL", self.default_model)

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the example."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        return logging.getLogger(self.name)

    def validate_environment(self) -> bool:
        """
        Validate that required environment variables are set.
        
        Returns:
            True if environment is valid, False otherwise
        """
        if not self.auth_token:
            self.logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
            self.logger.error("Please set your OpenWebUI API token:")
            self.logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
            return False
        
        self.logger.info(f"✅ Environment validated for {self.name}")
        self.logger.info(f"   Base URL: {self.base_url}")
        self.logger.info(f"   Default Model: {self.default_model}")
        return True

    def initialize_client(self) -> bool:
        """
        Initialize the OpenWebUI client.
        
        Returns:
            True if client initialized successfully, False otherwise
        """
        try:
            self.client = OpenWebUIClient(
                base_url=self.base_url,
                token=self.auth_token,
                default_model_id=self.default_model
            )
            self.logger.info("✅ OpenWebUI client initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize client: {e}")
            return False

    def run(self) -> bool:
        """
        Run the complete example with proper setup and error handling.
        
        Returns:
            True if example completed successfully, False otherwise
        """
        self.logger.info(f"🚀 Starting example: {self.name}")
        if self.description:
            self.logger.info(f"📝 Description: {self.description}")
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        # Initialize client
        if not self.initialize_client():
            return False
        
        # Run the actual example
        try:
            self.run_example()
            self.logger.info(f"🎉 Example '{self.name}' completed successfully")
            return True
        except KeyboardInterrupt:
            self.logger.info("⚠️ Example interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"❌ Example failed: {e}")
            return False
        finally:
            self.cleanup()

    @abstractmethod
    def run_example(self) -> None:
        """
        Abstract method to be implemented by specific examples.
        
        This method should contain the main logic of the example.
        """
        pass

    def cleanup(self) -> None:
        """
        Cleanup method called after example completion.
        
        Override this method in subclasses if cleanup is needed.
        """
        pass

    def print_separator(self, title: str = "", char: str = "=", width: int = 60) -> None:
        """Print a formatted separator line."""
        if title:
            title_formatted = f" {title} "
            padding = (width - len(title_formatted)) // 2
            line = char * padding + title_formatted + char * padding
            if len(line) < width:
                line += char
        else:
            line = char * width
        print(line)

    def print_section(self, title: str) -> None:
        """Print a section header."""
        self.print_separator()
        self.print_separator(title)
        self.print_separator()


class ExampleRunner:
    """Utility class for running multiple examples."""
    
    def __init__(self):
        self.examples: List[ExampleBase] = []
        
    def add_example(self, example: ExampleBase) -> None:
        """Add an example to the runner."""
        self.examples.append(example)
        
    def run_all(self) -> Dict[str, bool]:
        """
        Run all added examples.
        
        Returns:
            Dictionary mapping example names to success status
        """
        results = {}
        for example in self.examples:
            print(f"\n{'='*80}")
            print(f"Running example: {example.name}")
            print(f"{'='*80}")
            
            results[example.name] = example.run()
            
        return results
        
    def print_summary(self, results: Dict[str, bool]) -> None:
        """Print a summary of all example results."""
        print(f"\n{'='*80}")
        print("EXAMPLES SUMMARY")
        print(f"{'='*80}")
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        for name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status:<12} {name}")
            
        print(f"\n{success_count}/{total_count} examples completed successfully")


def validate_model_available(client: OpenWebUIClient, model_id: str) -> bool:
    """
    Validate that a specific model is available in the OpenWebUI instance.
    
    Args:
        client: Initialized OpenWebUI client
        model_id: Model ID to validate
        
    Returns:
        True if model is available, False otherwise
    """
    try:
        models = client.list_models()
        available_model_ids = [model.get('id', '') for model in models]
        return model_id in available_model_ids
    except Exception:
        return False


def get_available_models(client: OpenWebUIClient) -> List[str]:
    """
    Get list of available model IDs.
    
    Args:
        client: Initialized OpenWebUI client
        
    Returns:
        List of available model IDs
    """
    try:
        models = client.list_models()
        return [model.get('id', '') for model in models if model.get('id')]
    except Exception:
        return []


if __name__ == "__main__":
    # Example usage
    class TestExample(ExampleBase):
        def run_example(self):
            self.logger.info("This is a test example")
            
    example = TestExample("test_example", "A simple test example")
    example.run()