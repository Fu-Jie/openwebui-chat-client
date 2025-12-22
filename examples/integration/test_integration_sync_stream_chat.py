"""
Env-gated sync streaming integration test for OpenWebUIClient.
Requires OUI_BASE_URL and OUI_AUTH_TOKEN to be set.
"""

import os
import time
import uuid
import unittest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from openwebui_chat_client import OpenWebUIClient

ENV_READY = bool(os.getenv("OUI_BASE_URL") and os.getenv("OUI_AUTH_TOKEN"))


@unittest.skipUnless(
    ENV_READY,
    "Integration env not set (OUI_BASE_URL, OUI_AUTH_TOKEN).",
)
class TestSyncStreamChatIntegration(unittest.TestCase):
    def setUp(self):
        base_url = os.getenv("OUI_BASE_URL")
        token = os.getenv("OUI_AUTH_TOKEN")
        default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

        # Quick reachability check to avoid hard failures when server is down
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            server_reachable = response.ok
        except requests.exceptions.RequestException:
            server_reachable = False

        if not server_reachable:
            self.skipTest(
                f"OpenWebUI server at {base_url} is not reachable. Skipping integration tests."
            )

        self.client = OpenWebUIClient(
            base_url=base_url,
            token=token,
            default_model_id=default_model,
        )

    def test_stream_chat_live(self):
        chat_title = f"sync-stream-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        chunks = []
        try:
            for chunk in self.client.stream_chat(
                question="streaming ping",
                chat_title=chat_title,
                enable_follow_up=False,
                cleanup_placeholder_messages=True,
                wait_before_request=0.0,
            ):
                if chunk:
                    chunks.append(chunk)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                self.skipTest(
                    f"Live stream_chat failed with {e.response.status_code}: {e}"
                )
            raise e
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Live stream_chat failed: {e}")

        full = "".join(chunks)
        self.assertTrue(full, "Streamed response should not be empty")
        self.assertGreaterEqual(len(chunks), 1, "Should stream at least one chunk")


if __name__ == "__main__":
    unittest.main()
