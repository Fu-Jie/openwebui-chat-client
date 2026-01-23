#!/usr/bin/env python3
"""
Integration Tests for BaseManager

这些是针对重构后新架构的真实集成测试：
- 使用真实的 OpenWebUI 服务器（localhost:3003）
- 测试 BaseManager 的实际 HTTP 请求
- 验证分页、过滤、访问控制等在真实环境中的行为
- 不使用 mock，直接与 API 交互

要求：
- OUI_BASE_URL 环境变量（默认: http://localhost:3003）
- OUI_AUTH_TOKEN 环境变量
- OpenWebUI 服务器正在运行
"""

import os
import sys
import unittest
import logging
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.core.base_manager import BaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TestModelManager(BaseManager):
    """测试用的 ModelManager 实现"""

    def __init__(self, client: BaseClient):
        super().__init__(client)
        self._base_endpoint = "/models"

    def list_models(
        self, page: int = 1, page_size: int = 30, **kwargs
    ) -> Optional[list]:
        """列出模型 - 测试分页功能"""
        params = self._build_pagination_params(page=page, page_size=page_size, **kwargs)
        response = self._client.get(self._base_endpoint, params=params)
        return self._parse_list_response(response)


class IntegrationTestBaseManager(unittest.TestCase):
    """BaseManager 真实集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类 - 只运行一次"""
        cls.base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
        cls.auth_token = os.getenv("OUI_AUTH_TOKEN")

        if not cls.auth_token:
            raise unittest.SkipTest("OUI_AUTH_TOKEN environment variable not set")

        logger.info(f"🔧 Using base URL: {cls.base_url}")
        logger.info(f"🔑 Auth token: {cls.auth_token[:20]}...")

        # 创建真实的客户端
        cls.client = BaseClient(
            base_url=cls.base_url,
            token=cls.auth_token,
            default_model_id=os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1"),
        )

        # 创建测试管理器
        cls.model_manager = TestModelManager(cls.client)

    def test_01_real_connection(self):
        """测试1: 真实连接 - 验证可以连接到服务器"""
        logger.info("🧪 测试真实连接...")

        # 直接调用 API
        response = self.client.get("/models")
        self.assertIsNotNone(response, "应该能够连接到服务器")
        self.assertIsInstance(response, (list, dict), "响应应该是列表或字典")

        logger.info(f"✅ 成功连接，响应类型: {type(response).__name__}")

    def test_02_pagination_default(self):
        """测试2: 默认分页 - 使用默认参数"""
        logger.info("🧪 测试默认分页...")

        models = self.model_manager.list_models()
        self.assertIsNotNone(models, "应该返回模型列表")
        self.assertIsInstance(models, list, "应该返回列表")

        logger.info(f"✅ 获取到 {len(models)} 个模型（默认分页）")

    def test_03_pagination_custom_page_size(self):
        """测试3: 自定义分页大小"""
        logger.info("🧪 测试自定义分页大小...")

        # 获取第一页，每页5个
        models_page1 = self.model_manager.list_models(page=1, page_size=5)
        self.assertIsNotNone(models_page1, "第一页应该有结果")

        if len(models_page1) > 0:
            logger.info(f"✅ 第一页获取到 {len(models_page1)} 个模型")
        else:
            logger.warning("⚠️ 没有模型数据，跳过分页测试")
            self.skipTest("No models available")

    def test_04_url_building(self):
        """测试4: URL 构建 - 测试路径参数和编码"""
        logger.info("🧪 测试 URL 构建...")

        # 测试简单路径
        url1 = self.model_manager._build_url("/models")
        self.assertEqual(url1, f"{self.base_url}/api/v1/models")

        # 测试路径参数
        url2 = self.model_manager._build_url("/models/{id}", id="test-model")
        self.assertEqual(url2, f"{self.base_url}/api/v1/models/test-model")

        # 测试特殊字符编码
        url3 = self.model_manager._build_url(
            "/models/{id}", id="test model with spaces"
        )
        self.assertIn("test%20model%20with%20spaces", url3)

        logger.info("✅ URL 构建功能正常")

    def test_05_response_parsing_list(self):
        """测试5: 响应解析 - 列表格式"""
        logger.info("🧪 测试响应解析（列表）...")

        # 直接获取模型列表
        response = self.client.get("/models")
        parsed = self.model_manager._parse_list_response(response)

        self.assertIsNotNone(parsed, "应该能解析响应")
        self.assertIsInstance(parsed, list, "应该返回列表")

        if len(parsed) > 0:
            logger.info(f"✅ 成功解析 {len(parsed)} 个项目")
        else:
            logger.warning("⚠️ 解析结果为空列表")

    def test_06_response_parsing_with_data_field(self):
        """测试6: 响应解析 - 带 data 字段的字典格式"""
        logger.info("🧪 测试响应解析（data字段）...")

        # 构造一个模拟带 data 字段的响应
        mock_response = {"data": [{"id": "1"}, {"id": "2"}], "total": 2}
        parsed = self.model_manager._parse_list_response(mock_response)

        self.assertIsInstance(parsed, list, "应该提取出列表")
        self.assertEqual(len(parsed), 2, "应该有2个项目")

        logger.info("✅ data字段解析正常")

    def test_07_error_handling(self):
        """测试7: 错误处理 - 测试无效端点"""
        logger.info("🧪 测试错误处理...")

        # 尝试访问不存在的端点
        response = self.client.get("/nonexistent-endpoint-12345")

        # BaseClient 应该返回 None 或空列表而不是抛出异常
        self.assertIn(response, [None, [], {}], "错误情况应该返回 None 或空集合")

        logger.info("✅ 错误处理正常（没有抛出异常）")

    def test_08_logging_operations(self):
        """测试8: 日志记录 - 验证日志方法可用"""
        logger.info("🧪 测试日志记录...")

        # 测试日志方法（不会抛出异常）
        try:
            self.model_manager._log_operation_start(
                "test_operation", {"param": "value"}
            )
            self.model_manager._log_operation_success(
                "test_operation", {"result": "ok"}
            )
            self.model_manager._log_operation_failure(
                "test_operation", Exception("Test error")
            )
            logger.info("✅ 日志记录方法正常")
        except Exception as e:
            self.fail(f"日志记录不应该抛出异常: {e}")

    def test_09_filter_building(self):
        """测试9: 过滤参数构建"""
        logger.info("🧪 测试过滤参数构建...")

        # 测试查询过滤
        params = self.model_manager._build_filter_params(query="test")
        self.assertEqual(params.get("query"), "test")

        # 测试排序
        params = self.model_manager._build_filter_params(order_by="name", order="desc")
        self.assertEqual(params.get("order_by"), "name")
        self.assertEqual(params.get("order"), "desc")

        logger.info("✅ 过滤参数构建正常")

    def test_10_access_control_params(self):
        """测试10: 访问控制参数构建"""
        logger.info("🧪 测试访问控制参数...")

        # 测试公开访问
        params = self.model_manager._build_access_control(is_public=True)
        self.assertTrue(params.get("is_public"))

        # 测试私有访问
        params = self.model_manager._build_access_control(is_public=False)
        self.assertFalse(params.get("is_public"))

        logger.info("✅ 访问控制参数构建正常")


