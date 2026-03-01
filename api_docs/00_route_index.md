# OpenWebUI API Route Index

## Summary

- **Total Routes:** 394
- **Module Count:** 27

## analytics

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| analytics | GET | `/api/v1/analytics/models` | `get_model_analytics` | YES | Get message counts per model. |
| analytics | GET | `/api/v1/analytics/users` | `get_user_analytics` | YES | Get message counts and token usage per user with user info. |
| analytics | GET | `/api/v1/analytics/messages` | `get_messages` | YES | Query messages with filters. |
| analytics | GET | `/api/v1/analytics/summary` | `get_summary` | YES | Get summary statistics for the dashboard. |
| analytics | GET | `/api/v1/analytics/daily` | `get_daily_stats` | YES | Get message counts grouped by model for time-series chart. |
| analytics | GET | `/api/v1/analytics/tokens` | `get_token_usage` | YES | Get token usage aggregated by model. |
| analytics | GET | `/api/v1/analytics/models/{model_id}/chats` | `get_model_chats` | YES | Get chats that used a specific model, with preview and feedback info. |
| analytics | GET | `/api/v1/analytics/models/{model_id}/overview` | `get_model_overview` | YES | Get model overview with feedback history and chat tags. |

## audio

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| audio | GET | `/api/v1/audio/config` | `get_audio_config` | YES |  |
| audio | POST | `/api/v1/audio/config/update` | `update_audio_config` | YES |  |
| audio | POST | `/api/v1/audio/speech` | `speech` | YES |  |
| audio | POST | `/api/v1/audio/transcriptions` | `transcription` | YES |  |
| audio | GET | `/api/v1/audio/models` | `get_models` | YES |  |
| audio | GET | `/api/v1/audio/voices` | `get_voices` | YES |  |

## auths

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| auths | GET | `/api/v1/auths/` | `get_session_user` | YES |  |
| auths | POST | `/api/v1/auths/update/profile` | `update_profile` | YES |  |
| auths | POST | `/api/v1/auths/update/timezone` | `update_timezone` | YES |  |
| auths | POST | `/api/v1/auths/update/password` | `update_password` | YES |  |
| auths | POST | `/api/v1/auths/ldap` | `ldap_auth` | YES |  |
| auths | POST | `/api/v1/auths/signin` | `signin` | YES |  |
| auths | POST | `/api/v1/auths/signup` | `signup` | YES |  |
| auths | GET | `/api/v1/auths/signout` | `signout` | YES |  |
| auths | POST | `/api/v1/auths/add` | `add_user` | YES |  |
| auths | GET | `/api/v1/auths/admin/details` | `get_admin_details` | YES |  |
| auths | GET | `/api/v1/auths/admin/config` | `get_admin_config` | YES |  |
| auths | POST | `/api/v1/auths/admin/config` | `update_admin_config` | YES |  |
| auths | GET | `/api/v1/auths/admin/config/ldap/server` | `get_ldap_server` | YES |  |
| auths | POST | `/api/v1/auths/admin/config/ldap/server` | `update_ldap_server` | YES |  |
| auths | GET | `/api/v1/auths/admin/config/ldap` | `get_ldap_config` | YES |  |
| auths | POST | `/api/v1/auths/admin/config/ldap` | `update_ldap_config` | YES |  |
| auths | POST | `/api/v1/auths/api_key` | `generate_api_key` | YES |  |
| auths | DELETE | `/api/v1/auths/api_key` | `delete_api_key` | YES |  |
| auths | GET | `/api/v1/auths/api_key` | `get_api_key` | YES |  |
| auths | POST | `/api/v1/auths/oauth/{provider}/token/exchange` | `token_exchange` | YES | Exchange an external OAuth provider token for an OpenWebUI JWT. |

