from typing import Any, Dict, List, Optional, Generator
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Local imports - strictly one-way
from .api import ChatAPI
from .payloads import ChatPayloads

logger = logging.getLogger(__name__)


class ChatParallel:
    """
    Parallel Chat Execution Module.

    Handles multi-model broadcasting logic.
    Delegates actual API calls to ChatAPI.
    """

    def __init__(self, chat_api: ChatAPI):
        self.api = chat_api

    def run_parallel(
        self, chat_id: str, user_message: Dict[str, Any], model_ids: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """Run completion on multiple models in parallel."""

        results = []
        with ThreadPoolExecutor(max_workers=len(model_ids)) as executor:
            future_to_model = {}

            for model_id in model_ids:
                # Build isolated payload for each model
                payload = ChatPayloads.build_completion_payload(
                    model=model_id,
                    chat_id=chat_id,
                    user_message=user_message,
                    stream=False,
                    **kwargs,
                )

                future = executor.submit(self.api.completion, payload)
                future_to_model[future] = model_id

            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    response = future.result()
                    if response:
                        results.append(
                            {
                                "model": model_id,
                                "response": response,
                                "id": response.get("id"),
                            }
                        )
                except Exception as e:
                    logger.error(f"Parallel model {model_id} failed: {e}")

        return results
