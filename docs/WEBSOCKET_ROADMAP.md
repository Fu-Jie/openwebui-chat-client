# WebSocket Support Roadmap

## 概述

本文档记录 openwebui-chat-client 项目中 WebSocket 实时通信功能的实现计划。基于对 Open WebUI 官方源码的深入分析，规划完整的 WebSocket 支持路线图。

---

## 🎯 目标

实现与 Open WebUI 前端相同的 WebSocket 实时通信能力：

- **实时流式响应**：通过 WebSocket 接收 AI 回复
- **事件系统**：支持工具调用、RAG 检索等中间状态推送
- **多会话管理**：支持并发多个聊天会话
- **断线重连**：自动重连和状态恢复

---

## 📊 技术分析

### Open WebUI 的 WebSocket 架构

#### 1. 核心组件

```
前端 (Browser)
  ↓
Socket.IO Client (JavaScript)
  ↓
WebSocket Connection
  ↓
Socket.IO Server (Python)
  ↓
Open WebUI Backend
```

#### 2. 关键概念

##### **session_id**

- **来源**：Socket.IO 连接建立时自动分配的 `sid`
- **作用**：标识唯一的浏览器会话/标签页
- **生命周期**：从连接建立到断开
- **存储**：后端 `SESSION_POOL[session_id] = user_info`

##### **通信通道 (Channel)**

```python
channel = f"{user_id}:{session_id}:{request_id}"
# 示例: "user123:abc-def-456:req-789-xyz"
```

- `user_id`: 用户唯一标识
- `session_id`: 会话标识（区分不同标签页）
- `request_id`: 单次请求标识（每次请求新生成）

##### **事件系统**

**客户端 → 服务器**：

```python
await event_caller({
    "type": "request:chat:completion",
    "data": {
        "form_data": {...},
        "channel": channel,
        "session_id": session_id
    }
})
```

**服务器 → 客户端**：

```python
await sio.emit(channel, {
    "type": "message",
    "data": {"content": "回答内容..."}
})
```

#### 3. 关键文件分析

| 文件 | 作用 | 关键函数/类 |
|------|------|------------|
| `socket/main.py` | WebSocket 服务器 | `@sio.event`, `SESSION_POOL`, `get_event_emitter()` |
| `utils/chat.py` | 聊天处理逻辑 | `generate_direct_chat_completion()` |
| `utils/middleware.py` | 事件分发 | 检查 `session_id` 并启用事件系统 |
| `routers/chats.py` | 聊天 API | 接收带 `metadata.session_id` 的请求 |

---

## 🗺️ 实现路线图

### Phase 0: 当前状态 ✅ (已完成)

**状态**：使用 HTTP/SSE 流式响应，无 WebSocket

**功能**：

- ✅ 基础聊天功能
- ✅ SSE 流式响应
- ✅ 文件上传
- ✅ RAG 集成
- ✅ 知识库管理

**限制**：

- ❌ 无实时事件推送
- ❌ 无工具调用中间状态
- ❌ 无多标签页独立会话支持

---

### Phase 1: WebSocket 基础架构 🚧 (计划中)

**优先级**：中
**预估工时**：3-5 天
**依赖**：`python-socketio`, `aiohttp`

#### 1.1 依赖安装

```toml
# pyproject.toml
dependencies = [
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "python-socketio>=5.11.0",  # ← 新增
    "aiohttp>=3.9.0",           # ← 新增 (socketio 需要)
]
```

#### 1.2 创建 AsyncWebSocketClient

**文件**：`openwebui_chat_client/core/async_websocket_client.py`

