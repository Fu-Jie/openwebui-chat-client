#!/usr/bin/env python3
"""
ChatManager Integration Test - Phase 2

验证ChatManager继承BaseManager后的基础功能。
"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.modules.chat_manager import ChatManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestChatManagerPhase2(unittest.TestCase):
    """测试ChatManager Phase 2重构 - BaseManager集成"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
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
        self.chat_manager = ChatManager(self.base_client)

    def test_01_chat_manager_inherits_base_manager(self):
        """测试1: ChatManager继承BaseManager"""
        logger.info("🧪 测试ChatManager继承BaseManager...")

        from openwebui_chat_client.core.base_manager import BaseManager

        # 验证继承关系
        self.assertIsInstance(
            self.chat_manager, BaseManager, "ChatManager应该继承BaseManager"
        )

        logger.info("✅ ChatManager正确继承BaseManager")

    def test_02_chat_manager_has_base_manager_methods(self):
        """测试2: ChatManager拥有BaseManager的方法"""
        logger.info("🧪 测试ChatManager拥有BaseManager方法...")

        # 验证关键方法存在
        required_methods = [
            "_make_request",
            "_get_json_response",
            "_build_pagination_params",
            "_build_filter_params",
            "_parse_list_response",
            "_validate_required_fields",
            "_build_url",
            "_batch_operation",
            "_log_operation_start",
        ]

        for method in required_methods:
            self.assertTrue(
                hasattr(self.chat_manager, method), f"ChatManager应该有{method}方法"
            )

        logger.info(f"✅ ChatManager拥有所有{len(required_methods)}个BaseManager方法")

    def test_03_chat_manager_properties(self):
        """测试3: ChatManager属性访问"""
        logger.info("🧪 测试ChatManager属性...")

        # 验证属性
        self.assertIsNotNone(self.chat_manager.session, "session应该不为空")
        self.assertEqual(self.chat_manager.base_url, self.base_url, "base_url应该匹配")
        self.assertIn(
            "Authorization",
            self.chat_manager.json_headers,
            "应该包含Authorization header",
        )

        # 验证backward compatibility属性
        self.assertIsNotNone(
            self.chat_manager.base_client, "base_client应该存在（向后兼容）"
        )

        logger.info("✅ ChatManager属性正常")

    def test_04_chat_manager_can_make_requests(self):
        """测试4: ChatManager可以发起HTTP请求"""
        logger.info("🧪 测试ChatManager HTTP请求能力...")

        # 使用BaseManager的_make_request方法
        response = self.chat_manager._make_request("GET", "/api/v1/models")

        self.assertIsNotNone(response, "请求应该返回响应")
        self.assertEqual(response.status_code, 200, "状态码应该是200")

        logger.info("✅ ChatManager HTTP请求正常")

    def test_05_chat_manager_can_get_json(self):
        """测试5: ChatManager可以获取JSON响应"""
        logger.info("🧪 测试ChatManager JSON解析...")

        # 使用BaseManager的_get_json_response方法
        data = self.chat_manager._get_json_response("GET", "/api/v1/models")

        self.assertIsNotNone(data, "JSON响应应该不为空")
        self.assertIsInstance(data, dict, "应该返回字典")

        logger.info("✅ ChatManager JSON解析正常")

    def test_06_chat_manager_pagination_params(self):
        """测试6: ChatManager构建分页参数"""
        logger.info("🧪 测试ChatManager分页参数...")

        # 使用BaseManager的_build_pagination_params
        params = self.chat_manager._build_pagination_params(page=2, page_size=10)

        self.assertEqual(params["skip"], 10, "skip应该是10")
        self.assertEqual(params["limit"], 10, "limit应该是10")

        logger.info("✅ ChatManager分页参数正常")

    def test_07_chat_manager_logging_methods(self):
        """测试7: ChatManager日志记录方法"""
        logger.info("🧪 测试ChatManager日志方法...")

        # 使用BaseManager的日志方法
        self.chat_manager._log_operation_start("test_operation", chat_id="123")
        self.chat_manager._log_operation_success("test_operation", result="成功")

        # 不应该抛出异常
        logger.info("✅ ChatManager日志方法正常")

    def test_08_list_chats_uses_base_manager(self):
        """测试8: list_chats使用BaseManager方法"""
        logger.info("🧪 测试list_chats功能...")

        # 调用list_chats（应该使用BaseManager的方法）
        try:
            chats = self.chat_manager.list_chats(page=1)

            # 如果成功，验证返回类型
            if chats is not None:
                self.assertIsInstance(chats, list, "应该返回列表")
                logger.info(f"   ✅ 成功获取 {len(chats)} 个聊天")
            else:
                logger.info("   ℹ️  list_chats返回None（可能没有聊天记录）")

        except Exception as e:
            self.fail(f"list_chats调用失败: {e}")

        logger.info("✅ list_chats功能正常")

    def test_09_backward_compatibility(self):
        """测试9: 向后兼容性"""
        logger.info("🧪 测试向后兼容性...")

        # 验证旧属性仍然可用
        self.assertIsNotNone(self.chat_manager.base_client, "base_client应该存在")
        self.assertEqual(
            self.chat_manager.base_client, self.base_client, "base_client应该是相同对象"
        )

        # 验证Mixin方法仍然存在
        mixin_methods = [
            "chat",  # ChatOperationsMixin
            "list_chats",  # ChatQueriesMixin
            "create_folder",  # ChatFoldersMixin
        ]

        for method in mixin_methods:
            self.assertTrue(
                hasattr(self.chat_manager, method), f"Mixin方法 {method} 应该仍然存在"
            )

        logger.info("✅ 向后兼容性验证通过")

    def test_10_integration_flow(self):
        """测试10: 集成流程"""
        logger.info("🧪 测试集成流程...")

        # 1. 构建参数
        pagination = self.chat_manager._build_pagination_params(1, 5)
        logger.info(f"   📄 分页参数: {pagination}")

        # 2. 发起请求
        response = self.chat_manager._get_json_response(
            "GET", "/api/v1/models", params=pagination
        )

        # 3. 解析响应
        if response:
            items, total = self.chat_manager._parse_list_response(response)
            logger.info(f"   ✅ 获取 {len(items)} 个模型 (总数: {total})")
            self.assertIsInstance(items, list, "应该返回列表")

        logger.info("✅ 集成流程测试完成")


def run_tests():
    """运行测试套件"""
    print("\n" + "=" * 70)
    print("🚀 ChatManager Phase 2 集成测试")
    print("=" * 70)
    print("\n🔧 环境配置:")
    print(f"   Base URL: {os.getenv('OUI_BASE_URL', 'http://localhost:3003')}")
    print(f"   Auth Token: {os.getenv('OUI_AUTH_TOKEN', 'Not Set')[:20]}...")
    print("\n🧪 开始测试...\n")

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatManagerPhase2)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("📊 测试结果")
    print("=" * 70)
    print(
        f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}"
    )
    print(f"❌ 失败: {len(result.failures)}")
    print(f"💥 错误: {len(result.errors)}")
    print(f"⏭️  跳过: {len(result.skipped)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
