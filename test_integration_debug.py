#!/usr/bin/env python3

import os
import sys
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_integration_example():
    """Test basic_chat.py to see what errors occur."""
    
    # First test with mock environment variables 
    env = os.environ.copy()
    env.update({
        'OUI_BASE_URL': 'http://localhost:3000',
        'OUI_AUTH_TOKEN': 'mock_token',
        'OUI_DEFAULT_MODEL': 'gpt-4.1'
    })
    
    try:
        result = subprocess.run(
            [sys.executable, 'examples/getting_started/basic_chat.py'],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        logger.info(f"Return code: {result.returncode}")
        logger.info("STDOUT:")
        print(result.stdout)
        logger.info("STDERR:")
        print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧪 Testing basic_chat.py integration example...")
    success = test_integration_example()
    logger.info(f"Result: {'✅ Passed' if success else '❌ Failed'}")