```python
"""
Async WebSocket Client for Open WebUI.
Provides real-time communication support using Socket.IO.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, Callable
import socketio

logger = logging.getLogger(__name__)


class AsyncWebSocketClient:
    """
    Async WebSocket client for real-time communication.
    
    Features:
    - Socket.IO connection management
    - Automatic reconnection
    - Event handling
    - Channel-based message routing
    """
    
    def __init__(self, base_url: str, auth_token: str):
        """
        Initialize WebSocket client.
        
        Args:
            base_url: Open WebUI base URL
            auth_token: Authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        
        # Socket.IO client
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
            logger=False,
            engineio_logger=False
        )
        
        # State
        self.connected = False
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # Event handlers
        self._channel_handlers: Dict[str, Callable] = {}
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup Socket.IO event handlers."""
        
        @self.sio.event
        async def connect():
            self.connected = True
            self.session_id = self.sio.sid
            logger.info(f"✅ WebSocket connected: {self.session_id}")
        
        @self.sio.event
        async def disconnect():
            self.connected = False
            logger.warning("⚠️ WebSocket disconnected")
        
        @self.sio.event
        async def connect_error(data):
            logger.error(f"❌ WebSocket connection error: {data}")
    
    async def connect(self):
        """Establish WebSocket connection."""
        socket_url = f"{self.base_url}/socket.io/"
        
        try:
            await self.sio.connect(
                socket_url,
                auth={"token": self.auth_token},
                transports=["websocket", "polling"]
            )
            
            # Wait for connection to be established
            timeout = 10
            elapsed = 0
            while not self.connected and elapsed < timeout:
                await asyncio.sleep(0.1)
                elapsed += 0.1
            
            if not self.connected:
                raise TimeoutError("WebSocket connection timeout")
            
            logger.info(f"🔗 WebSocket connected with session_id: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect WebSocket: {e}")
            raise
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.connected:
            await self.sio.disconnect()
            logger.info("🔌 WebSocket disconnected")
    
    def register_channel_handler(
        self,
        channel: str,
        handler: Callable[[Dict[str, Any]], None]
    ):
        """
        Register a handler for a specific channel.
        
        Args:
            channel: Channel identifier (user_id:session_id:request_id)
            handler: Async function to handle messages
        """
        @self.sio.on(channel)
        async def channel_handler(data):
            await handler(data)
        
        self._channel_handlers[channel] = handler
        logger.debug(f"📡 Registered handler for channel: {channel}")
    
    def unregister_channel_handler(self, channel: str):
        """Unregister a channel handler."""
        if channel in self._channel_handlers:
            # Remove from Socket.IO
            if channel in self.sio.handlers.get("/", {}):
                del self.sio.handlers["/"][channel]
            
            # Remove from our tracking
            del self._channel_handlers[channel]
            logger.debug(f"🔇 Unregistered handler for channel: {channel}")
    
    async def emit(self, event: str, data: Dict[str, Any]):
        """
        Emit an event to the server.
        
        Args:
            event: Event name
            data: Event data
        """
        if not self.connected:
            raise ConnectionError("WebSocket not connected")
        
        await self.sio.emit(event, data)
        logger.debug(f"📤 Emitted event: {event}")
    
    async def wait_for(self, channel: str, timeout: float = 30.0) -> Any:
        """
        Wait for a message on a specific channel.
        
        Args:
            channel: Channel to listen on
            timeout: Timeout in seconds
            
        Returns:
            Received data
        """
        future = asyncio.Future()
        
        async def handler(data):
            if not future.done():
                future.set_result(data)
        
        self.register_channel_handler(channel, handler)
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        finally:
            self.unregister_channel_handler(channel)
    
    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected
    
    def __enter__(self):
        """Context manager entry (not for async)."""
        raise TypeError("Use 'async with' for AsyncWebSocketClient")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
```

#### 1.3 测试用例

**文件**：`tests/test_websocket/test_async_websocket_client.py`

```python
import pytest
import asyncio
from openwebui_chat_client.core.async_websocket_client import AsyncWebSocketClient


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection establishment."""
    client = AsyncWebSocketClient(
        base_url="http://localhost:3000",
        auth_token="test_token"
    )
    
    await client.connect()
    assert client.is_connected
    assert client.session_id is not None
    
    await client.disconnect()
    assert not client.is_connected


@pytest.mark.asyncio
async def test_channel_handler():
    """Test channel-based message handling."""
    client = AsyncWebSocketClient(
        base_url="http://localhost:3000",
        auth_token="test_token"
    )
    
    received_data = []
    
    async def handler(data):
        received_data.append(data)
    
    await client.connect()
    
    channel = "test_channel"
    client.register_channel_handler(channel, handler)
    
    # Simulate message (would come from server in real scenario)
    # await client.sio.emit(channel, {"test": "data"})
    
    await client.disconnect()


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager usage."""
    async with AsyncWebSocketClient(
        base_url="http://localhost:3000",
        auth_token="test_token"
    ) as client:
        assert client.is_connected
    
    # Should be disconnected after context exit
    assert not client.is_connected
```

---

### Phase 2: 集成到主客户端 🔄 (待实施)

**优先级**：中
**预估工时**：2-3 天
**依赖**：Phase 1

#### 2.1 扩展 AsyncOpenWebUIClient

**文件**：`openwebui_chat_client/async_openwebui_client.py`

