# 代码覆盖率提升指南

## 📊 当前状态

- **当前覆盖率**: 50%
- **目标覆盖率**: 80%
- **需要提升**: 30个百分点

---

## 🎯 提升策略

### 阶段1：快速提升到60%（1-2周）

#### 1. 识别未覆盖的代码

**本地运行覆盖率分析**:
```bash
# 运行测试并生成覆盖率报告
coverage run -m pytest tests/ -v
coverage report --show-missing

# 生成HTML报告（更直观）
coverage html
open htmlcov/index.html  # macOS
# 或在浏览器打开 htmlcov/index.html
```

**查看未覆盖的文件**:
```bash
# 按覆盖率排序，找出最低的文件
coverage report --sort=cover
```

#### 2. 优先测试的模块

根据重要性和复杂度，优先为以下模块添加测试：

**高优先级**（核心功能）:
- ✅ `openwebui_chat_client.py` - 主客户端类
- ✅ `modules/chat_manager.py` - 聊天管理
- ⚠️ `modules/file_manager.py` - 文件管理（可能覆盖不足）
- ⚠️ `modules/knowledge_base_manager.py` - 知识库管理
- ⚠️ `core/base_client.py` - 基础HTTP客户端

**中优先级**（常用功能）:
- `modules/model_manager.py` - 模型管理
- `modules/notes_manager.py` - 笔记管理
- `modules/prompts_manager.py` - 提示词管理
- `modules/user_manager.py` - 用户管理

**低优先级**（辅助功能）:
- `async_*.py` - 异步客户端（如果不常用）
- 工具脚本和示例代码

#### 3. 快速提升技巧

**A. 测试简单的工具方法**

找出未测试的简单方法（getter、setter、工具函数）：

```python
# 例如：测试简单的属性访问
def test_client_properties():
    client = OpenWebUIClient(base_url, token, model)
    assert client.base_url == base_url
    assert client.default_model_id == model
    assert client.chat_id is None  # 初始状态
```

**B. 测试错误处理路径**

很多未覆盖的代码是错误处理分支：

```python
def test_method_with_invalid_input():
    client = OpenWebUIClient(base_url, token, model)
    
    # 测试空输入
    result = client.some_method(None)
    assert result is None
    
    # 测试无效输入
    result = client.some_method("")
    assert result is None
```

**C. 测试边界条件**

```python
def test_method_edge_cases():
    # 空列表
    result = client.batch_operation([])
    assert result == {}
    
    # 单个元素
    result = client.batch_operation(["item1"])
    assert len(result) == 1
    
    # 大量元素
    result = client.batch_operation([f"item{i}" for i in range(100)])
    assert len(result) == 100
```

---

### 阶段2：提升到70%（2-3周）

#### 4. 测试复杂的业务逻辑

**A. 多步骤流程测试**

```python
def test_complete_chat_workflow():
    """测试完整的聊天工作流"""
    client = OpenWebUIClient(base_url, token, model)
    
    # 1. 创建聊天
    result = client.chat("Hello", chat_title="Test")
    assert result is not None
    chat_id = result['chat_id']
    
    # 2. 继续对话
    result = client.chat("How are you?")
    assert result['chat_id'] == chat_id
    
    # 3. 切换模型
    success = client.switch_chat_model("new-model")
    assert success
    
    # 4. 添加标签
    client.set_chat_tags(["test", "automated"])
    
    # 5. 重命名
    client.rename_chat(chat_id, "Updated Title")
```

**B. 异常场景测试**

```python
def test_network_failure_handling():
    """测试网络故障处理"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        client = OpenWebUIClient(base_url, token, model)
        result = client.chat("Hello")
        
        assert result is None  # 应该优雅地处理失败
```

**C. 并发场景测试**

```python
def test_parallel_operations():
    """测试并发操作"""
    client = OpenWebUIClient(base_url, token, model)
    
    results = client.parallel_chat(
        question="Test",
        model_ids=["model1", "model2", "model3"]
    )
    
    assert len(results) == 3
    assert all(r is not None for r in results.values())
```

