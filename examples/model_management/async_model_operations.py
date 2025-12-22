#!/usr/bin/env python3
"""
Async model operations example for OpenWebUI Chat Client.

This example demonstrates asynchronous model management operations including
listing, querying, and managing models using AsyncOpenWebUIClient.

Features demonstrated:
- Async model listing with concurrent queries
- Async model details retrieval
- Batch model operations with asyncio.gather
- Model filtering and categorization
- Error handling for model operations

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN

Usage:
    python examples/model_management/async_model_operations.py
"""

import asyncio
import logging
import os
import sys
from typing import Optional, List, Dict, Any
from collections import defaultdict

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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def list_models_example(client: AsyncOpenWebUIClient) -> Optional[List[Dict[str, Any]]]:
    """Demonstrate async model listing."""
    logger.info("📋 Async List Models Example")
    logger.info("=" * 40)
    
    models = await client.list_models()
    
    if models:
        logger.info(f"✅ Found {len(models)} models")
        
        # Show first 10 models with details
        print("\n📦 Available Models (first 10):")
        print("-" * 60)
        
        for i, model in enumerate(models[:10]):
            model_id = model.get('id', 'Unknown')
            model_name = model.get('name', model_id)
            owned_by = model.get('owned_by', 'unknown')
            
            # Truncate long names
            display_name = model_name[:40] + "..." if len(model_name) > 40 else model_name
            print(f"  {i+1:2}. {display_name:<45} [{owned_by}]")
        
        if len(models) > 10:
            print(f"  ... and {len(models) - 10} more models")
        
        print()
        return models
    else:
        logger.error("❌ Failed to list models")
        return None


async def categorize_models_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate model categorization by owner/type."""
    logger.info("\n📊 Model Categorization Example")
    logger.info("=" * 40)
    
    models = await client.list_models()
    
    if not models:
        logger.error("❌ Failed to get models for categorization")
        return False
    
    # Group models by owner
    by_owner: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for model in models:
        owner = model.get('owned_by', 'unknown')
        by_owner[owner].append(model)
    
    print("\n📈 Models by Owner/Provider:")
    print("-" * 40)
    
    # Sort by count descending
    sorted_owners = sorted(by_owner.items(), key=lambda x: len(x[1]), reverse=True)
    
    for owner, owner_models in sorted_owners[:8]:  # Top 8 providers
        count = len(owner_models)
        bar = "█" * min(count, 20)
        print(f"  {owner:<20} {bar} ({count})")
    
    if len(sorted_owners) > 8:
        remaining = sum(len(m) for _, m in sorted_owners[8:])
        print(f"  {'[others]':<20} ... ({remaining})")
    
    print()
    logger.info(f"✅ Categorized {len(models)} models into {len(by_owner)} categories")
    return True


async def concurrent_model_details_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate concurrent model detail fetching."""
    logger.info("\n⚡ Concurrent Model Details Example")
    logger.info("=" * 40)
    
    # First, get the model list
    models = await client.list_models()
    if not models or len(models) < 3:
        logger.warning("⚠️ Not enough models to demonstrate concurrent fetching")
        return True
    
    # Select a few models to fetch details concurrently
    sample_models = models[:5]
    model_ids = [m.get('id') for m in sample_models if m.get('id')]
    
    logger.info(f"📤 Fetching details for {len(model_ids)} models concurrently...")
    
    async def fetch_model_details(model_id: str) -> tuple:
        """Fetch details for a single model."""
        try:
            details = await client.get_model(model_id)
            return (model_id, details, None)
        except Exception as e:
            return (model_id, None, str(e))
    
    # Fetch all details concurrently
    tasks = [fetch_model_details(mid) for mid in model_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = 0
    print("\n📋 Model Details:")
    print("-" * 60)
    
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"   ❌ Unexpected error: {result}")
        else:
            model_id, details, error = result
            short_id = model_id[:30] + "..." if len(model_id) > 30 else model_id
            
            if error:
                print(f"   ⚠️ {short_id}: {error}")
            elif details:
                name = details.get('name', 'N/A')[:25]
                model_type = details.get('owned_by', 'unknown')
                print(f"   ✅ {short_id}: {name} [{model_type}]")
                success_count += 1
            else:
                print(f"   ⚠️ {short_id}: No details available")
    
    print()
    logger.info(f"🎯 Successfully fetched {success_count}/{len(model_ids)} model details")
    return success_count > 0