```python
class AsyncOpenWebUIClient:
    """Async client with optional WebSocket support."""
    
    def __init__(
        self,
        base_url: str,
        auth_token: str,
        default_model: str,
        enable_websocket: bool = False  # ← 新参数
    ):
        self.base_client = AsyncBaseClient(base_url, auth_token)
        self.default_model = default_model
        self.enable_websocket = enable_websocket
        
        # WebSocket client (optional)
        self.ws_client: Optional[AsyncWebSocketClient] = None
        if enable_websocket:
            self.ws_client = AsyncWebSocketClient(base_url, auth_token)
    
    async def connect(self):
        """Initialize connection (including WebSocket if enabled)."""
        if self.enable_websocket and self.ws_client:
            await self.ws_client.connect()
            logger.info("✅ WebSocket enabled")
    
    async def disconnect(self):
        """Close all connections."""
        if self.ws_client:
            await self.ws_client.disconnect()
    
    async def chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None,
        **kwargs
    ):
        """
        Send chat message with optional WebSocket support.
        """
        # Generate IDs if not provided
        chat_id = chat_id or str(uuid.uuid4())
        message_id = message_id or str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        
        # Build metadata
        metadata = {
            "user_id": self.user_id,
            "chat_id": chat_id,
            "message_id": message_id
        }
        
        # Add session_id if WebSocket is enabled
        if self.ws_client and self.ws_client.is_connected:
            metadata["session_id"] = self.ws_client.session_id
        
        # Prepare request
        payload = {
            "model": kwargs.get("model_id", self.default_model),
            "messages": self._build_messages(question),
            "stream": kwargs.get("stream", True),
            "metadata": metadata
        }
        
        # Use WebSocket or HTTP
        if metadata.get("session_id"):
            return await self._chat_with_websocket(
                payload, request_id, metadata
            )
        else:
            return await self._chat_with_http(payload)
    
    async def _chat_with_websocket(
        self,
        payload: Dict,
        request_id: str,
        metadata: Dict
    ):
        """Handle chat with WebSocket real-time events."""
        user_id = metadata["user_id"]
        session_id = metadata["session_id"]
        channel = f"{user_id}:{session_id}:{request_id}"
        
        # Setup message collector
        messages = []
        
        async def message_handler(data):
            if isinstance(data, dict):
                if "done" in data and data["done"]:
                    return  # Stop
                messages.append(data)
        
        # Register handler
        self.ws_client.register_channel_handler(channel, message_handler)
        
        try:
            # Send request
            response = await self.base_client.post(
                "/api/chat/completions",
                json=payload
            )
            
            # Wait for completion or timeout
            timeout = 300  # 5 minutes
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                if messages and messages[-1].get("done"):
                    break
                await asyncio.sleep(0.1)
            
            return self._process_websocket_messages(messages)
            
        finally:
            # Cleanup
            self.ws_client.unregister_channel_handler(channel)
```

#### 2.2 向后兼容性

保持现有 API 不变：

- 默认 `enable_websocket=False`
- 用户可以选择启用
- 无 WebSocket 时自动回退到 HTTP/SSE

---

### Phase 3: 高级功能 🚀 (未来)

**优先级**：低
**预估工时**：5-7 天

#### 3.1 实时事件系统

- [ ] 工具调用进度推送
- [ ] RAG 检索状态显示
- [ ] 图片生成进度
- [ ] 思考过程可视化

#### 3.2 协作功能

- [ ] 多用户实时协作
- [ ] 聊天共享
- [ ] 实时通知

#### 3.3 性能优化

- [ ] 连接池管理
- [ ] 消息队列
- [ ] 断线重连策略
- [ ] 心跳检测

---

## 📦 技术依赖

### 新增 Python 包

```toml
[project]
dependencies = [
    # 现有依赖
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    
    # WebSocket 支持
    "python-socketio>=5.11.0",
    "aiohttp>=3.9.0",
    "websockets>=12.0",  # 可选，用于更底层的控制
]
```

### 兼容性要求

- Python >= 3.8 (asyncio 支持)
- Open WebUI >= 0.1.0 (Socket.IO 支持)
- 网络环境支持 WebSocket 协议

---

## 🧪 测试策略

### 单元测试

- [ ] WebSocket 连接/断开
- [ ] 通道注册/注销
- [ ] 消息处理
- [ ] 错误处理
- [ ] 重连机制

### 集成测试

- [ ] 与真实 Open WebUI 服务器通信
- [ ] 流式响应完整性
- [ ] 并发多会话
- [ ] 长时间运行稳定性

### 性能测试

- [ ] 连接建立时间
- [ ] 消息延迟
- [ ] 内存占用
- [ ] 并发连接数

---

## 📝 文档更新

### 需要更新的文档

- [ ] README.md - 添加 WebSocket 使用说明
- [ ] API Reference - 新增 AsyncWebSocketClient
- [ ] User Guide - WebSocket vs HTTP 对比
- [ ] Examples - WebSocket 使用示例
- [ ] CHANGELOG - 记录重大变更