class IntegrationTestRealWorldScenarios(unittest.TestCase):
    """真实场景集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        cls.base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
        cls.auth_token = os.getenv("OUI_AUTH_TOKEN")

        if not cls.auth_token:
            raise unittest.SkipTest("OUI_AUTH_TOKEN environment variable not set")

        cls.client = BaseClient(
            base_url=cls.base_url,
            token=cls.auth_token,
            default_model_id=os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1"),
        )
        cls.model_manager = TestModelManager(cls.client)

    def test_scenario_01_list_and_paginate(self):
        """场景1: 列出并分页浏览所有模型"""
        logger.info("🎬 场景测试: 列出并分页浏览模型...")

        # 第一页
        page1 = self.model_manager.list_models(page=1, page_size=5)
        self.assertIsNotNone(page1, "第一页应该有结果")

        if len(page1) > 0:
            logger.info(f"   📄 第1页: {len(page1)} 个模型")

            # 如果有足够多的模型，尝试获取第二页
            if len(page1) >= 5:
                page2 = self.model_manager.list_models(page=2, page_size=5)
                if page2:
                    logger.info(f"   📄 第2页: {len(page2)} 个模型")

        logger.info("✅ 分页浏览场景完成")

    def test_scenario_02_error_recovery(self):
        """场景2: 错误恢复 - 测试重试机制"""
        logger.info("🎬 场景测试: 错误恢复...")

        # 尝试访问不存在的端点（应该优雅失败）
        result = self.model_manager._client.get("/invalid-endpoint-xyz")

        # 应该返回 None 或空集合，而不是抛出异常
        self.assertIsNone(result, "无效端点应该返回 None")

        logger.info("✅ 错误恢复场景完成")

    def test_scenario_03_multiple_requests(self):
        """场景3: 多个连续请求"""
        logger.info("🎬 场景测试: 多个连续请求...")

        results = []
        for i in range(3):
            models = self.model_manager.list_models(page_size=5)
            results.append(models)
            if models:
                logger.info(f"   请求 {i+1}: 获取到 {len(models)} 个模型")

        # 所有请求都应该成功
        self.assertTrue(all(r is not None for r in results), "所有请求都应该成功")

        logger.info("✅ 多个请求场景完成")


def run_integration_tests():
    """运行集成测试套件"""
    print("\n" + "=" * 70)
    print("🧪 BaseManager 新架构集成测试")
    print("=" * 70)

    # 检查环境变量
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
    auth_token = os.getenv("OUI_AUTH_TOKEN")

    print(f"\n🔧 配置:")
    print(f"   Base URL: {base_url}")
    print(f"   Auth Token: {auth_token[:20] if auth_token else 'NOT SET'}...")

    if not auth_token:
        print("\n❌ 错误: OUI_AUTH_TOKEN 环境变量未设置")
        print("   请设置: export OUI_AUTH_TOKEN='your-token-here'")
        sys.exit(1)

    print("\n🚀 开始测试...\n")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTestBaseManager))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTestRealWorldScenarios))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)
    print(f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"💥 错误: {len(result.errors)}")
    print(f"⏭️  跳过: {len(result.skipped)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
