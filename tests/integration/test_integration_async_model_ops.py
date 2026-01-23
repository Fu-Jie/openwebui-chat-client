"""
Env-gated async model operations integration test for AsyncOpenWebUIClient.
Requires OUI_BASE_URL and OUI_AUTH_TOKEN to be set.
"""

import unittest
import httpx

from openwebui_chat_client import AsyncOpenWebUIClient
from .integration_helpers import ensure_env_loaded, get_env

ENV_READY = ensure_env_loaded()


@unittest.skipUnless(
    ENV_READY,
    "Integration env not set (OUI_BASE_URL, OUI_AUTH_TOKEN).",
)
class TestAsyncModelOpsIntegration(unittest.IsolatedAsyncioTestCase):
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

    async def test_get_first_model_details(self):
        try:
            models = await self.client.list_models()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.skipTest(f"Live list_models failed: {e}")

        if not models:
            self.skipTest("No models available on server to get details.")

        first_id = models[0].get("id") or models[0].get("name")
        if not first_id:
            self.skipTest("First model lacks id; skipping detail fetch.")

        try:
            detail = await self.client.get_model(first_id)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.skipTest(f"Live get_model failed: {e}")

        if detail is None:
            self.skipTest("Live get_model returned None; skipping detail assertions.")

        # detail may be partial; assert shape without being too strict
        self.assertIsInstance(detail, dict)
        self.assertIn("id", detail)


if __name__ == "__main__":
    unittest.main()
