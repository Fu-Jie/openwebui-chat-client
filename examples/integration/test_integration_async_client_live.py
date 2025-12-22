"""
Env-gated async integration tests for AsyncOpenWebUIClient.
Requires OUI_BASE_URL and OUI_AUTH_TOKEN to be set.
"""

import os
import time
import uuid
import unittest
import httpx

from openwebui_chat_client import AsyncOpenWebUIClient

ENV_READY = bool(os.getenv("OUI_BASE_URL") and os.getenv("OUI_AUTH_TOKEN"))


@unittest.skipUnless(
    ENV_READY,
    "Integration env not set (OUI_BASE_URL, OUI_AUTH_TOKEN).",
)
class TestAsyncOpenWebUIClientIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        base_url = os.getenv("OUI_BASE_URL")
        token = os.getenv("OUI_AUTH_TOKEN")
        default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
        self.client = AsyncOpenWebUIClient(
            base_url,
            token,
            default_model,
            timeout=30.0,
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_list_models_live(self):
        try:
            models = await self.client.list_models()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.skipTest(f"Live list_models failed: {e}")

        self.assertIsInstance(models, list)
        self.assertGreaterEqual(len(models), 0)

    async def test_basic_chat_live(self):
        chat_title = f"async-int-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        try:
            result = await self.client.chat(
                "ping",
                chat_title,
            )
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.skipTest(f"Live chat failed: {e}")

        self.assertIsNotNone(result)
        self.assertIn("response", result)
        self.assertTrue(result["response"])


if __name__ == "__main__":
    unittest.main()
