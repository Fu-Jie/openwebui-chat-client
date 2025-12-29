# 安装指南

本指南介绍 `openwebui-chat-client` 及其依赖项的安装。

---

## 系统要求

- **Python**: 3.8 或更高版本
- **Open WebUI**: 运行中的 Open WebUI 实例，并具有 API 访问权限

---

## 安装

### 从 PyPI 安装（推荐）

使用 pip 安装 `openwebui-chat-client` 是最简单的方式：

```bash
pip install openwebui-chat-client
```

### 从源码安装

如果您想安装最新的开发版本：

```bash
git clone https://github.com/Fu-Jie/openwebui-chat-client.git
cd openwebui-chat-client
pip install -e .
```

### 安装测试依赖

如果您计划运行测试：

```bash
pip install openwebui-chat-client[test]
```

---

## 依赖项

软件包具有以下核心依赖项（自动安装）：

| 软件包 | 用途 |
|--------|------|
| `requests` | 同步 API 调用的 HTTP 客户端 |
| `httpx` | 异步 API 调用的 HTTP 客户端 |
| `python-dotenv` | 环境变量管理 |

### 可选依赖项

| 软件包 | 用途 | 安装方式 |
|--------|------|----------|
| `responses` | 测试用 HTTP 模拟 | `pip install openwebui-chat-client[test]` |

---

## 配置

### 环境变量

您可以使用环境变量配置客户端：

```bash
# 必需
export OUI_BASE_URL="http://localhost:3000"
export OUI_AUTH_TOKEN="your-bearer-token"

# 可选
export OUI_DEFAULT_MODEL="gpt-4.1"
```

### 使用 `.env` 文件

在项目根目录创建 `.env` 文件：

```ini
OUI_BASE_URL=http://localhost:3000
OUI_AUTH_TOKEN=your-bearer-token
OUI_DEFAULT_MODEL=gpt-4.1
```

客户端将使用 `python-dotenv` 自动加载这些变量。

---

## 验证安装

安装后，验证软件包是否正确安装：

```python
from openwebui_chat_client import OpenWebUIClient

# 检查版本
import openwebui_chat_client
print(f"版本: {openwebui_chat_client.__version__}")

# 测试连接
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-bearer-token",
    default_model_id="gpt-4.1"
)

# 列出可用模型以验证连接
models = client.list_models()
if models:
    print(f"已连接！找到 {len(models)} 个模型。")
else:
    print("连接失败或没有可用模型。")
```

---

## 故障排除

### 常见问题

#### `ModuleNotFoundError: No module named 'openwebui_chat_client'`

确保软件包已安装在当前 Python 环境中：

```bash
pip list | grep openwebui-chat-client
```

#### 连接错误

1. 验证您的 Open WebUI 实例正在运行
2. 检查 `base_url` 是否正确
3. 确保您的 API 令牌有效

#### SSL 证书错误

如果您连接的服务器使用自签名证书：

```python
client = AsyncOpenWebUIClient(
    base_url="https://your-server:3000",
    token="your-token",
    default_model_id="gpt-4.1",
    verify=False  # 禁用 SSL 验证（不建议在生产环境使用）
)
```

---

## 下一步

- [用户指南](usage.zh.md) - 学习如何使用客户端
- [API 参考](api.zh.md) - 探索完整的 API
