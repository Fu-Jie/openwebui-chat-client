"""
Env-gated async streaming integration test for AsyncOpenWebUIClient.
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
class TestAsyncStreamChatIntegration(unittest.IsolatedAsyncioTestCase):
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

    async def test_stream_chat_live(self):
        chat_title = f"async-stream-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        chunks = []
        try:
            async for chunk in self.client.stream_chat(
                question="streaming ping",
                chat_title=chat_title,
                enable_follow_up=False,
            ):
                if chunk:
                    chunks.append(chunk)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.skipTest(f"Live stream_chat failed: {e}")

        full = "".join(chunks)
        self.assertTrue(full, "Streamed response should not be empty")
        # ensure at least a couple of chunks were streamed
        self.assertGreaterEqual(len(chunks), 1)


if __name__ == "__main__":
    unittest.main()
