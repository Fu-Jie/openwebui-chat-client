import unittest

import responses

from openwebui_chat_client.core.base_client import BaseClient


class TestBaseClientRetry(unittest.TestCase):

    def setUp(self):
        """Set up a BaseClient instance for each test."""
        self.base_client = BaseClient(
            base_url="http://test-server.com",
            token="test_token",
            default_model_id="test-model",
        )

    @responses.activate
    def test_post_request_retries_on_server_error(self):
        """
        Test that a POST request is retried on a 503 server error and eventually succeeds.
        """
        # --- Arrange ---
        test_url = "http://test-server.com/api/test"

        # Mock a 503 Service Unavailable error for the first two calls
        responses.add(responses.POST, test_url, status=503)
        responses.add(responses.POST, test_url, status=503)

        # Mock a successful response for the third call
        responses.add(responses.POST, test_url, json={"status": "success"}, status=200)

        # --- Act ---
        # Call a method that uses session.post
        result = self.base_client._get_json_response(
            method="POST", endpoint="/api/test", json_data={"key": "value"}
        )

        # --- Assert ---
        # The request should have been made 3 times in total (1 initial + 2 retries)
        self.assertEqual(len(responses.calls), 3)

        # The final result should be the successful one
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")

    @responses.activate
    def test_get_request_no_retry_on_client_error(self):
        """
        Test that a GET request is NOT retried on a 404 client error.
        """
        # --- Arrange ---
        test_url = "http://test-server.com/api/notfound"

        # Mock a 404 Not Found error
        responses.add(responses.GET, test_url, status=404)

        # --- Act ---
        # Call a method that uses session.get.
        # This will raise an HTTPError which is caught by _make_request, returning None.
        result = self.base_client._get_json_response(
            method="GET", endpoint="/api/notfound"
        )

        # --- Assert ---
        # The request should have been made only once
        self.assertEqual(len(responses.calls), 1)

        # The result should be None as the request failed without retries
        self.assertIsNone(result)

    @responses.activate
    def test_retries_exhausted(self):
        """
        Test that after all retries are exhausted, the request fails.
        """
        # --- Arrange ---
        test_url = "http://test-server.com/api/fail"

        # Mock a 500 error for all attempts (initial + 3 retries)
        for _ in range(4):
            responses.add(responses.POST, test_url, status=500)

        # --- Act ---
        result = self.base_client._get_json_response(
            method="POST", endpoint="/api/fail", json_data={"key": "value"}
        )

        # --- Assert ---
        # The request should have been made 4 times in total (1 initial + 3 retries)
        self.assertEqual(len(responses.calls), 4)

        # The final result should be None because all attempts failed
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