#### 5. 测试集成场景

```python
def test_rag_with_knowledge_base():
    """测试RAG与知识库集成"""
    client = OpenWebUIClient(base_url, token, model)
    
    # 创建知识库
    kb = client.create_knowledge_base("test_kb", files=["doc.pdf"])
    
    # 使用知识库进行聊天
    result = client.chat(
        question="What's in the document?",
        rag_knowledge_bases=[kb['id']]
    )
    
    assert result is not None
    assert 'response' in result
```

---

### 阶段3：达到80%（3-4周）

#### 6. 覆盖剩余的边缘情况

**A. 异步代码测试**

```python
import pytest

@pytest.mark.asyncio
async def test_async_client_operations():
    """测试异步客户端"""
    async_client = AsyncOpenWebUIClient(base_url, token, model)
    
    result = await async_client.chat("Hello")
    assert result is not None
    
    await async_client.close()
```

**B. 配置和初始化测试**

```python
def test_client_initialization_variants():
    """测试各种初始化方式"""
    # 最小配置
    client1 = OpenWebUIClient(base_url, token)
    
    # 完整配置
    client2 = OpenWebUIClient(
        base_url=base_url,
        token=token,
        default_model_id=model,
        timeout=60,
        max_retries=5
    )
    
    # 从环境变量
    with patch.dict(os.environ, {
        'OUI_BASE_URL': base_url,
        'OUI_AUTH_TOKEN': token
    }):
        client3 = OpenWebUIClient.from_env()
```

**C. 数据转换和格式化测试**

```python
def test_data_formatting():
    """测试数据格式化方法"""
    client = OpenWebUIClient(base_url, token, model)
    
    # 测试历史记录格式化
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    formatted = client._build_linear_history_for_api(history)
    assert len(formatted) == 2
    
    # 测试图片编码
    image_data = client._encode_image_to_base64("test.jpg")
    assert image_data.startswith("data:image/")
```

---

## 🛠️ 实用工具和技巧

### 1. 使用覆盖率报告找出未测试代码

```bash
# 生成详细报告
coverage report -m

# 输出示例：
# Name                                    Stmts   Miss  Cover   Missing
# ---------------------------------------------------------------------
# openwebui_chat_client/core/base.py       150     75    50%   45-67, 89-120
# openwebui_chat_client/modules/chat.py    300    120    60%   234-267, 345-389
```

**Missing列显示未覆盖的行号**，直接去这些行添加测试！

### 2. 使用HTML报告可视化

```bash
coverage html
open htmlcov/index.html
```

HTML报告会：
- 用红色高亮未覆盖的代码
- 显示每个文件的覆盖率
- 提供交互式浏览

### 3. 测试模板

创建 `tests/test_template.py`:

```python
"""测试模板 - 复制此文件开始新测试"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from openwebui_chat_client import OpenWebUIClient

class TestNewFeature(unittest.TestCase):
    """测试新功能"""
    
    def setUp(self):
        """每个测试前运行"""
        self.base_url = "http://localhost:3000"
        self.token = "test-token"
        self.model = "test-model"
        self.client = OpenWebUIClient(
            self.base_url, 
            self.token, 
            self.model
        )
    
    def tearDown(self):
        """每个测试后运行"""
        pass
    
    @patch('requests.post')
    def test_feature_success(self, mock_post):
        """测试功能成功场景"""
        # 设置mock返回值
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "success": True,
            "data": "test"
        }
        
        # 调用被测试的方法
        result = self.client.some_method("input")
        
        # 断言
        self.assertIsNotNone(result)
        self.assertEqual(result['data'], "test")
        
        # 验证mock被正确调用
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_feature_failure(self, mock_post):
        """测试功能失败场景"""
        mock_post.side_effect = Exception("Network error")
        
        result = self.client.some_method("input")
        
        self.assertIsNone(result)
```

### 4. 批量生成测试

