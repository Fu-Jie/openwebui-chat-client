
### 2. 解决方案文档化

#### 问题描述标准

- **症状描述**: 清晰描述用户遇到的现象
- **错误信息**: 提供具体的错误消息示例
- **环境信息**: 说明问题发生的环境条件

#### 解决步骤格式

- **分步骤**: 将解决方案分解为可操作的步骤
- **代码示例**: 提供具体的代码修复示例
- **验证方法**: 说明如何验证问题是否解决

### 3. 预防性文档

#### 最佳实践指导

- **配置建议**: 推荐的配置和设置方式
- **使用模式**: 推荐的API使用模式和反模式
- **性能优化**: 提高性能和稳定性的建议

#### 注意事项

- **限制说明**: 明确API的限制和约束
- **兼容性**: 说明版本兼容性和升级注意事项
- **安全建议**: 关于API密钥和数据安全的指导

---

## 示例代码开发规范

### 1. 示例目录结构

#### 目录组织

```
examples/
├── README.md                     # 示例总览和使用指南
├── config/                       # 配置和环境设置
│   ├── basic_config.py          # 基础客户端配置
│   └── environment_setup.py     # 环境变量设置指南
├── getting_started/              # 入门示例
│   ├── hello_world.py           # 最简单的使用示例
│   ├── basic_chat.py            # 基础聊天功能
│   └── quick_start.py           # 快速开始指南
├── chat_features/                # 聊天功能示例
│   ├── streaming_chat.py        # 流式聊天
│   ├── parallel_chat.py         # 并行多模型聊天
│   ├── follow_up_suggestions.py # 后续建议功能
│   ├── chat_with_images.py      # 多模态聊天
│   └── chat_management.py       # 聊天管理功能
├── rag_knowledge/                # RAG和知识库示例
│   ├── file_rag.py              # 文件RAG
│   ├── knowledge_base.py        # 知识库管理
│   ├── batch_knowledge_ops.py   # 批量知识库操作
│   └── advanced_rag.py          # 高级RAG功能
├── model_management/             # 模型管理示例
│   ├── list_models.py           # 列出可用模型
│   ├── model_operations.py      # 模型CRUD操作
│   └── model_switching.py       # 模型切换
├── notes_api/                    # 笔记API示例
│   ├── basic_notes.py           # 基础笔记操作
│   └── advanced_notes.py        # 高级笔记管理
├── advanced_features/            # 高级功能示例
│   ├── real_time_streaming.py   # 实时流式更新
│   ├── concurrent_operations.py # 并发操作
│   ├── error_handling.py        # 错误处理模式
│   └── custom_tools.py          # 自定义工具使用
├── comprehensive/                # 综合示例
│   ├── full_demo.py             # 全功能演示
│   └── use_case_scenarios.py    # 实际用例场景
└── utils/                        # 工具和辅助函数
    ├── example_base.py          # 示例基类
    ├── file_helpers.py          # 文件操作辅助
    └── test_data.py             # 测试数据生成
```

### 2. 示例代码标准

#### 文件结构模板

每个示例文件都应遵循以下模板结构：

```python
#!/usr/bin/env python3
"""
示例功能的简要描述。

本示例演示的功能：
- 功能1
- 功能2
- 功能3

要求：
- 环境变量: OUI_BASE_URL
- 环境变量: OUI_AUTH_TOKEN
- 模型可用性: 特定模型（如果需要）

使用方法：
    python examples/category/example_name.py
"""

import logging
import os
from typing import Optional, Dict, Any

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# 日志设置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """演示示例功能的主函数。"""
    # 验证环境变量
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN 环境变量未设置")
        return
    
    # 客户端初始化
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ 客户端初始化成功")
    except Exception as e:
        logger.error(f"❌ 客户端初始化失败: {e}")
        return
    
    # 示例实现
    # ... 你的示例代码 ...
    
    logger.info("🎉 示例执行完成")


if __name__ == "__main__":
    main()
```

#### 命名规范

- **文件名**: 使用 `snake_case.py`，描述性命名
- **函数名**: 遵循 PEP 8，使用 `snake_case`
- **类名**: 使用 `PascalCase`
- **常量**: 使用 `UPPER_SNAKE_CASE`

#### 代码规范

- **导入顺序**: 标准库 → 第三方库 → 本地库
- **环境变量**: 统一的环境变量处理方式
- **错误处理**: 适当的异常处理和日志记录
- **类型提示**: 完整的类型注解
- **文档**: 清晰的docstring和注释

#### 文档规范

- **文件头部**: 功能描述、演示功能列表、要求、使用方法
- **函数文档**: 清晰的参数和返回值描述
- **注释**: 解释复杂逻辑的有意义注释
- **错误消息**: 用户友好的错误消息

### 3. 示例开发流程

#### 新示例开发

1. **需求分析**: 确定要演示的功能和目标用户
2. **分类放置**: 根据功能将示例放在合适的目录中
3. **遵循模板**: 使用标准模板结构
4. **功能实现**: 实现核心演示功能
5. **测试验证**: 确保示例可以正常运行
6. **文档更新**: 更新相关README和说明

#### 示例质量标准

- **可执行性**: 示例必须可以直接运行
- **教育性**: 代码清晰易懂，有教育价值
- **完整性**: 包含必要的错误处理和验证
- **一致性**: 遵循项目的代码风格和约定
- **实用性**: 演示真实的使用场景

### 4. 环境变量规范

#### 标准环境变量

所有示例都应支持以下环境变量：

```bash
# 必需
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your_api_token_here"

# 可选
export OUI_DEFAULT_MODEL="gpt-4.1"
export OUI_PARALLEL_MODELS="gpt-4.1,gemini-2.5-flash"
export OUI_RAG_MODEL="gemini-2.5-flash"
export OUI_MULTIMODAL_MODEL="gpt-4.1"
```

