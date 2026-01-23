---
description: 自动生成单元测试代码
---

# Test Generation Skill

此 Skill 用于根据现有的 Python 方法代码，自动生成符合项目规范的单元测试代码。

## 输入格式

提供待测试的 Python 方法代码（包括同步和异步版本）。

## 处理逻辑

1. **分析方法**: 识别参数、返回值和可能的异常
2. **生成 Mock**: 针对 `requests` 或 `httpx` 生成 Mock 对象
3. **生成成功用例**: 模拟正常的 API 响应
4. **生成失败用例**: 模拟网络错误、4xx/5xx 响应
5. **生成边界用例**: 测试空参数、特殊字符等情况

## 输出示例

```python
# 针对 archive_chat 方法的测试
class TestArchiveChat(unittest.TestCase):
    def test_archive_chat_success(self):
        """Test successful chat archival."""
        # Setup
        self.mock_session.post.return_value.status_code = 200
        
        # Execute
        result = self.manager.archive_chat("chat123")
        
        # Verify
        self.assertTrue(result)
        self.mock_session.post.assert_called_once()

    def test_archive_chat_failure(self):
        """Test chat archival failure."""
        # Setup
        self.mock_session.post.side_effect = Exception("Network error")
        
        # Execute
        result = self.manager.archive_chat("chat123")
        
        # Verify
        self.assertFalse(result)
```

## 使用提示

- 如果方法包含复杂的逻辑分支，请明确指出需要覆盖的场景
- 说明是否需要测试参数验证逻辑
