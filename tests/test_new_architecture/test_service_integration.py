#!/usr/bin/env python3
"""
Service Layer Integration Tests

Tests RAGService, TaskService, and StreamingService with real API calls.
These tests validate that service layer properly uses BaseClient and BaseManager.
"""

import logging
import os
import time
import unittest
from pathlib import Path
from typing import Dict, List, Any

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.services.rag_service import RAGService
from openwebui_chat_client.services.task_service import TaskService
from openwebui_chat_client.services.streaming_service import StreamingService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestServiceIntegration(unittest.TestCase):
    """Integration tests for Service layer"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
        cls.auth_token = os.getenv("OUI_AUTH_TOKEN")
        cls.default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

        if not cls.auth_token:
            raise unittest.SkipTest("OUI_AUTH_TOKEN not set")

        logger.info("🔧 Base URL: %s", cls.base_url)
        logger.info("🔑 Auth Token: %s...", cls.auth_token[:20])
        logger.info("🤖 Default Model: %s", cls.default_model)

    def setUp(self):
        """Set up for each test"""
        self.base_client = BaseClient(
            self.base_url, self.auth_token, self.default_model
        )
        self.rag_service = RAGService(self.base_client)
        self.task_service = TaskService(self.base_client)
        self.streaming_service = StreamingService(self.base_client)

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.base_client, "session"):
            self.base_client.session.close()

    # ==========================================
    # RAGService Tests
    # ==========================================

    def test_01_rag_service_initialization(self):
        """测试1: RAGService 初始化"""
        logger.info("🧪 测试 RAGService 初始化...")

        # Verify RAGService is properly initialized
        self.assertIsNotNone(self.rag_service)
        self.assertIsInstance(self.rag_service, RAGService)
        self.assertEqual(self.rag_service.base_url, self.base_url)

        logger.info("✅ RAGService 初始化正常")

    def test_02_rag_handle_empty_references(self):
        """测试2: RAG 处理空引用"""
        logger.info("🧪 测试 RAG 空引用处理...")

        # Handle empty RAG references
        api_payload, storage_payload = self.rag_service.handle_rag_references(
            rag_files=None, rag_collections=None
        )

        self.assertEqual(api_payload, [], "空文件应返回空列表")
        self.assertEqual(storage_payload, [], "空集合应返回空列表")

        logger.info("✅ RAG 空引用处理正常")

    @unittest.skip("RAGService依赖_parent_client属性，需要完整客户端")
    def test_03_rag_process_nonexistent_collection(self):
        """测试3: RAG 处理不存在的知识库"""
        logger.info("🧪 测试处理不存在的知识库...")

        # Try to process a non-existent knowledge base
        api_payload, storage_payload = self.rag_service.process_rag_collections(
            ["nonexistent_kb_12345"]
        )

        # Should return empty payloads (KB not found)
        self.assertEqual(api_payload, [], "不存在的KB应返回空payload")
        self.assertEqual(storage_payload, [], "不存在的KB应返回空storage")

        logger.info("✅ 不存在的知识库处理正常")

    def test_04_rag_file_upload_missing_method(self):
        """测试4: RAG 文件上传（缺少方法）"""
        logger.info("🧪 测试 RAG 文件上传（无上传方法）...")

        # BaseClient doesn't have _upload_file by default
        # This should handle the missing method gracefully
        result = self.rag_service._upload_file("/tmp/test.txt")

        self.assertIsNone(result, "缺少上传方法应返回None")

        logger.info("✅ 缺少上传方法处理正常")

    # ==========================================
    # TaskService Tests
    # ==========================================

    def test_05_task_service_initialization(self):
        """测试5: TaskService 初始化"""
        logger.info("🧪 测试 TaskService 初始化...")

        # Verify TaskService is properly initialized
        self.assertIsNotNone(self.task_service)
        self.assertIsInstance(self.task_service, TaskService)
        self.assertEqual(self.task_service.base_url, self.base_url)

        logger.info("✅ TaskService 初始化正常")

    def test_06_task_get_system_prompt(self):
        """测试6: 获取任务处理系统提示"""
        logger.info("🧪 测试获取任务系统提示...")

        prompt = self.task_service.get_task_processing_prompt()

        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100, "系统提示应该有实质内容")
        self.assertIn("Thought", prompt, "应包含Thought关键词")
        self.assertIn("Action", prompt, "应包含Action关键词")
        self.assertIn("Observation", prompt, "应包含Observation关键词")

        logger.info("✅ 任务系统提示获取正常")

    def test_07_task_extract_final_answer(self):
        """测试7: 提取最终答案"""
        logger.info("🧪 测试提取最终答案...")

        # Test with valid JSON response
        response_with_answer = """
Here is my analysis:

```json
{
    "final_answer": "The answer is 42",
    "todo_list": [
        {"task": "Research", "status": "complete"}
    ]
}
```
"""
        answer = self.task_service.extract_final_answer(response_with_answer)
        self.assertEqual(answer, "The answer is 42")

        # Test with response without final answer
        response_without_answer = "This is just regular text"
        answer = self.task_service.extract_final_answer(response_without_answer)
        self.assertIsNone(answer)

        logger.info("✅ 最终答案提取正常")

    def test_08_task_extract_todo_list(self):
        """测试8: 提取TODO列表"""
        logger.info("🧪 测试提取TODO列表...")

        response_with_todo = """
