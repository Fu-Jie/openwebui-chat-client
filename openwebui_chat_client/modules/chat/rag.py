from typing import Any, Dict, List, Optional
import os
import base64
import mimetypes


class ChatRAG:
    """
    RAG & File Handling Module.

    Handles file encoding, upload preparation, and RAG context injection.
    Dependencies should be injected via method args to maintain loose coupling.
    """

    @staticmethod
    def encode_image(image_path: str) -> Optional[str]:
        """Encode local image to base64 data URL."""
        if not os.path.exists(image_path):
            return None

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith("image/"):
            return None

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"

    @staticmethod
    def build_rag_payload(
        file_ids: Optional[List[str]] = None, collection_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build RAG-specific payload wrapper."""
        payload = {}
        if file_ids:
            # Construct file referencing structure
            payload["files"] = [{"id": fid, "type": "file"} for fid in file_ids]
        if collection_ids:
            payload["collections"] = collection_ids
        return payload

    @staticmethod
    def inject_context(
        messages: List[Dict[str, Any]], rag_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Inject RAG context into message history (if needed logic exists)."""
        # Logic to append context to last user message if required
        return messages