## channels

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| channels | GET | `/api/v1/channels/` | `get_channels` | YES |  |
| channels | GET | `/api/v1/channels/list` | `get_all_channels` | YES |  |
| channels | GET | `/api/v1/channels/users/{user_id}` | `get_dm_channel_by_user_id` | YES |  |
| channels | POST | `/api/v1/channels/create` | `create_new_channel` | YES |  |
| channels | GET | `/api/v1/channels/{id}` | `get_channel_by_id` | YES |  |
| channels | GET | `/api/v1/channels/{id}/members` | `get_channel_members_by_id` | YES |  |
| channels | POST | `/api/v1/channels/{id}/members/active` | `update_is_active_member_by_id_and_user_id` | YES |  |
| channels | POST | `/api/v1/channels/{id}/update/members/add` | `add_members_by_id` | YES |  |
| channels | POST | `/api/v1/channels/{id}/update/members/remove` | `remove_members_by_id` | YES |  |
| channels | POST | `/api/v1/channels/{id}/update` | `update_channel_by_id` | YES |  |
| channels | DELETE | `/api/v1/channels/{id}/delete` | `delete_channel_by_id` | YES |  |
| channels | GET | `/api/v1/channels/{id}/messages` | `get_channel_messages` | YES |  |
| channels | GET | `/api/v1/channels/{id}/messages/pinned` | `get_pinned_channel_messages` | YES |  |
| channels | POST | `/api/v1/channels/{id}/messages/post` | `post_new_message` | YES |  |
| channels | GET | `/api/v1/channels/{id}/messages/{message_id}` | `get_channel_message` | YES |  |
| channels | GET | `/api/v1/channels/{id}/messages/{message_id}/data` | `get_channel_message_data` | YES |  |
| channels | POST | `/api/v1/channels/{id}/messages/{message_id}/pin` | `pin_channel_message` | YES |  |
| channels | GET | `/api/v1/channels/{id}/messages/{message_id}/thread` | `get_channel_thread_messages` | YES |  |
| channels | POST | `/api/v1/channels/{id}/messages/{message_id}/update` | `update_message_by_id` | YES |  |
| channels | POST | `/api/v1/channels/{id}/messages/{message_id}/reactions/add` | `add_reaction_to_message` | YES |  |
| channels | POST | `/api/v1/channels/{id}/messages/{message_id}/reactions/remove` | `remove_reaction_by_id_and_user_id_and_name` | YES |  |
| channels | DELETE | `/api/v1/channels/{id}/messages/{message_id}/delete` | `delete_message_by_id` | YES |  |
| channels | GET | `/api/v1/channels/webhooks/{webhook_id}/profile/image` | `get_webhook_profile_image` | YES | Get webhook profile image by webhook ID. |
| channels | GET | `/api/v1/channels/{id}/webhooks` | `get_channel_webhooks` | YES |  |
| channels | POST | `/api/v1/channels/{id}/webhooks/create` | `create_channel_webhook` | YES |  |
| channels | POST | `/api/v1/channels/{id}/webhooks/{webhook_id}/update` | `update_channel_webhook` | YES |  |
| channels | DELETE | `/api/v1/channels/{id}/webhooks/{webhook_id}/delete` | `delete_channel_webhook` | YES |  |
| channels | POST | `/api/v1/channels/webhooks/{webhook_id}/{token}` | `post_webhook_message` | YES | Public endpoint to post messages via webhook |

## chats

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| chats | GET | `/api/v1/chats/` | `get_session_user_chat_list` | YES |  |
| chats | GET | `/api/v1/chats/list` | `get_session_user_chat_list` | YES |  |
| chats | GET | `/api/v1/chats/stats/usage` | `get_session_user_chat_usage_stats` | YES |  |
| chats | GET | `/api/v1/chats/stats/export` | `export_chat_stats` | YES |  |
| chats | GET | `/api/v1/chats/stats/export/{chat_id}` | `export_single_chat_stats` | YES | Export stats for exactly one chat by ID. |
| chats | DELETE | `/api/v1/chats/` | `delete_all_user_chats` | YES |  |
| chats | GET | `/api/v1/chats/list/user/{user_id}` | `get_user_chat_list_by_user_id` | YES |  |
| chats | POST | `/api/v1/chats/new` | `create_new_chat` | YES |  |
| chats | POST | `/api/v1/chats/import` | `import_chats` | YES |  |
| chats | GET | `/api/v1/chats/search` | `search_user_chats` | YES |  |
| chats | GET | `/api/v1/chats/folder/{folder_id}` | `get_chats_by_folder_id` | YES |  |
| chats | GET | `/api/v1/chats/folder/{folder_id}/list` | `get_chat_list_by_folder_id` | YES |  |
| chats | GET | `/api/v1/chats/pinned` | `get_user_pinned_chats` | YES |  |
| chats | GET | `/api/v1/chats/all` | `get_user_chats` | YES |  |
| chats | GET | `/api/v1/chats/all/archived` | `get_user_archived_chats` | YES |  |
| chats | GET | `/api/v1/chats/all/tags` | `get_all_user_tags` | YES |  |
| chats | GET | `/api/v1/chats/all/db` | `get_all_user_chats_in_db` | YES |  |
| chats | GET | `/api/v1/chats/archived` | `get_archived_session_user_chat_list` | YES |  |
| chats | POST | `/api/v1/chats/archive/all` | `archive_all_chats` | YES |  |
| chats | POST | `/api/v1/chats/unarchive/all` | `unarchive_all_chats` | YES |  |
| chats | GET | `/api/v1/chats/shared` | `get_shared_session_user_chat_list` | YES |  |
| chats | GET | `/api/v1/chats/share/{share_id}` | `get_shared_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/tags` | `get_user_chat_list_by_tag_name` | YES |  |
| chats | GET | `/api/v1/chats/{id}` | `get_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}` | `update_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/messages/{message_id}` | `update_chat_message_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/messages/{message_id}/event` | `send_chat_message_event_by_id` | YES |  |
| chats | DELETE | `/api/v1/chats/{id}` | `delete_chat_by_id` | YES |  |
| chats | GET | `/api/v1/chats/{id}/pinned` | `get_pinned_status_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/pin` | `pin_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/clone` | `clone_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/clone/shared` | `clone_shared_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/archive` | `archive_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/share` | `share_chat_by_id` | YES |  |
| chats | DELETE | `/api/v1/chats/{id}/share` | `delete_shared_chat_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/folder` | `update_chat_folder_id_by_id` | YES |  |
| chats | GET | `/api/v1/chats/{id}/tags` | `get_chat_tags_by_id` | YES |  |
| chats | POST | `/api/v1/chats/{id}/tags` | `add_tag_by_id_and_tag_name` | YES |  |
| chats | DELETE | `/api/v1/chats/{id}/tags` | `delete_tag_by_id_and_tag_name` | YES |  |
| chats | DELETE | `/api/v1/chats/{id}/tags/all` | `delete_all_tags_by_id` | YES |  |

