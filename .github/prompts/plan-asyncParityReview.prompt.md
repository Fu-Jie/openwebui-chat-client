Plan: align async chat logic with sync implementation

1) AsyncChatManager.chat: add RAG, images, tools handling; ensure payload mirrors sync (api_rag_payload, parent_message, tool_ids) and local history persistence; call _update_remote_chat.
2) AsyncChatManager.stream_chat: support tags, folder assignment, auto-tagging/auto-titling, wait_before_request; ensure final persistence after stream; reuse sync logging and safeguards.
3) Shared helpers: ensure _handle_rag_references/_encode_image_to_base64 used in chat path; check placeholder pool creation uses full chat object when updating remote.
4) Async client surface: confirm async_openwebui_client passes through new kwargs to managers; keep delete_all_chats parity.
5) Tests: add/extend async tests to cover chat, stream_chat payloads (parent_message, files/tools), and delete_all_chats; update mappings if needed.
6) Validation: run targeted unit tests for async chat/stream; optional integration async categories once implemented.
