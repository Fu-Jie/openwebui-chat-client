#!/usr/bin/env python3

import logging
import os
import sys

# Add the client to path
sys.path.insert(0, os.path.abspath('.'))

from openwebui_chat_client import OpenWebUIClient

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_basic_initialization():
    """Test basic client initialization without real connection."""
    try:
        # Create client with dummy values
        client = OpenWebUIClient("http://localhost:3000", "dummy_token", "gpt-4.1", skip_model_refresh=True)
        logger.info("✅ Client created successfully")
        
        # Test if basic methods exist
        assert hasattr(client, 'chat'), "Missing chat method"
        assert hasattr(client, '_upload_file'), "Missing _upload_file method"
        assert hasattr(client, 'get_knowledge_base_by_name'), "Missing get_knowledge_base_by_name method"
        assert hasattr(client, '_get_knowledge_base_details'), "Missing _get_knowledge_base_details method"
        
        logger.info("✅ All required methods exist")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_initialization()
    if success:
        logger.info("🎉 Basic initialization test passed")
    else:
        logger.error("❌ Basic initialization test failed")
        sys.exit(1)