async def model_search_example(client: AsyncOpenWebUIClient) -> bool:
    """Demonstrate model searching and filtering."""
    logger.info("\n🔍 Model Search Example")
    logger.info("=" * 40)
    
    models = await client.list_models()
    if not models:
        logger.error("❌ Failed to get models")
        return False
    
    # Search for models containing specific keywords
    search_terms = ["gpt", "claude", "llama", "gemini", "deepseek"]
    
    print("\n🔎 Search Results:")
    print("-" * 50)
    
    for term in search_terms:
        matching = [
            m for m in models 
            if term.lower() in m.get('id', '').lower() 
            or term.lower() in m.get('name', '').lower()
        ]
        
        if matching:
            examples = [m.get('name', m.get('id', 'Unknown'))[:25] for m in matching[:3]]
            examples_str = ", ".join(examples)
            if len(matching) > 3:
                examples_str += f", +{len(matching) - 3} more"
            print(f"   '{term}': {len(matching)} models - {examples_str}")
        else:
            print(f"   '{term}': 0 models")
    
    print()
    logger.info("✅ Model search completed")
    return True


async def model_statistics_example(client: AsyncOpenWebUIClient) -> bool:
    """Calculate and display model statistics."""
    logger.info("\n📊 Model Statistics Example")
    logger.info("=" * 40)
    
    models = await client.list_models()
    if not models:
        logger.error("❌ Failed to get models")
        return False
    
    # Calculate statistics
    total_count = len(models)
    
    # Count by different criteria
    by_owner = defaultdict(int)
    with_description = 0
    
    for model in models:
        owner = model.get('owned_by', 'unknown')
        by_owner[owner] += 1
        
        if model.get('description'):
            with_description += 1
    
    print("\n📈 Model Statistics:")
    print("-" * 40)
    print(f"   Total models: {total_count}")
    print(f"   Unique providers: {len(by_owner)}")
    print(f"   With descriptions: {with_description} ({with_description*100//total_count}%)")
    
    # Top providers
    top_providers = sorted(by_owner.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n   Top Providers:")
    for provider, count in top_providers:
        percentage = count * 100 // total_count
        print(f"      {provider}: {count} ({percentage}%)")
    
    print()
    logger.info("✅ Statistics calculated successfully")
    return True


async def main() -> None:
    """Main async function demonstrating model operations."""
    logger.info("🚀 AsyncOpenWebUIClient - Model Operations Examples")
    logger.info("=" * 60)
    
    # Validation
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.error("Please set your OpenWebUI API token:")
        logger.error("  export OUI_AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Use async context manager for clean resource handling
    async with AsyncOpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL) as client:
        logger.info("✅ Client initialized with context manager")
        
        # Run model operation examples
        examples = [
            ("list_models", list_models_example),
            ("categorize_models", categorize_models_example),
            ("concurrent_model_details", concurrent_model_details_example),
            ("model_search", model_search_example),
            ("model_statistics", model_statistics_example),
        ]
        
        success_count = 0
        for example_name, example_func in examples:
            try:
                result = await example_func(client)
                if result is not None and result is not False:
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
        logger.info(f"\n🎉 Model operation examples completed: {success_count}/{total_examples}")
        
        if success_count < total_examples // 2:
            logger.error("❌ Too many examples failed")
            sys.exit(1)
    
    logger.info("🔌 Client automatically closed by context manager")


if __name__ == "__main__":
    asyncio.run(main())
