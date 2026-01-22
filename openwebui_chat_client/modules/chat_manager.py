"""Chat manager (thin wrapper).

REFACTORING STATUS: Phase 2 - Base Manager Integration
- ✅ Now inherits from BaseManager
- ✅ Uses BaseManager's 20 utility methods
- 🔲 Mixins still present (will be integrated in Phase 3)
"""

from typing import TYPE_CHECKING

from openwebui_chat_client.core.base_manager import BaseManager
from openwebui_chat_client.models import ModelAccessMixin
from openwebui_chat_client.modules.chat import (
    ChatActionsMixin,
    ChatCoreMixin,
    ChatFoldersMixin,
    ChatMetadataMixin,
    ChatOperationsMixin,
    ChatPlaceholdersMixin,
    ChatQueriesMixin,
    TaskProcessingMixin,
)

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient


class ChatManager(
    BaseManager,  # ✅ NEW: Inherit from BaseManager first
    ModelAccessMixin,  # 🔲 TODO: Remove in Phase 4
    ChatCoreMixin,
    ChatOperationsMixin,
    ChatFoldersMixin,
    ChatQueriesMixin,
    ChatActionsMixin,
    ChatPlaceholdersMixin,
    ChatMetadataMixin,
    TaskProcessingMixin,
):
    """
    Chat manager with unified base architecture.
    
    Inherits from BaseManager to get:
    - Unified HTTP methods (_make_request, _get_json_response)
    - Parameter building (_build_pagination_params, _build_filter_params)
    - Response parsing (_parse_list_response)
    - Validation (_validate_required_fields, _validate_enum_value)
    - Batch operations (_batch_operation)
    - Logging (_log_operation_start/success/failure)
    - And 13 more utility methods
    """

    def __init__(self, base_client: "BaseClient"):
        """
        Initialize ChatManager with BaseManager foundation.
        
        Args:
            base_client: The BaseClient instance providing HTTP connectivity
        """
        # Initialize BaseManager (provides 20 utility methods)
        super().__init__(base_client)
        
        # Keep backward compatibility attribute
        self.base_client = base_client