### 示例代码

```python
# examples/advanced_features/websocket_chat.py
"""
Example: Real-time chat with WebSocket support.
"""

import asyncio
from openwebui_chat_client import AsyncOpenWebUIClient


async def main():
    # Create client with WebSocket enabled
    async with AsyncOpenWebUIClient(
        base_url="http://localhost:3000",
        auth_token="your_token",
        default_model="gpt-4",
        enable_websocket=True  # ← Enable WebSocket
    ) as client:
        
        # Connect WebSocket
        await client.connect()
        
        # Chat with real-time events
        result = await client.chat(
            question="Explain quantum computing",
            stream=True
        )
        
        print(f"Response: {result['content']}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎯 成功标准

### Phase 1 完成标准

- [x] `AsyncWebSocketClient` 类实现
- [x] 基础连接管理
- [x] 事件处理机制
- [x] 单元测试覆盖 >80%

### Phase 2 完成标准

- [ ] 集成到 `AsyncOpenWebUIClient`
- [ ] 向后兼容
- [ ] 集成测试通过
- [ ] 文档完整

### Phase 3 完成标准

- [ ] 高级功能实现
- [ ] 性能基准达标
- [ ] 生产环境验证

---

## 🚧 已知挑战

### 技术挑战

1. **认证方式**
   - Open WebUI 使用 JWT token 进行 WebSocket 认证
   - 需要正确处理 token 过期和刷新

2. **消息顺序**
   - WebSocket 消息可能乱序
   - 需要实现序列号机制

3. **错误处理**
   - 网络断开时的状态恢复
   - 重连后的会话恢复

4. **并发控制**
   - 多个异步请求的通道管理
   - 避免内存泄漏

### 解决方案

- 使用 `python-socketio` 的成熟特性
- 参考官方前端实现
- 增量开发，逐步验证

---

## 📅 时间规划

| 阶段 | 预估时间 | 状态 | 备注 |
|------|---------|------|------|
| Phase 0 | - | ✅ 完成 | 当前 HTTP/SSE 实现 |
| Phase 1.1 | 1天 | 📅 计划 | 依赖安装和环境准备 |
| Phase 1.2 | 3天 | 📅 计划 | AsyncWebSocketClient 实现 |
| Phase 1.3 | 1天 | 📅 计划 | 单元测试编写 |
| Phase 2.1 | 2天 | ⏳ 待定 | 集成到主客户端 |
| Phase 2.2 | 1天 | ⏳ 待定 | 兼容性测试 |
| Phase 3 | 5-7天 | ⏳ 待定 | 高级功能（可选）|

**总计**：约 13-16 天（不含 Phase 3）

---

## 🔗 相关资源

### 官方文档

- [Socket.IO Python Client](https://python-socketio.readthedocs.io/)
- [Open WebUI GitHub](https://github.com/open-webui/open-webui)

### 代码参考

- `open_webui/socket/main.py` - WebSocket 服务器实现
- `open_webui/utils/chat.py` - 聊天逻辑
- Open WebUI 前端 - JavaScript WebSocket 客户端

### 相关 Issues

- #TBD - WebSocket support tracking issue (待创建)

---

## 📊 优先级评估

### 当前优先级：**中等**

**原因**：

- ✅ 现有 HTTP/SSE 实现已满足大部分需求
- ⚠️ WebSocket 是锦上添花，不是必需品
- 🎯 重点应先完成架构重构和测试覆盖

**建议**：

1. 先完成架构重构（Phase 1-4 in 主 roadmap）
2. 达到 80% 测试覆盖率
3. 再考虑 WebSocket 功能

---

## ✅ 决策记录

### 2026-01-22

- **决策**：暂不实现 WebSocket，聚焦核心架构重构
- **理由**：HTTP/SSE 已足够强大，避免过早优化
- **下一步**：完成 BaseManager 和 ChatManager 重构

### 未来决策

- 待用户反馈确定是否需要 WebSocket
- 待性能测试确定是否需要优化

---

## 🎓 学习要点

通过本次分析，我们学到：

1. **session_id 的本质**
   - 它是 WebSocket 会话的标识符
   - 用于构建通信通道
   - 支持多标签页并发

2. **Open WebUI 的架构智慧**
   - 优雅的降级策略（有 WebSocket 用 WebSocket，没有用 HTTP）
   - 清晰的职责分离（连接管理、消息路由、业务逻辑）
   - 灵活的事件系统

3. **我们的选择**
   - 先做好基础（HTTP/SSE）
   - 保持架构可扩展性
   - 未来可以无缝添加 WebSocket

---

**最后更新**：2026-01-22  
**状态**：📝 规划中  
**责任人**：Development Team