## configs

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| configs | POST | `/api/v1/configs/import` | `import_config` | YES |  |
| configs | GET | `/api/v1/configs/export` | `export_config` | YES |  |
| configs | GET | `/api/v1/configs/connections` | `get_connections_config` | YES |  |
| configs | POST | `/api/v1/configs/connections` | `set_connections_config` | YES |  |
| configs | POST | `/api/v1/configs/oauth/clients/register` | `register_oauth_client` | YES |  |
| configs | GET | `/api/v1/configs/tool_servers` | `get_tool_servers_config` | YES |  |
| configs | POST | `/api/v1/configs/tool_servers` | `set_tool_servers_config` | YES |  |
| configs | POST | `/api/v1/configs/tool_servers/verify` | `verify_tool_servers_config` | YES | Verify the connection to the tool server. |
| configs | GET | `/api/v1/configs/code_execution` | `get_code_execution_config` | YES |  |
| configs | POST | `/api/v1/configs/code_execution` | `set_code_execution_config` | YES |  |
| configs | GET | `/api/v1/configs/models` | `get_models_config` | YES |  |
| configs | POST | `/api/v1/configs/models` | `set_models_config` | YES |  |
| configs | POST | `/api/v1/configs/suggestions` | `set_default_suggestions` | YES |  |
| configs | POST | `/api/v1/configs/banners` | `set_banners` | YES |  |
| configs | GET | `/api/v1/configs/banners` | `get_banners` | YES |  |

