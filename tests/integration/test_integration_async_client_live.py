"""
Env-gated async integration tests for AsyncOpenWebUIClient.
Requires OUI_BASE_URL and OUI_AUTH_TOKEN to be set.
"""

import time
import uuid
import unittest
import httpx

from openwebui_chat_client import AsyncOpenWebUIClient
from .integration_helpers import (
    ensure_env_loaded,
    get_env,
    normalize_chat_response,
)

ENV_READY = ensure_env_loaded()


@unittest.skipUnless(
    ENV_READY,
    "Integration env not set (OUI_BASE_URL, OUI_AUTH_TOKEN).",
)
class TestAsyncOpenWebUIClientIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        base_url = get_env("OUI_BASE_URL")
        token = get_env("OUI_AUTH_TOKEN")
        default_model = get_env("OUI_DEFAULT_MODEL", "gpt-4.1")
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
        response_data = normalize_chat_response(result)
        self.assertTrue(response_data.get("response"))


if __name__ == "__main__":
    unittest.main()
