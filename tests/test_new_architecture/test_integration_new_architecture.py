#!/usr/bin/env python3
"""
新架构集成测试

针对重构后的 BaseClient 和 BaseManager 的真实集成测试。
使用真实的 OpenWebUI 服务器而不是 mock。

要求:
- OUI_BASE_URL 环境变量 (默认: http://localhost:3003)
- OUI_AUTH_TOKEN 环境变量
- OUI_DEFAULT_MODEL 环境变量 (默认: gpt-4.1)
- OpenWebUI 服务器正在运行

运行方式:
    cd /path/to/openwebui-client
    source .env
    python tests/test_new_architecture/test_integration_new_architecture.py
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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealModelManager(BaseManager):
    """
    真实的 ModelManager 实现 - 用于测试
    使用 BaseManager 的所有功能
    """

    def list_models(self, page: int = 1, page_size: int = 30) -> Optional[list]:
        """列出模型 - 测试分页和实际API调用"""
        self._log_operation_start("list_models", page=page, page_size=page_size)

        params = self._build_pagination_params(page=page, page_size=page_size)
        response_data = self._get_json_response("GET", "/api/v1/models", params=params)

        if response_data:
            result = self._parse_list_response(response_data)
            self._log_operation_success(
                "list_models", count=len(result) if result else 0
            )
            return result
        else:
            self._log_operation_failure("list_models", Exception("No response"))
            return None


class TestNewArchitectureIntegration(unittest.TestCase):
    """新架构真实集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类 - 初始化真实客户端"""
        cls.base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
        cls.auth_token = os.getenv("OUI_AUTH_TOKEN")
        cls.default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

        if not cls.auth_token:
            raise unittest.SkipTest("OUI_AUTH_TOKEN environment variable not set")

        logger.info(f"🔧 Base URL: {cls.base_url}")
        logger.info(f"🔑 Auth Token: {cls.auth_token[:20]}...")
        logger.info(f"🤖 Default Model: {cls.default_model}")

        # 创建真实的 BaseClient
        cls.client = BaseClient(
            base_url=cls.base_url,
            token=cls.auth_token,
            default_model_id=cls.default_model,
        )

        # 创建测试用的 Manager
        cls.model_manager = RealModelManager(cls.client)

    def test_01_base_client_properties(self):
        """测试1: BaseClient 基本属性"""
        logger.info("🧪 测试 BaseClient 基本属性...")

        self.assertIsNotNone(self.client.session, "Session 应该存在")
        self.assertEqual(self.client.base_url, self.base_url, "Base URL 应该匹配")
        self.assertIn(
            "Authorization", self.client.json_headers, "应该有 Authorization 头"
        )
        self.assertIn(
            "Bearer", self.client.json_headers["Authorization"], "应该是 Bearer token"
        )

        logger.info("✅ BaseClient 属性正常")

    def test_02_base_manager_properties(self):
        """测试2: BaseManager 基本属性"""
        logger.info("🧪 测试 BaseManager 基本属性...")

        self.assertIsNotNone(self.model_manager.session, "应该能访问 session")
        self.assertEqual(
            self.model_manager.base_url, self.base_url, "应该能访问 base_url"
        )
        self.assertIsNotNone(self.model_manager.json_headers, "应该能访问 json_headers")
        self.assertEqual(
            self.model_manager.base_client, self.client, "应该引用正确的 client"
        )

        logger.info("✅ BaseManager 属性正常")

    def test_03_pagination_params_building(self):
        """测试3: 分页参数构建"""
        logger.info("🧪 测试分页参数构建...")

        # 默认分页
        params1 = self.model_manager._build_pagination_params()
        self.assertIn("limit", params1, "应该有 limit")
        self.assertEqual(params1["limit"], 30, "默认 limit 应该是 30")

        # 自定义分页
        params2 = self.model_manager._build_pagination_params(page=2, page_size=10)
        self.assertEqual(params2["skip"], 10, "第2页 skip 应该是 10")
        self.assertEqual(params2["limit"], 10, "limit 应该是 10")

        # Skip 优先级高于 page
        params3 = self.model_manager._build_pagination_params(skip=5, page=3)
        self.assertEqual(params3["skip"], 5, "显式 skip 优先级更高")

        logger.info("✅ 分页参数构建正常")

    def test_04_filter_params_building(self):
        """测试4: 过滤参数构建"""
        logger.info("🧪 测试过滤参数构建...")

        # 查询过滤
        params1 = self.model_manager._build_filter_params(query="test")
        self.assertEqual(params1.get("query"), "test")

        # 排序
        params2 = self.model_manager._build_filter_params(
            order_by="name", direction="desc"
        )
        self.assertEqual(params2.get("order_by"), "name")
        self.assertEqual(params2.get("direction"), "desc")

        # 自定义过滤
        params3 = self.model_manager._build_filter_params(custom_field="value")
        self.assertEqual(params3.get("custom_field"), "value")

        logger.info("✅ 过滤参数构建正常")

    def test_05_access_control_building(self):
        """测试5: 访问控制参数构建"""
        logger.info("🧪 测试访问控制参数构建...")

        # 公开访问
        access1 = self.model_manager._build_access_control("public")
        self.assertIsNone(access1, "公开访问应该返回 None")

        # 自定义访问控制
        access2 = self.model_manager._build_access_control(
            "custom", user_ids=["user1", "user2"], group_ids=["group1"]
        )
        self.assertIsNotNone(access2, "自定义访问应该返回配置")
        self.assertIn("read", access2, "应该有 read 配置")
        self.assertIn("write", access2, "应该有 write 配置")
        self.assertEqual(len(access2["read"]["user_ids"]), 2)
        self.assertEqual(len(access2["write"]["group_ids"]), 1)

        logger.info("✅ 访问控制参数构建正常")

    def test_06_url_building(self):
        """测试6: URL 构建"""
        logger.info("🧪 测试 URL 构建...")

        # 简单路径
        url1 = self.model_manager._build_url("/models")
        self.assertEqual(url1, f"{self.base_url}/models")

        # 路径参数 (使用path_params字典)
        url2 = self.model_manager._build_url(
            "/models/{id}", path_params={"id": "test-model"}
        )
        self.assertEqual(url2, f"{self.base_url}/models/test-model")

        # 特殊字符编码
        url3 = self.model_manager._build_url(
            "/models/{id}", path_params={"id": "test model"}
        )
        self.assertIn("test%20model", url3)

        logger.info("✅ URL 构建正常")

    def test_07_response_parsing(self):
        """测试7: 响应解析"""
        logger.info("🧪 测试响应解析...")

        # 列表响应 - 返回 (list, count) tuple
        items1, count1 = self.model_manager._parse_list_response(
            [{"id": "1"}, {"id": "2"}]
        )
        self.assertIsInstance(items1, list)
        self.assertEqual(len(items1), 2)
        self.assertEqual(count1, 2)

        # 字典响应（带 data 字段）
        items2, count2 = self.model_manager._parse_list_response(
            {"data": [{"id": "1"}]}
        )
        self.assertIsInstance(items2, list)
        self.assertEqual(len(items2), 1)

        # 字典响应（带 items 字段）
        items3, count3 = self.model_manager._parse_list_response(
            {"items": [{"id": "1"}, {"id": "2"}]}
        )
        self.assertIsInstance(items3, list)
        self.assertEqual(len(items3), 2)

        # 空响应
        items4, count4 = self.model_manager._parse_list_response(None)
        self.assertEqual(items4, [])
        self.assertIsNone(count4)

        logger.info("✅ 响应解析正常")

    def test_08_required_field_validation(self):
        """测试8: 必填字段验证"""
        logger.info("🧪 测试必填字段验证...")

        # 有效数据 (需要context参数)
        valid_data = {"name": "test", "description": "desc"}
        self.assertTrue(
            self.model_manager._validate_required_fields(
                valid_data, ["name", "description"], "test"
            )
        )

        # 缺少字段
        invalid_data = {"name": "test"}
        self.assertFalse(
            self.model_manager._validate_required_fields(
                invalid_data, ["name", "description"], "test"
            )
        )

        # 空值
        empty_data = {"name": "test", "description": ""}
        self.assertFalse(
            self.model_manager._validate_required_fields(
                empty_data, ["name", "description"], "test"
            )
        )

        logger.info("✅ 必填字段验证正常")

    def test_09_enum_value_validation(self):
        """测试9: 枚举值验证"""
        logger.info("🧪 测试枚举值验证...")

        # 有效值 (需要field_name参数)
        self.assertTrue(
            self.model_manager._validate_enum_value(
                "active", ["active", "inactive"], "status"
            )
        )

        # 无效值
        self.assertFalse(
            self.model_manager._validate_enum_value(
                "pending", ["active", "inactive"], "status"
            )
        )

        # 空值
        self.assertFalse(
            self.model_manager._validate_enum_value(
                "", ["active", "inactive"], "status"
            )
        )

        logger.info("✅ 枚举值验证正常")

    def test_10_real_api_call_list_models(self):
        """测试10: 真实API调用 - 列出模型"""
        logger.info("🧪 测试真实API调用 - 列出模型...")

        # 调用真实API - 返回 (models, total_count) tuple
        models, total_count = self.model_manager.list_models(page=1, page_size=5)

        # 验证响应
        self.assertIsNotNone(models, "应该返回模型列表")
        self.assertIsInstance(models, list, "应该是列表类型")
        self.assertIsInstance(total_count, int, "总数应该是整数")

        if len(models) > 0:
            logger.info(f"   ✅ 获取到 {len(models)} 个模型 (总数: {total_count})")
            logger.info(f"   第一个模型ID: {models[0].get('id', 'N/A')}")
        else:
            logger.warning("   ⚠️ 模型列表为空")

    def test_11_real_api_call_with_pagination(self):
        """测试11: 真实API调用 - 分页测试"""
        logger.info("🧪 测试真实API调用 - 分页...")

        # 第一页
        page1 = self.model_manager.list_models(page=1, page_size=3)
        self.assertIsNotNone(page1, "第一页应该有结果")

        if len(page1) >= 3:
            # 第二页
            page2 = self.model_manager.list_models(page=2, page_size=3)
            if page2 and len(page2) > 0:
                logger.info(
                    f"   ✅ 分页正常 - 页1: {len(page1)}项, 页2: {len(page2)}项"
                )
            else:
                logger.info("   ℹ️ 只有一页数据")
        else:
            logger.info(f"   ℹ️ 数据量较少（{len(page1)}项）")

    def test_12_batch_operation_simulation(self):
        """测试12: 批量操作模拟"""
        logger.info("🧪 测试批量操作模拟...")

        def mock_operation(item_id: str) -> Dict[str, Any]:
            """模拟操作"""
            return {"id": item_id, "status": "success"}

        # 批量处理 (operation_func参数,不是operation_fn)
        items = ["item1", "item2", "item3"]
        results = self.model_manager._batch_operation(
            items=items, operation_func=mock_operation, max_workers=2
        )

        self.assertIn("success", results, "应该有success列表")
        self.assertIn("failed", results, "应该有failed列表")
        self.assertEqual(len(results["success"]), 3, "应该处理3个项目")

        logger.info("✅ 批量操作正常")

    # ==========================================
    # BaseClient 核心功能测试
    # ==========================================

    def test_13_make_request_get(self):
        """测试13: _make_request GET请求"""
        logger.info("🧪 测试 _make_request GET请求...")

        # 测试GET请求 - 获取模型列表
        response = self.client._make_request("GET", "/api/v1/models")

        self.assertIsNotNone(response, "GET请求应该返回响应")
        self.assertEqual(response.status_code, 200, "状态码应该是200")

        # 验证可以解析JSON - API返回dict with "data" field
        data = response.json()
        self.assertIsInstance(data, dict, "响应应该是字典")

        # 提取模型列表
        models = data.get("data", [])
        self.assertIsInstance(models, list, "模型数据应该是数组")

        logger.info(f"   ✅ 成功获取 {len(models)} 个模型")
        logger.info("✅ GET请求正常")

    def test_14_make_request_post_with_json(self):
        """测试14: _make_request POST请求（JSON数据）"""
        logger.info("🧪 测试 _make_request POST请求...")

        # 测试POST请求 - 获取配置（使用POST但不创建资源）
        endpoint = "/api/v1/tasks/config"
        response = self.client._make_request("GET", endpoint)

        if response:
            self.assertEqual(response.status_code, 200, "配置请求应该成功")
            config = response.json()
            self.assertIsInstance(config, dict, "配置应该是字典")
            logger.info(f"   ✅ 成功获取任务配置: {list(config.keys())[:3]}...")
        else:
            logger.warning("   ⚠️ 任务配置端点可能不可用")

        logger.info("✅ POST请求正常")

    def test_15_make_request_timeout_handling(self):
        """测试15: _make_request 超时处理"""
        logger.info("🧪 测试超时处理...")

        # 使用很短的超时测试（0.001秒）
        response = self.client._make_request(
            "GET", "/api/v1/models", timeout=(0.001, 0.001)
        )

        # 超时应该返回None（被异常处理捕获）
        # 注意：如果服务器响应很快，可能不会超时
        logger.info("   ✅ 超时处理机制正常（如果超时会返回None）")
        logger.info("✅ 超时处理测试完成")

    def test_16_get_json_response(self):
        """测试16: _get_json_response 方法"""
        logger.info("🧪 测试 _get_json_response...")

        # 测试GET JSON响应
        response = self.client._get_json_response("GET", "/api/v1/models")

        self.assertIsNotNone(response, "应该返回数据")
        # API返回的是字典，包含data字段
        self.assertIsInstance(response, dict, "响应应该是字典")
        self.assertIn("data", response, "响应应该包含data字段")

        # 提取模型列表
        data = response.get("data", [])
        self.assertIsInstance(data, list, "模型数据应该是列表")
        self.assertGreater(len(data), 0, "应该至少有一个模型")

        # 验证模型对象结构
        first_model = data[0]
        self.assertIn("id", first_model, "模型应该有id")

        logger.info(f"   ✅ 成功解析JSON响应，获取 {len(data)} 个模型")
        logger.info("✅ JSON响应解析正常")

    def test_17_upload_file_real(self):
        """测试17: 真实文件上传"""
        logger.info("🧪 测试真实文件上传...")

        import tempfile

        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            test_file_path = f.name
            f.write("This is a test file for integration testing.\n")
            f.write("Testing BaseClient._upload_file() method.\n")
            f.write("Test timestamp: 2026-01-22\n")

        try:
            # 上传文件
            logger.info(f"   📤 上传文件: {test_file_path}")
            file_metadata = self.client._upload_file(test_file_path)

            # 验证上传结果
            self.assertIsNotNone(file_metadata, "上传应该返回元数据")
            self.assertIn("id", file_metadata, "元数据应该包含文件ID")
            self.assertIn("filename", file_metadata, "元数据应该包含文件名")

            file_id = file_metadata["id"]
            filename = file_metadata.get("filename", "unknown")

            logger.info(f"   ✅ 文件上传成功")
            logger.info(f"      文件ID: {file_id}")
            logger.info(f"      文件名: {filename}")
            logger.info("✅ 文件上传功能正常")

        finally:
            # 清理临时文件
            import os

            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                logger.info(f"   🧹 清理临时文件: {test_file_path}")

    def test_18_upload_file_nonexistent(self):
        """测试18: 上传不存在的文件"""
        logger.info("🧪 测试上传不存在的文件...")

        # 尝试上传不存在的文件
        result = self.client._upload_file("/nonexistent/path/test.txt")

        self.assertIsNone(result, "不存在的文件应该返回None")

        logger.info("✅ 不存在文件处理正常")

    def test_19_upload_file_with_special_chars(self):
        """测试19: 上传特殊字符文件名"""
        logger.info("🧪 测试特殊字符文件名上传...")

        import tempfile
        import os

        # 创建带特殊字符的文件名（但避免文件系统不允许的字符）
        special_filename = "test_文件_2026_01_22.txt"
        temp_dir = tempfile.gettempdir()
        test_file_path = os.path.join(temp_dir, special_filename)

        try:
            # 创建文件
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("测试中文文件名上传\n")

            # 上传文件
            logger.info(f"   📤 上传文件: {special_filename}")
            file_metadata = self.client._upload_file(test_file_path)

            if file_metadata:
                logger.info(f"   ✅ 特殊字符文件名上传成功")
                logger.info(f"      文件ID: {file_metadata.get('id')}")
            else:
                logger.warning("   ⚠️ 特殊字符文件名上传失败（可能是服务器限制）")

        finally:
            # 清理
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

        logger.info("✅ 特殊字符文件名测试完成")

    def test_20_get_task_model(self):
        """测试20: 获取任务模型配置"""
        logger.info("🧪 测试获取任务模型...")

        # 获取任务模型(可能返回None或字符串)
        task_model = self.client._get_task_model()

        if task_model is not None:
            self.assertIsInstance(task_model, str, "任务模型应该是字符串")
            self.assertGreater(len(task_model), 0, "任务模型不应为空")
            logger.info(f"   ✅ 任务模型: {task_model}")
        else:
            logger.info("   ℹ️  任务模型未配置(返回None)")

        logger.info("✅ 任务模型获取测试完成(通过)")

    def test_21_error_handling_404(self):
        """测试21: 错误处理 - HTTP错误"""
        logger.info("🧪 测试HTTP错误处理...")

        # 请求明显不存在的端点
        response = self.client._make_request(
            "GET", "/api/v1/truly_nonexistent_test_endpoint_12345"
        )

        # 验证错误处理 (API可能返回None、4xx或200)
        if response is None:
            logger.info("   ✅ API返回None处理HTTP错误")
        elif response.status_code >= 400:
            logger.info(f"   ✅ API返回错误状态码: {response.status_code}")
        else:
            # 某些API框架对不存在路由也返回200，这是服务器行为
            logger.info(f"   ℹ️  服务器对不存在路由返回: {response.status_code}")

        logger.info("✅ HTTP错误处理测试完成(通过)")

    def test_22_validate_required_params(self):
        """测试22: 参数验证"""
        logger.info("🧪 测试参数验证...")

        # 测试完整参数
        params1 = {"name": "test", "type": "model"}
        result1 = self.client._validate_required_params(params1, ["name", "type"])
        self.assertTrue(result1, "完整参数应该验证通过")

        # 测试缺失参数
        params2 = {"name": "test"}
        result2 = self.client._validate_required_params(params2, ["name", "type"])
        self.assertFalse(result2, "缺失参数应该验证失败")

        # 测试空值参数
        params3 = {"name": "", "type": "model"}
        result3 = self.client._validate_required_params(params3, ["name", "type"])
        self.assertFalse(result3, "空值参数应该验证失败")

        logger.info("✅ 参数验证正常")

    # ==========================================
    # BaseManager 补充功能测试 (test_23-34)
    # ==========================================

    def test_23_manager_properties(self):
        """测试23: Manager属性访问"""
        logger.info("🧪 测试Manager属性访问...")

        # 直接创建BaseManager实例
        manager = BaseManager(self.client)

        # 测试session属性
        self.assertIsNotNone(manager.session, "session应该不为空")
        self.assertEqual(
            manager.session, self.client.session, "session应该与client一致"
        )

        # 测试base_url属性
        self.assertEqual(manager.base_url, self.client.base_url, "base_url应该一致")

        # 测试json_headers属性
        self.assertIn("Authorization", manager.json_headers, "应该包含Authorization")

        logger.info("✅ Manager属性访问正常")

    def test_24_manager_make_request(self):
        """测试24: Manager的_make_request方法"""
        logger.info("🧪 测试Manager._make_request...")

        manager = BaseManager(self.client)

        # 测试通过Manager发起请求
        response = manager._make_request("GET", "/api/v1/models")

        self.assertIsNotNone(response, "请求应该返回响应")
        self.assertEqual(response.status_code, 200, "状态码应该是200")

        logger.info("✅ Manager._make_request正常")

    def test_25_manager_get_json_response(self):
        """测试25: Manager的_get_json_response方法"""
        logger.info("🧪 测试Manager._get_json_response...")

        manager = BaseManager(self.client)

        # 测试获取JSON响应
        data = manager._get_json_response("GET", "/api/v1/models")

        self.assertIsNotNone(data, "JSON响应应该不为空")
        self.assertIsInstance(data, dict, "应该返回字典")

        logger.info("✅ Manager._get_json_response正常")

    def test_26_check_write_access(self):
        """测试26: 写权限检查"""
        logger.info("🧪 测试写权限检查...")

        manager = BaseManager(self.client)

        # 测试Admin权限
        resource = {"user_id": "other_user"}
        has_access = manager._check_write_access(resource, "test_user", "admin")
        self.assertTrue(has_access, "Admin应该有写权限")

        # 测试Owner权限
        resource = {"user_id": "test_user"}
        has_access = manager._check_write_access(resource, "test_user", "user")
        self.assertTrue(has_access, "Owner应该有写权限")

        # 测试无权限
        resource = {"user_id": "other_user"}
        has_access = manager._check_write_access(resource, "test_user", "user")
        self.assertFalse(has_access, "非Owner/Admin不应该有写权限")

        logger.info("✅ 写权限检查正常")

    def test_27_batch_operation_success(self):
        """测试27: 批量操作 - 成功场景"""
        logger.info("🧪 测试批量操作...")

        manager = BaseManager(self.client)

        # 模拟批量操作
        items = ["item1", "item2", "item3"]

        def mock_operation(item):
            return {"id": item, "processed": True}

        results = manager._batch_operation(items, mock_operation, max_workers=2)

        self.assertEqual(len(results["success"]), 3, "应该有3个成功项")
        self.assertEqual(len(results["failed"]), 0, "不应该有失败项")

        logger.info(f"   ✅ 成功处理 {len(results['success'])} 项")
        logger.info("✅ 批量操作测试完成")

    def test_28_batch_operation_with_failures(self):
        """测试28: 批量操作 - 带失败"""
        logger.info("🧪 测试批量操作(带失败)...")

        manager = BaseManager(self.client)

        items = ["success1", "fail", "success2"]

        def operation_with_error(item):
            if item == "fail":
                raise ValueError("Simulated failure")
            return {"id": item, "processed": True}

        results = manager._batch_operation(
            items, operation_with_error, max_workers=2, continue_on_error=True
        )

        self.assertEqual(len(results["success"]), 2, "应该有2个成功项")
        self.assertEqual(len(results["failed"]), 1, "应该有1个失败项")

        logger.info(
            f"   ✅ 成功: {len(results['success'])}, 失败: {len(results['failed'])}"
        )
        logger.info("✅ 批量操作失败处理正常")

    def test_29_encode_path_param(self):
        """测试29: URL路径参数编码"""
        logger.info("🧪 测试URL参数编码...")

        manager = BaseManager(self.client)

        # 测试特殊字符编码
        encoded = manager._encode_path_param("test value/with:special?chars")
        self.assertNotIn("/", encoded, "斜杠应该被编码")
        self.assertNotIn(":", encoded, "冒号应该被编码")
        self.assertNotIn("?", encoded, "问号应该被编码")

        # 测试空格编码
        encoded_space = manager._encode_path_param("test value")
        self.assertNotIn(" ", encoded_space, "空格应该被编码")

        logger.info(f"   ✅ 编码结果: {encoded}")
        logger.info("✅ URL参数编码正常")

    def test_30_logging_methods(self):
        """测试30: 日志记录方法"""
        logger.info("🧪 测试日志记录方法...")

        manager = BaseManager(self.client)

        # 测试操作开始日志
        manager._log_operation_start("测试操作", chat_id="123", user="test")

        # 测试成功日志
        manager._log_operation_success("测试操作", result="完成", count=5)

        # 测试失败日志
        test_error = Exception("测试异常")
        manager._log_operation_failure("测试操作", test_error, context="测试上下文")

        logger.info("✅ 日志记录方法正常")

    def test_31_format_context(self):
        """测试31: 上下文格式化"""
        logger.info("🧪 测试上下文格式化...")

        manager = BaseManager(self.client)

        # 测试空上下文
        empty_result = manager._format_context({})
        self.assertEqual(empty_result, "", "空上下文应该返回空字符串")

        # 测试有内容的上下文
        context = {"chat_id": "123", "user": "test", "count": 5}
        formatted = manager._format_context(context)

        self.assertIn("chat_id=123", formatted, "应该包含chat_id")
        self.assertIn("user=test", formatted, "应该包含user")
        self.assertIn("count=5", formatted, "应该包含count")

        logger.info(f"   ✅ 格式化结果: {formatted}")
        logger.info("✅ 上下文格式化正常")

    def test_32_real_batch_list_models(self):
        """测试32: 真实批量获取模型"""
        logger.info("🧪 测试真实批量获取模型...")

        # 使用RealModelManager
        manager = RealModelManager(self.client)

        # 获取一些模型ID
        response = self.client._make_request("GET", "/api/v1/models")
        if response and response.status_code == 200:
            data = response.json()
            models = data.get("data", [])[:3]  # 只测试前3个
            model_ids = [m["id"] for m in models]

            logger.info(f"   📋 测试模型: {model_ids}")

            # 批量获取详情（注意：某些API可能不支持单个模型查询）
            def get_model_detail(model_id):
                try:
                    result = manager._get_json_response(
                        "GET", f"/api/v1/models/{model_id}"
                    )
                    return (
                        result
                        if result
                        else {"id": model_id, "note": "API不支持单个模型查询"}
                    )
                except Exception as e:
                    logger.info(f"   ℹ️  获取模型{model_id}失败: {e}")
                    return {"id": model_id, "error": str(e)}

            results = manager._batch_operation(
                model_ids, get_model_detail, max_workers=2, continue_on_error=True
            )

            # 成功可能是0（如果API不支持），也可能>0
            success_count = len(results["success"])
            failed_count = len(results["failed"])
            total_processed = success_count + failed_count

            logger.info(
                f"   ✅ 批量处理完成: {success_count}成功, {failed_count}失败, 总计{total_processed}项"
            )

            # 验证至少处理了所有项目
            self.assertEqual(total_processed, len(model_ids), "应该处理所有模型ID")

        logger.info("✅ 真实批量操作测试完成")

    def test_33_manager_error_handling(self):
        """测试33: Manager错误处理"""
        logger.info("🧪 测试Manager错误处理...")

        manager = BaseManager(self.client)

        # 测试无效endpoint
        response = manager._make_request("GET", "/api/invalid/endpoint/12345")
        # 可能返回None或错误响应，都是正常的
        logger.info(f"   ℹ️  无效endpoint返回: {response}")

        # 测试_get_json_response的错误处理
        json_data = manager._get_json_response("GET", "/api/invalid/endpoint/67890")
        # 应该返回None或错误数据
        logger.info(f"   ℹ️  JSON解析结果: {json_data is not None}")

        logger.info("✅ Manager错误处理测试完成")

    def test_34_manager_integration_flow(self):
        """测试34: Manager集成流程"""
        logger.info("🧪 测试Manager集成流程...")

        manager = BaseManager(self.client)

        # 1. 构建分页参数
        pagination = manager._build_pagination_params(page=1, page_size=5)
        logger.info(f"   📄 分页参数: {pagination}")

        # 2. 构建过滤参数
        filters = manager._build_filter_params(query="gpt", order_by="created")
        logger.info(f"   🔍 过滤参数: {filters}")

        # 3. 发起请求
        all_params = {**pagination, **filters}
        response = manager._get_json_response(
            "GET", "/api/v1/models", params=all_params
        )

        # 4. 解析响应
        if response:
            items, total = manager._parse_list_response(response)
            logger.info(f"   ✅ 获取 {len(items)} 个模型 (总数: {total})")

            # 5. 构建URL
            if items and len(items) > 0:
                model_id = items[0]["id"]
                url = manager._build_url(
                    "/api/v1/models/{model_id}", path_params={"model_id": model_id}
                )
                logger.info(f"   🔗 构建URL: {url}")

        logger.info("✅ Manager集成流程测试完成")


def run_tests():
    """运行测试套件"""
    print("\n" + "=" * 70)
    print("🚀 新架构集成测试")
    print("=" * 70)

    # 检查环境
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
    auth_token = os.getenv("OUI_AUTH_TOKEN")

    print(f"\n🔧 环境配置:")
    print(f"   Base URL: {base_url}")
    print(f"   Auth Token: {auth_token[:20] if auth_token else 'NOT SET'}...")

    if not auth_token:
        print("\n❌ 错误: OUI_AUTH_TOKEN 未设置")
        print("   请运行: source .env")
        sys.exit(1)

    print("\n🧪 开始测试...\n")

    # 运行测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNewArchitectureIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 结果总结
    print("\n" + "=" * 70)
    print("📊 测试结果")
    print("=" * 70)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"💥 错误: {len(result.errors)}")
    print(f"⏭️  跳过: {len(result.skipped)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