## evaluations

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| evaluations | GET | `/api/v1/evaluations/leaderboard` | `get_leaderboard` | YES | Get model leaderboard with Elo ratings |
| evaluations | GET | `/api/v1/evaluations/leaderboard/{model_id}/history` | `get_model_history` | YES | Get daily win/loss history for a specific model. |
| evaluations | GET | `/api/v1/evaluations/config` | `get_config` | YES |  |
| evaluations | POST | `/api/v1/evaluations/config` | `update_config` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedbacks/all` | `get_all_feedbacks` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedbacks/all/ids` | `get_all_feedback_ids` | YES |  |
| evaluations | DELETE | `/api/v1/evaluations/feedbacks/all` | `delete_all_feedbacks` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedbacks/all/export` | `export_all_feedbacks` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedbacks/user` | `get_feedbacks` | YES |  |
| evaluations | DELETE | `/api/v1/evaluations/feedbacks` | `delete_feedbacks` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedbacks/list` | `get_feedbacks` | YES |  |
| evaluations | POST | `/api/v1/evaluations/feedback` | `create_feedback` | YES |  |
| evaluations | GET | `/api/v1/evaluations/feedback/{id}` | `get_feedback_by_id` | YES |  |
| evaluations | POST | `/api/v1/evaluations/feedback/{id}` | `update_feedback_by_id` | YES |  |
| evaluations | DELETE | `/api/v1/evaluations/feedback/{id}` | `delete_feedback_by_id` | YES |  |

## files

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| files | POST | `/api/v1/files/` | `upload_file` | YES |  |
| files | GET | `/api/v1/files/` | `list_files` | YES |  |
| files | GET | `/api/v1/files/search` | `search_files` | YES | Search for files by filename with support for wildcard patterns. |
| files | DELETE | `/api/v1/files/all` | `delete_all_files` | YES |  |
| files | GET | `/api/v1/files/{id}` | `get_file_by_id` | YES |  |
| files | GET | `/api/v1/files/{id}/process/status` | `get_file_process_status` | YES |  |
| files | GET | `/api/v1/files/{id}/data/content` | `get_file_data_content_by_id` | YES |  |
| files | POST | `/api/v1/files/{id}/data/content/update` | `update_file_data_content_by_id` | YES |  |
| files | GET | `/api/v1/files/{id}/content` | `get_file_content_by_id` | YES |  |
| files | GET | `/api/v1/files/{id}/content/html` | `get_html_file_content_by_id` | YES |  |
| files | GET | `/api/v1/files/{id}/content/{file_name}` | `get_file_content_by_id` | YES |  |
| files | DELETE | `/api/v1/files/{id}` | `delete_file_by_id` | YES |  |

## folders

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| folders | GET | `/api/v1/folders/` | `get_folders` | YES |  |
| folders | POST | `/api/v1/folders/` | `create_folder` | YES |  |
| folders | GET | `/api/v1/folders/{id}` | `get_folder_by_id` | YES |  |
| folders | POST | `/api/v1/folders/{id}/update` | `update_folder_name_by_id` | YES |  |
| folders | POST | `/api/v1/folders/{id}/update/parent` | `update_folder_parent_id_by_id` | YES |  |
| folders | POST | `/api/v1/folders/{id}/update/expanded` | `update_folder_is_expanded_by_id` | YES |  |
| folders | DELETE | `/api/v1/folders/{id}` | `delete_folder_by_id` | YES |  |

## functions

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| functions | GET | `/api/v1/functions/` | `get_functions` | YES |  |
| functions | GET | `/api/v1/functions/list` | `get_function_list` | YES |  |
| functions | GET | `/api/v1/functions/export` | `get_functions` | YES |  |
| functions | POST | `/api/v1/functions/load/url` | `load_function_from_url` | YES |  |
| functions | POST | `/api/v1/functions/sync` | `sync_functions` | YES |  |
| functions | POST | `/api/v1/functions/create` | `create_new_function` | YES |  |
| functions | GET | `/api/v1/functions/id/{id}` | `get_function_by_id` | YES |  |
| functions | POST | `/api/v1/functions/id/{id}/toggle` | `toggle_function_by_id` | YES |  |
| functions | POST | `/api/v1/functions/id/{id}/toggle/global` | `toggle_global_by_id` | YES |  |
| functions | POST | `/api/v1/functions/id/{id}/update` | `update_function_by_id` | YES |  |
| functions | DELETE | `/api/v1/functions/id/{id}/delete` | `delete_function_by_id` | YES |  |
| functions | GET | `/api/v1/functions/id/{id}/valves` | `get_function_valves_by_id` | YES |  |
| functions | GET | `/api/v1/functions/id/{id}/valves/spec` | `get_function_valves_spec_by_id` | YES |  |
| functions | POST | `/api/v1/functions/id/{id}/valves/update` | `update_function_valves_by_id` | YES |  |
| functions | GET | `/api/v1/functions/id/{id}/valves/user` | `get_function_user_valves_by_id` | YES |  |
| functions | GET | `/api/v1/functions/id/{id}/valves/user/spec` | `get_function_user_valves_spec_by_id` | YES |  |
| functions | POST | `/api/v1/functions/id/{id}/valves/user/update` | `update_function_user_valves_by_id` | YES |  |

## groups

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| groups | GET | `/api/v1/groups/` | `get_groups` | YES |  |
| groups | POST | `/api/v1/groups/create` | `create_new_group` | YES |  |
| groups | GET | `/api/v1/groups/id/{id}` | `get_group_by_id` | YES |  |
| groups | GET | `/api/v1/groups/id/{id}/info` | `get_group_info_by_id` | YES |  |
| groups | GET | `/api/v1/groups/id/{id}/export` | `export_group_by_id` | YES |  |
| groups | POST | `/api/v1/groups/id/{id}/users` | `get_users_in_group` | YES |  |
| groups | POST | `/api/v1/groups/id/{id}/update` | `update_group_by_id` | YES |  |
| groups | POST | `/api/v1/groups/id/{id}/users/add` | `add_user_to_group` | YES |  |
| groups | POST | `/api/v1/groups/id/{id}/users/remove` | `remove_users_from_group` | YES |  |
| groups | DELETE | `/api/v1/groups/id/{id}/delete` | `delete_group_by_id` | YES |  |

## images

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| images | GET | `/api/v1/images/config` | `get_config` | YES |  |
| images | POST | `/api/v1/images/config/update` | `update_config` | YES |  |
| images | GET | `/api/v1/images/config/url/verify` | `verify_url` | YES |  |
| images | GET | `/api/v1/images/models` | `get_models` | YES |  |
| images | POST | `/api/v1/images/generations` | `generate_images` | YES |  |
| images | POST | `/api/v1/images/edit` | `image_edits` | YES |  |

## knowledge

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| knowledge | GET | `/api/v1/knowledge/` | `get_knowledge_bases` | YES |  |
| knowledge | GET | `/api/v1/knowledge/search` | `search_knowledge_bases` | YES |  |
| knowledge | GET | `/api/v1/knowledge/search/files` | `search_knowledge_files` | YES |  |
| knowledge | POST | `/api/v1/knowledge/create` | `create_new_knowledge` | YES |  |
| knowledge | POST | `/api/v1/knowledge/reindex` | `reindex_knowledge_files` | YES |  |
| knowledge | POST | `/api/v1/knowledge/metadata/reindex` | `reindex_knowledge_base_metadata_embeddings` | YES | Batch embed all existing knowledge bases |
| knowledge | GET | `/api/v1/knowledge/{id}` | `get_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/update` | `update_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/access/update` | `update_knowledge_access_by_id` | YES |  |
| knowledge | GET | `/api/v1/knowledge/{id}/files` | `get_knowledge_files_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/file/add` | `add_file_to_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/file/update` | `update_file_from_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/file/remove` | `remove_file_from_knowledge_by_id` | YES |  |
| knowledge | DELETE | `/api/v1/knowledge/{id}/delete` | `delete_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/reset` | `reset_knowledge_by_id` | YES |  |
| knowledge | POST | `/api/v1/knowledge/{id}/files/batch/add` | `add_files_to_knowledge_batch` | YES | Add multiple files to a knowledge base |
| knowledge | GET | `/api/v1/knowledge/{id}/export` | `export_knowledge_by_id` | YES | Export a knowledge base as a zip file containing .txt files. |

## memories

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| memories | GET | `/api/v1/memories/` | `get_memories` | YES |  |
| memories | POST | `/api/v1/memories/add` | `add_memory` | YES |  |
| memories | POST | `/api/v1/memories/query` | `query_memory` | YES |  |
| memories | POST | `/api/v1/memories/reset` | `reset_memory_from_vector_db` | YES | Reset user's memory vector embeddings. |
| memories | DELETE | `/api/v1/memories/delete/user` | `delete_memory_by_user_id` | YES |  |
| memories | POST | `/api/v1/memories/{memory_id}/update` | `update_memory_by_id` | YES |  |
| memories | DELETE | `/api/v1/memories/{memory_id}` | `delete_memory_by_id` | YES |  |

## models

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| models | GET | `/api/v1/models/list` | `get_models` | YES |  |
| models | GET | `/api/v1/models/base` | `get_base_models` | YES |  |
| models | GET | `/api/v1/models/tags` | `get_model_tags` | YES |  |
| models | POST | `/api/v1/models/create` | `create_new_model` | YES |  |
| models | GET | `/api/v1/models/export` | `export_models` | YES |  |
| models | POST | `/api/v1/models/import` | `import_models` | YES |  |
| models | POST | `/api/v1/models/sync` | `sync_models` | YES |  |
| models | GET | `/api/v1/models/model` | `get_model_by_id` | YES |  |
| models | GET | `/api/v1/models/model/profile/image` | `get_model_profile_image` | YES |  |
| models | POST | `/api/v1/models/model/toggle` | `toggle_model_by_id` | YES |  |
| models | POST | `/api/v1/models/model/update` | `update_model_by_id` | YES |  |
| models | POST | `/api/v1/models/model/access/update` | `update_model_access_by_id` | YES |  |
| models | POST | `/api/v1/models/model/delete` | `delete_model_by_id` | YES |  |
| models | DELETE | `/api/v1/models/delete/all` | `delete_all_models` | YES |  |

## notes

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| notes | GET | `/api/v1/notes/` | `get_notes` | YES |  |
| notes | GET | `/api/v1/notes/search` | `search_notes` | YES |  |
| notes | POST | `/api/v1/notes/create` | `create_new_note` | YES |  |
| notes | GET | `/api/v1/notes/{id}` | `get_note_by_id` | YES |  |
| notes | POST | `/api/v1/notes/{id}/update` | `update_note_by_id` | YES |  |
| notes | POST | `/api/v1/notes/{id}/access/update` | `update_note_access_by_id` | YES |  |
| notes | DELETE | `/api/v1/notes/{id}/delete` | `delete_note_by_id` | YES |  |

## ollama

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| ollama | GET | `/ollama/` | `get_status` | NO |  |
| ollama | POST | `/ollama/verify` | `verify_connection` | YES |  |
| ollama | GET | `/ollama/config` | `get_config` | YES |  |
| ollama | POST | `/ollama/config/update` | `update_config` | YES |  |
| ollama | GET | `/ollama/api/tags` | `get_ollama_tags` | YES |  |
| ollama | GET | `/ollama/api/tags/{url_idx}` | `get_ollama_tags` | YES |  |
| ollama | GET | `/ollama/api/ps` | `get_ollama_loaded_models` | YES | List models that are currently loaded into Ollama memory, and which node they are loaded on. |
| ollama | GET | `/ollama/api/version` | `get_ollama_versions` | NO |  |
| ollama | GET | `/ollama/api/version/{url_idx}` | `get_ollama_versions` | NO |  |
| ollama | POST | `/ollama/api/unload` | `unload_model` | YES |  |
| ollama | POST | `/ollama/api/pull` | `pull_model` | YES |  |
| ollama | POST | `/ollama/api/pull/{url_idx}` | `pull_model` | YES |  |
| ollama | DELETE | `/ollama/api/push` | `push_model` | YES |  |
| ollama | DELETE | `/ollama/api/push/{url_idx}` | `push_model` | YES |  |
| ollama | POST | `/ollama/api/create` | `create_model` | YES |  |
| ollama | POST | `/ollama/api/create/{url_idx}` | `create_model` | YES |  |
| ollama | POST | `/ollama/api/copy` | `copy_model` | YES |  |
| ollama | POST | `/ollama/api/copy/{url_idx}` | `copy_model` | YES |  |
| ollama | DELETE | `/ollama/api/delete` | `delete_model` | YES |  |
| ollama | DELETE | `/ollama/api/delete/{url_idx}` | `delete_model` | YES |  |
| ollama | POST | `/ollama/api/show` | `show_model_info` | YES |  |
| ollama | POST | `/ollama/api/embed` | `embed` | YES |  |
| ollama | POST | `/ollama/api/embed/{url_idx}` | `embed` | YES |  |
| ollama | POST | `/ollama/api/embeddings` | `embeddings` | YES |  |
| ollama | POST | `/ollama/api/embeddings/{url_idx}` | `embeddings` | YES |  |
| ollama | POST | `/ollama/api/generate` | `generate_completion` | YES |  |
| ollama | POST | `/ollama/api/generate/{url_idx}` | `generate_completion` | YES |  |
| ollama | POST | `/ollama/api/chat` | `generate_chat_completion` | YES |  |
| ollama | POST | `/ollama/api/chat/{url_idx}` | `generate_chat_completion` | YES |  |
| ollama | POST | `/ollama/v1/completions` | `generate_openai_completion` | YES |  |
| ollama | POST | `/ollama/v1/completions/{url_idx}` | `generate_openai_completion` | YES |  |
| ollama | POST | `/ollama/v1/chat/completions` | `generate_openai_chat_completion` | YES |  |
| ollama | POST | `/ollama/v1/chat/completions/{url_idx}` | `generate_openai_chat_completion` | YES |  |
| ollama | GET | `/ollama/v1/models` | `get_openai_models` | YES |  |
| ollama | GET | `/ollama/v1/models/{url_idx}` | `get_openai_models` | YES |  |
| ollama | POST | `/ollama/models/download` | `download_model` | YES |  |
| ollama | POST | `/ollama/models/download/{url_idx}` | `download_model` | YES |  |
| ollama | POST | `/ollama/models/upload` | `upload_model` | YES |  |
| ollama | POST | `/ollama/models/upload/{url_idx}` | `upload_model` | YES |  |

## openai

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| openai | GET | `/openai/config` | `get_config` | YES |  |
| openai | POST | `/openai/config/update` | `update_config` | YES |  |
| openai | POST | `/openai/audio/speech` | `speech` | YES |  |
| openai | GET | `/openai/models` | `get_models` | YES |  |
| openai | GET | `/openai/models/{url_idx}` | `get_models` | YES |  |
| openai | POST | `/openai/verify` | `verify_connection` | YES |  |
| openai | POST | `/openai/chat/completions` | `generate_chat_completion` | YES |  |
| openai | POST | `/openai/responses` | `responses` | YES | Forward requests to the OpenAI Responses API endpoint. |

## pipelines

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| pipelines | GET | `/api/v1/pipelines/list` | `get_pipelines_list` | YES |  |
| pipelines | POST | `/api/v1/pipelines/upload` | `upload_pipeline` | YES |  |
| pipelines | POST | `/api/v1/pipelines/add` | `add_pipeline` | YES |  |
| pipelines | DELETE | `/api/v1/pipelines/delete` | `delete_pipeline` | YES |  |
| pipelines | GET | `/api/v1/pipelines/` | `get_pipelines` | YES |  |
| pipelines | GET | `/api/v1/pipelines/{pipeline_id}/valves` | `get_pipeline_valves` | YES |  |
| pipelines | GET | `/api/v1/pipelines/{pipeline_id}/valves/spec` | `get_pipeline_valves_spec` | YES |  |
| pipelines | POST | `/api/v1/pipelines/{pipeline_id}/valves/update` | `update_pipeline_valves` | YES |  |

## prompts

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| prompts | GET | `/api/v1/prompts/` | `get_prompts` | YES |  |
| prompts | GET | `/api/v1/prompts/tags` | `get_prompt_tags` | YES |  |
| prompts | GET | `/api/v1/prompts/list` | `get_prompt_list` | YES |  |
| prompts | POST | `/api/v1/prompts/create` | `create_new_prompt` | YES |  |
| prompts | GET | `/api/v1/prompts/command/{command}` | `get_prompt_by_command` | YES |  |
| prompts | GET | `/api/v1/prompts/id/{prompt_id}` | `get_prompt_by_id` | YES |  |
| prompts | POST | `/api/v1/prompts/id/{prompt_id}/update` | `update_prompt_by_id` | YES |  |
| prompts | POST | `/api/v1/prompts/id/{prompt_id}/update/meta` | `update_prompt_metadata` | YES | Update prompt name and command only (no history created). |
| prompts | POST | `/api/v1/prompts/id/{prompt_id}/update/version` | `set_prompt_version` | YES |  |
| prompts | POST | `/api/v1/prompts/id/{prompt_id}/access/update` | `update_prompt_access_by_id` | YES |  |
| prompts | POST | `/api/v1/prompts/id/{prompt_id}/toggle` | `toggle_prompt_active` | YES |  |
| prompts | DELETE | `/api/v1/prompts/id/{prompt_id}/delete` | `delete_prompt_by_id` | YES |  |
| prompts | GET | `/api/v1/prompts/id/{prompt_id}/history` | `get_prompt_history` | YES | Get version history for a prompt. |
| prompts | GET | `/api/v1/prompts/id/{prompt_id}/history/{history_id}` | `get_prompt_history_entry` | YES | Get a specific version from history. |
| prompts | DELETE | `/api/v1/prompts/id/{prompt_id}/history/{history_id}` | `delete_prompt_history_entry` | YES | Delete a history entry |
| prompts | GET | `/api/v1/prompts/id/{prompt_id}/history/diff` | `get_prompt_diff` | YES | Get diff between two versions. |

## retrieval

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| retrieval | GET | `/api/v1/retrieval/` | `get_status` | NO |  |
| retrieval | GET | `/api/v1/retrieval/embedding` | `get_embedding_config` | YES |  |
| retrieval | POST | `/api/v1/retrieval/embedding/update` | `update_embedding_config` | YES |  |
| retrieval | GET | `/api/v1/retrieval/config` | `get_rag_config` | YES |  |
| retrieval | POST | `/api/v1/retrieval/config/update` | `update_rag_config` | YES |  |
| retrieval | POST | `/api/v1/retrieval/process/file` | `process_file` | YES | Process a file and save its content to the vector database. |
| retrieval | POST | `/api/v1/retrieval/process/text` | `process_text` | YES |  |
| retrieval | POST | `/api/v1/retrieval/process/youtube` | `process_web` | YES |  |
| retrieval | POST | `/api/v1/retrieval/process/web` | `process_web` | YES |  |
| retrieval | POST | `/api/v1/retrieval/process/web/search` | `process_web_search` | YES |  |
| retrieval | POST | `/api/v1/retrieval/query/doc` | `query_doc_handler` | YES |  |
| retrieval | POST | `/api/v1/retrieval/query/collection` | `query_collection_handler` | YES |  |
| retrieval | POST | `/api/v1/retrieval/delete` | `delete_entries_from_collection` | YES |  |
| retrieval | POST | `/api/v1/retrieval/reset/db` | `reset_vector_db` | YES |  |
| retrieval | POST | `/api/v1/retrieval/reset/uploads` | `reset_upload_dir` | YES |  |
| retrieval | GET | `/api/v1/retrieval/ef/{text}` | `get_embeddings` | NO |  |
| retrieval | POST | `/api/v1/retrieval/process/files/batch` | `process_files_batch` | YES | Process a batch of files and save them to the vector database. |

## scim

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| scim | GET | `/api/v1/scim/v2/ServiceProviderConfig` | `get_service_provider_config` | NO | Get SCIM Service Provider Configuration |
| scim | GET | `/api/v1/scim/v2/ResourceTypes` | `get_resource_types` | NO | Get SCIM Resource Types |
| scim | GET | `/api/v1/scim/v2/Schemas` | `get_schemas` | NO | Get SCIM Schemas |
| scim | GET | `/api/v1/scim/v2/Users` | `get_users` | YES | List SCIM Users |
| scim | GET | `/api/v1/scim/v2/Users/{user_id}` | `get_user` | YES | Get SCIM User by ID |
| scim | POST | `/api/v1/scim/v2/Users` | `create_user` | YES | Create SCIM User |
| scim | PUT | `/api/v1/scim/v2/Users/{user_id}` | `update_user` | YES | Update SCIM User (full update) |
| scim | PATCH | `/api/v1/scim/v2/Users/{user_id}` | `patch_user` | YES | Update SCIM User (partial update) |
| scim | DELETE | `/api/v1/scim/v2/Users/{user_id}` | `delete_user` | YES | Delete SCIM User |
| scim | GET | `/api/v1/scim/v2/Groups` | `get_groups` | YES | List SCIM Groups |
| scim | GET | `/api/v1/scim/v2/Groups/{group_id}` | `get_group` | YES | Get SCIM Group by ID |
| scim | POST | `/api/v1/scim/v2/Groups` | `create_group` | YES | Create SCIM Group |
| scim | PUT | `/api/v1/scim/v2/Groups/{group_id}` | `update_group` | YES | Update SCIM Group (full update) |
| scim | PATCH | `/api/v1/scim/v2/Groups/{group_id}` | `patch_group` | YES | Update SCIM Group (partial update) |
| scim | DELETE | `/api/v1/scim/v2/Groups/{group_id}` | `delete_group` | YES | Delete SCIM Group |

## skills

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| skills | GET | `/api/v1/skills/` | `get_skills` | YES |  |
| skills | GET | `/api/v1/skills/list` | `get_skill_list` | YES |  |
| skills | GET | `/api/v1/skills/export` | `export_skills` | YES |  |
| skills | POST | `/api/v1/skills/create` | `create_new_skill` | YES |  |
| skills | GET | `/api/v1/skills/id/{id}` | `get_skill_by_id` | YES |  |
| skills | POST | `/api/v1/skills/id/{id}/update` | `update_skill_by_id` | YES |  |
| skills | POST | `/api/v1/skills/id/{id}/access/update` | `update_skill_access_by_id` | YES |  |
| skills | POST | `/api/v1/skills/id/{id}/toggle` | `toggle_skill_by_id` | YES |  |
| skills | DELETE | `/api/v1/skills/id/{id}/delete` | `delete_skill_by_id` | YES |  |

## tasks

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| tasks | POST | `/api/v1/tasks/active/chats` | `check_active_chats` | YES | Check which chat IDs have active tasks. |
| tasks | GET | `/api/v1/tasks/config` | `get_task_config` | YES |  |
| tasks | POST | `/api/v1/tasks/config/update` | `update_task_config` | YES |  |
| tasks | POST | `/api/v1/tasks/title/completions` | `generate_title` | YES |  |
| tasks | POST | `/api/v1/tasks/follow_up/completions` | `generate_follow_ups` | YES |  |
| tasks | POST | `/api/v1/tasks/tags/completions` | `generate_chat_tags` | YES |  |
| tasks | POST | `/api/v1/tasks/image_prompt/completions` | `generate_image_prompt` | YES |  |
| tasks | POST | `/api/v1/tasks/queries/completions` | `generate_queries` | YES |  |
| tasks | POST | `/api/v1/tasks/auto/completions` | `generate_autocompletion` | YES |  |
| tasks | POST | `/api/v1/tasks/emoji/completions` | `generate_emoji` | YES |  |
| tasks | POST | `/api/v1/tasks/moa/completions` | `generate_moa_response` | YES |  |

## tools

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| tools | GET | `/api/v1/tools/` | `get_tools` | YES |  |
| tools | GET | `/api/v1/tools/list` | `get_tool_list` | YES |  |
| tools | POST | `/api/v1/tools/load/url` | `load_tool_from_url` | YES |  |
| tools | GET | `/api/v1/tools/export` | `export_tools` | YES |  |
| tools | POST | `/api/v1/tools/create` | `create_new_tools` | YES |  |
| tools | GET | `/api/v1/tools/id/{id}` | `get_tools_by_id` | YES |  |
| tools | POST | `/api/v1/tools/id/{id}/update` | `update_tools_by_id` | YES |  |
| tools | POST | `/api/v1/tools/id/{id}/access/update` | `update_tool_access_by_id` | YES |  |
| tools | DELETE | `/api/v1/tools/id/{id}/delete` | `delete_tools_by_id` | YES |  |
| tools | GET | `/api/v1/tools/id/{id}/valves` | `get_tools_valves_by_id` | YES |  |
| tools | GET | `/api/v1/tools/id/{id}/valves/spec` | `get_tools_valves_spec_by_id` | YES |  |
| tools | POST | `/api/v1/tools/id/{id}/valves/update` | `update_tools_valves_by_id` | YES |  |
| tools | GET | `/api/v1/tools/id/{id}/valves/user` | `get_tools_user_valves_by_id` | YES |  |
| tools | GET | `/api/v1/tools/id/{id}/valves/user/spec` | `get_tools_user_valves_spec_by_id` | YES |  |
| tools | POST | `/api/v1/tools/id/{id}/valves/user/update` | `update_tools_user_valves_by_id` | YES |  |

## users

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| users | GET | `/api/v1/users/` | `get_users` | YES |  |
| users | GET | `/api/v1/users/all` | `get_all_users` | YES |  |
| users | GET | `/api/v1/users/search` | `search_users` | YES |  |
| users | GET | `/api/v1/users/groups` | `get_user_groups` | YES |  |
| users | GET | `/api/v1/users/permissions` | `get_user_permissisions` | YES |  |
| users | GET | `/api/v1/users/default/permissions` | `get_default_user_permissions` | YES |  |
| users | POST | `/api/v1/users/default/permissions` | `update_default_user_permissions` | YES |  |
| users | GET | `/api/v1/users/user/settings` | `get_user_settings_by_session_user` | YES |  |
| users | POST | `/api/v1/users/user/settings/update` | `update_user_settings_by_session_user` | YES |  |
| users | GET | `/api/v1/users/user/status` | `get_user_status_by_session_user` | YES |  |
| users | POST | `/api/v1/users/user/status/update` | `update_user_status_by_session_user` | YES |  |
| users | GET | `/api/v1/users/user/info` | `get_user_info_by_session_user` | YES |  |
| users | POST | `/api/v1/users/user/info/update` | `update_user_info_by_session_user` | YES |  |
| users | GET | `/api/v1/users/{user_id}` | `get_user_by_id` | YES |  |
| users | GET | `/api/v1/users/{user_id}/info` | `get_user_info_by_id` | YES |  |
| users | GET | `/api/v1/users/{user_id}/oauth/sessions` | `get_user_oauth_sessions_by_id` | YES |  |
| users | GET | `/api/v1/users/{user_id}/profile/image` | `get_user_profile_image_by_id` | YES |  |
| users | GET | `/api/v1/users/{user_id}/active` | `get_user_active_status_by_id` | YES |  |
| users | POST | `/api/v1/users/{user_id}/update` | `update_user_by_id` | YES |  |
| users | DELETE | `/api/v1/users/{user_id}` | `delete_user_by_id` | YES |  |
| users | GET | `/api/v1/users/{user_id}/groups` | `get_user_groups_by_id` | YES |  |

## utils

| Module | HTTP Method | Path | Handler Function | Auth Required | Brief Description |
|--------|------------|------|-----------------|--------------|-------------------|
| utils | GET | `/api/v1/utils/gravatar` | `get_gravatar` | YES |  |
| utils | POST | `/api/v1/utils/code/format` | `format_code` | YES |  |
| utils | POST | `/api/v1/utils/code/execute` | `execute_code` | YES |  |
| utils | POST | `/api/v1/utils/markdown` | `get_html_from_markdown` | YES |  |
| utils | POST | `/api/v1/utils/pdf` | `download_chat_as_pdf` | YES |  |
| utils | GET | `/api/v1/utils/db/download` | `download_db` | YES |  |