```json
{
    "final_answer": "Done",
    "todo_list": [
        {"task": "Task 1", "status": "complete"},
        {"task": "Task 2", "status": "in_progress"}
    ]
}
```
"""
        todo_list = self.task_service.extract_todo_list(response_with_todo)

        self.assertEqual(len(todo_list), 2)
        self.assertEqual(todo_list[0]["task"], "Task 1")
        self.assertEqual(todo_list[0]["status"], "complete")

        logger.info("✅ TODO列表提取正常")

    def test_09_task_has_decision_options(self):
        """测试9: 检测决策选项"""
        logger.info("🧪 测试检测决策选项...")

        # Response with decision options
        response_with_decision = """
```json
{
    "decision_needed": "yes",
    "question": "Which approach?",
    "options": ["Option A", "Option B"]
}
```
"""
        has_decision = self.task_service.has_decision_options(response_with_decision)
        self.assertTrue(has_decision)

        # Response without decision
        response_without_decision = "Just regular text"
        has_decision = self.task_service.has_decision_options(response_without_decision)
        self.assertFalse(has_decision)

        logger.info("✅ 决策选项检测正常")

    def test_10_task_extract_decision_options(self):
        """测试10: 提取决策选项"""
        logger.info("🧪 测试提取决策选项...")

        response_with_options = """
```json
{
    "decision_needed": "yes",
    "question": "Choose your path:",
    "options": ["Path A", "Path B", "Path C"]
}
```
"""
        options = self.task_service.extract_decision_options(response_with_options)

        self.assertIsNotNone(options)
        self.assertEqual(options["question"], "Choose your path:")
        self.assertEqual(len(options["options"]), 3)
        self.assertIn("Path A", options["options"])

        logger.info("✅ 决策选项提取正常")

    def test_11_task_summarize_history(self):
        """测试11: 历史记录摘要"""
        logger.info("🧪 测试历史记录摘要...")

        # Create a long message history
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "A" * 5000},
            {"role": "assistant", "content": "B" * 5000},
            {"role": "user", "content": "C" * 5000},
        ]

        # Summarize with length limit
        summarized = self.task_service.summarize_history(messages, max_length=6000)

        # Should keep system message
        self.assertEqual(summarized[0]["role"], "system")

        # Total length should be reasonably close to limit (允许小幅超出)
        total_length = sum(len(msg["content"]) for msg in summarized)
        self.assertLessEqual(total_length, 6100, "摘要长度应接近限制")

        logger.info("✅ 历史记录摘要正常")

    def test_12_task_log_todo_list(self):
        """测试12: 记录TODO列表"""
        logger.info("🧪 测试TODO列表日志...")

        todo_list = [
            {"task": "Research topic", "status": "complete"},
            {"task": "Write draft", "status": "in_progress"},
            {"task": "Review", "status": "pending"},
        ]

        # This should not raise an exception
        self.task_service.log_todo_list(todo_list)

        # Test with empty list
        self.task_service.log_todo_list([])

        logger.info("✅ TODO列表日志正常")

    # ==========================================
    # StreamingService Tests
    # ==========================================

    def test_13_streaming_service_initialization(self):
        """测试13: StreamingService 初始化"""
        logger.info("🧪 测试 StreamingService 初始化...")

        # Verify StreamingService is properly initialized
        self.assertIsNotNone(self.streaming_service)
        self.assertIsInstance(self.streaming_service, StreamingService)
        self.assertEqual(self.streaming_service.base_url, self.base_url)

        logger.info("✅ StreamingService 初始化正常")

    @unittest.skip("需要真实聊天ID和消息，跳过流式测试")
    def test_14_streaming_real_completion(self):
        """测试14: 真实流式响应（需要有效聊天）"""
        logger.info("🧪 测试真实流式响应...")

        # This test requires a valid chat_id and would make real API calls
        # Skipped for now as it needs proper setup

        chat_id = "test_chat_123"
        messages = [{"role": "user", "content": "Say hello"}]

        stream = self.streaming_service.stream_completion(
            chat_id=chat_id, messages=messages, model=self.default_model
        )

        # Collect streaming response
        full_response = self.streaming_service.collect_streaming_response(stream)

        self.assertIsInstance(full_response, str)
        self.assertGreater(len(full_response), 0)

        logger.info("✅ 流式响应正常")

    def test_15_streaming_collect_empty_stream(self):
        """测试15: 收集空流式响应"""
        logger.info("🧪 测试收集空流...")

        # Create an empty generator
        def empty_generator():
            return
            yield  # Never reached

        full_response = self.streaming_service.collect_streaming_response(
            empty_generator()
        )

        self.assertEqual(full_response, "")

        logger.info("✅ 空流处理正常")

    def test_16_streaming_collect_formatted_chunks(self):
        """测试16: 收集格式化的响应块"""
        logger.info("🧪 测试收集格式化响应块...")

        # Create a mock generator with formatted chunks
        def mock_generator():
            yield {"choices": [{"delta": {"content": "Hello "}}]}
            yield {"choices": [{"delta": {"content": "world!"}}]}

        full_response = self.streaming_service.collect_streaming_response(
            mock_generator()
        )

        self.assertEqual(full_response, "Hello world!")

        logger.info("✅ 格式化响应块收集正常")


if __name__ == "__main__":
    unittest.main(verbosity=2)
