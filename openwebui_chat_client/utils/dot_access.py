"""Deprecated dot-access module.

All dot-access behavior has moved to openwebui_chat_client.models.
This module only re-exports model-based helpers.
"""

from openwebui_chat_client.models import ModelAccessMixin, to_model, wrap_result

__all__ = ["ModelAccessMixin", "to_model", "wrap_result"]