创建脚本 `scripts/generate_tests.py`:

```python
#!/usr/bin/env python3
"""为未测试的方法生成测试骨架"""
import ast
import os

def find_untested_methods(source_file, test_file):
    """找出未测试的方法"""
    # 解析源文件，提取所有公共方法
    with open(source_file) as f:
        tree = ast.parse(f.read())
    
    methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):
                methods.append(node.name)
    
    # 解析测试文件，提取已测试的方法
    if os.path.exists(test_file):
        with open(test_file) as f:
            test_content = f.read()
        tested = [m for m in methods if f"test_{m}" in test_content]
    else:
        tested = []
    
    # 返回未测试的方法
    return [m for m in methods if m not in tested]

def generate_test_skeleton(method_name):
    """生成测试骨架"""
    return f"""
    def test_{method_name}_success(self):
        \"\"\"测试 {method_name} 成功场景\"\"\"
        # TODO: 实现测试
        pass
    
    def test_{method_name}_failure(self):
        \"\"\"测试 {method_name} 失败场景\"\"\"
        # TODO: 实现测试
        pass
"""

# 使用示例
untested = find_untested_methods(
    "openwebui_chat_client/modules/chat_manager.py",
    "tests/test_chat_functionality.py"
)

for method in untested:
    print(generate_test_skeleton(method))
```

---

## 📈 进度追踪

### 每周检查覆盖率

```bash
# 创建覆盖率追踪脚本
cat > scripts/track_coverage.sh << 'EOF'
#!/bin/bash
coverage run -m pytest tests/ -v
COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
echo "$(date +%Y-%m-%d): $COVERAGE%" >> coverage_history.txt
echo "当前覆盖率: $COVERAGE%"
EOF

chmod +x scripts/track_coverage.sh
```

### 设置里程碑

在 `pyproject.toml` 中逐步提升阈值：

```toml
# 第1周
[tool.coverage.report]
fail_under = 50

# 第2周
fail_under = 55

# 第3周
fail_under = 60

# ... 逐步提升到80
```

---

## 🎯 最佳实践

### 1. 测试驱动开发（TDD）

新功能开发时：
1. 先写测试（会失败）
2. 实现功能（测试通过）
3. 重构代码（测试仍通过）

### 2. 代码审查时检查测试

PR审查清单：
- [ ] 新代码有对应的测试
- [ ] 测试覆盖了正常和异常场景
- [ ] 覆盖率没有下降

### 3. 持续监控

在CI中：
```yaml
- name: Check coverage trend
  run: |
    CURRENT=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
    echo "Coverage: $CURRENT%"
    if [ "$CURRENT" -lt 50 ]; then
      echo "❌ Coverage dropped below 50%"
      exit 1
    fi
```

---

## 🚀 快速行动计划

### 本周（第1周）

1. **周一**: 运行覆盖率报告，识别最低覆盖率的5个文件
2. **周二-周三**: 为这5个文件添加基础测试（目标：每个文件+10%）
3. **周四**: 测试错误处理路径
4. **周五**: 测试边界条件，提交PR

**目标**: 覆盖率从50%提升到55%

### 下周（第2周）

1. 为中等复杂度的方法添加测试
2. 测试集成场景
3. 添加并发测试

**目标**: 覆盖率从55%提升到65%

### 第3-4周

1. 覆盖剩余的边缘情况
2. 添加异步代码测试
3. 完善文档和示例

**目标**: 覆盖率达到80%

---

## 📚 参考资源

- [Coverage.py 文档](https://coverage.readthedocs.io/)
- [pytest 最佳实践](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python unittest.mock 指南](https://docs.python.org/3/library/unittest.mock.html)
- [测试驱动开发](https://en.wikipedia.org/wiki/Test-driven_development)

---

**记住**: 覆盖率是手段，不是目的。重要的是测试质量，而不仅仅是数量！

**创建日期**: 2025-01-09  
**维护者**: openwebui-chat-client 团队
