import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量 (需要安装 python-dotenv: pip install python-dotenv)
load_dotenv()

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.async_openwebui_client import AsyncOpenWebUIClient

# 从环境变量读取配置，提供默认值为 localhost:3003 的测试环境
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3003")
TOKEN = os.getenv("OUI_AUTH_TOKEN", "sk-2053c9c4d4994d0398bc2484d6874ef5")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")


def test_sync_client():
    print("\n" + "=" * 50)
    print("🚀 测试同步客户端 (Sync Client) - localhost:3003")
    print("=" * 50)

    try:
        # 初始化同步客户端
        client = OpenWebUIClient(
            base_url=BASE_URL, token=TOKEN, default_model_id=DEFAULT_MODEL
        )
        print("✅ 同步客户端初始化成功")

        # 测试 1: 创建全新无名会话 (利用刚重构的功能，默认命名为 "New Chat")
        print("\n--- 1. 测试创建新会话 ---")
        response1 = client.chat(
            question="你好！这是一条同步测试消息，用来验证后端自动生成的无名会话功能。",
        )
        if response1:
            print(f"回复: {response1.content}")
            print(f"新会话 ID (由服务器分配): {response1.chat_id}")
            print(f"当前客户端被绑定到了这个新会话中: {client.chat_id}")

            # 测试 2: 保持当前对象，直接发送第二句话，会自动使用上面的 chat_id
            print("\n--- 2. 测试在当前会话继续提问 ---")
            response2 = client.chat(question="我刚才发送了什么内容？")
            print(f"回复: {response2.content}")
            print(f"使用的会话 ID: {response2.chat_id}")

            # 清理测试数据
            if response1.chat_id:
                client._chat_manager.delete_chat(response1.chat_id)
                print(f"已清理测试会话: {response1.chat_id}")
        else:
            print("❌ 获取回复失败")

    except Exception as e:
        print(f"❌ 同步测试出现异常: {e}")


async def test_async_client():
    print("\n" + "=" * 50)
    print("🚀 测试异步客户端 (Async Client) - localhost:3003")
    print("=" * 50)

    try:
        # 初始化异步客户端
        async_client = AsyncOpenWebUIClient(
            base_url=BASE_URL, token=TOKEN, default_model_id=DEFAULT_MODEL
        )
        print("✅ 异步客户端初始化成功")

        # 测试 1: 发送消息时仅传入 chat_title 进行标题搜索，或者自动生成无名会话
        print("\n--- 1. 异步创建/搜索会话测试 ---")
        response = await async_client.chat(
            question="你好！这是一条异步测试消息。",
            chat_title="自动化测试会话",  # 显式传递一个标题，它会自动搜索该标题不存在时再创建
        )

        if response:
            print(f"回复: {response.content}")
            print(f"会话 ID: {response.chat_id}")

            # 测试 2: 获取会话列表 (验证返回的是 Pydantic 模型而不是字典)
            print("\n--- 2. 异步检索聊天列表 (验证 Pydantic) ---")
            chats = await async_client._chat_manager.list_chats(page=1)
            if chats:
                print(f"找到了 {len(chats)} 个会话。最新的一个：")
                latest_chat = chats[0]  # ChatDetails 对象
                print(f"  - 标题: {latest_chat.title}")  # 属性访问
                print(f"  - ID: {latest_chat.id}")  # 属性访问

            # 清理数据
            if response.chat_id:
                await async_client._chat_manager.delete_chat(response.chat_id)
                print(f"已清理异步测试会话: {response.chat_id}")
        else:
            print("❌ 异步获取回复失败")

    except Exception as e:
        print(f"❌ 异步测试出现异常: {e}")


if __name__ == "__main__":
    test_sync_client()
    asyncio.run(test_async_client())
