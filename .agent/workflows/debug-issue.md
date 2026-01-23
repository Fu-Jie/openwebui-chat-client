---
description: 问题调试和排查流程
---

# 问题调试流程

## 1. 问题复现

### 收集信息
1. 错误信息或异常堆栈
2. 使用的 Python 版本
3. 调用的方法和参数
4. 预期行为 vs 实际行为

### 设置调试日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 2. 本地复现

### 创建最小复现脚本
```python
from openwebui_chat_client import OpenWebUIClient

client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-token",
    default_model_id="your-model"
)

# 复现问题的代码
result = client.problematic_method(...)
print(result)
```

### 运行调试
// turbo
```bash
python debug_script.py
```

## 3. 检查常见问题

### 网络连接
// turbo
```bash
curl -I http://localhost:3000/api/v1/models
```

### 认证问题
```python
# 检查 token 是否有效
response = client._base_client.session.get(
    f"{client._base_client.base_url}/api/v1/models"
)
print(response.status_code)
```

### 环境变量
// turbo
```bash
echo $OUI_BASE_URL
echo $OUI_AUTH_TOKEN
echo $OUI_DEFAULT_MODEL
```

## 4. 单元测试验证

### 运行相关测试
// turbo
```bash
pytest tests/test_specific.py -v -s
```

### 添加失败用例测试
```python
def test_issue_reproduction(self):
    """测试问题复现"""
    # 添加能复现问题的测试用例
    pass
```

## 5. 修复验证

### 运行所有相关测试
// turbo
```bash
make test
```

### 运行集成测试
// turbo
```bash
python run_integration_tests.py --category basic_chat
```

## 6. 常见问题速查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 401 Unauthorized | Token 无效或过期 | 重新获取 API Token |
| 连接超时 | 网络问题或服务未启动 | 检查 base_url 和网络 |
| JSON 解析错误 | 响应格式变更 | 检查 API 版本兼容性 |
| 聊天不同步 | 状态管理问题 | 检查 chat_id 和 message 结构 |
