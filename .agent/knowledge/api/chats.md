# OpenWebUI Chat APIs
>
> 核心聊天与生成接口相关文档 (Core Chat & Completion APIs)

## 1. 对话补全 (Chat Completions)

- **Endpoint**: `POST /api/chat/completions`
- **Description**: 用于发送消息、重新生成 (Regenerate) 以及编辑后发送 (Edit).
- **Behavior (The Task ID mechanism)**:
  - 当前端请求生成时，如果请求不是简单的同步流式返回，服务器经常会返回 `{"status": true, "task_id": "..."}`。
  - 这是 OpenWebUI 的异步任务处理架构。前端在拿到 `task_id` 后，并不直接等待，而是通过持续长轮询或连接 `GET /api/v1/chats/:id` 来获得实时的内容更新。
- **Regenerate vs Edit**:
  - `Regenerate` (重新生成): 复用旧的 `messages` 历史，向此接口发送时带上目标消息的 `parent_id`。这样可以在 UI 上形成 `1/2` 这种多版本的树状结构。
  - `Edit` (编辑): 如果用户编辑了某个消息再发送，也是调用此接口，但替换最后一条消息的内容，同样需要正确的 `id` 和 `parent_id` 追踪。

## 2. 对话管理 (Chat Management)

- **Create**: `POST /api/v1/chats/new`
  - 负载通常包含初始的模板或空结构 `chat: {title, models, messages: []}`，返回生成的对话 `id`。
- **Update History**: `POST /api/v1/chats/:id`
  - 对话过程中，UI 会频繁调用此接口来持久化对话的 tags (标签)、完整的 messages 树等。
- **Delete**: `DELETE /api/v1/chats/:id`
  - 彻底删除某条对话以及服务端保存的历史树。

## 3. 附件上传机制 (File Upload in Chat)

*(To be investigated thoroughly, usually hits `/api/v1/files/` first before attaching to messages)*
