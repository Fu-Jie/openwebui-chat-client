# 文档开发指南

本指南说明如何开发和维护 `openwebui-chat-client` 的文档站点。

## 前提条件

安装文档依赖项：

```bash
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-static-i18n
```

## 本地开发

### 本地构建和预览

在本地预览文档：

```bash
mkdocs serve
```

这将在 `http://127.0.0.1:8000/` 启动一个带有热重载功能的本地服务器。

### 生产环境构建

构建静态站点：

```bash
mkdocs build
```

站点将生成在 `site/` 目录中。

### 使用严格模式构建

使用严格模式构建（部署前推荐）：

```bash
mkdocs build --strict
```

这将在任何警告时失败，帮助及早发现问题。

## 文档结构

```
docs/
├── index.md              # 英文首页
├── index.zh.md           # 中文首页
├── installation.md       # 英文安装指南
├── installation.zh.md    # 中文安装指南
├── usage.md              # 英文用户指南
├── usage.zh.md           # 中文用户指南
├── api.md                # 英文 API 参考（自动生成）
├── api.zh.md             # 中文 API 参考（自动生成）
├── github-pages-setup.md # 英文 GitHub Pages 设置指南
├── github-pages-setup.zh.md # 中文 GitHub Pages 设置指南
├── DEVELOPMENT.md        # 英文开发指南
└── DEVELOPMENT.zh.md     # 中文开发指南

mkdocs.yml                # MkDocs 配置
```

## GitHub Pages 部署

### 自动部署

当更改推送到 `main` 分支时，文档会自动部署到 GitHub Pages。GitHub Actions 工作流（`.github/workflows/deploy.yml`）处理此过程。

### 必需的 GitHub 仓库设置

要启用 GitHub Pages 部署，请在仓库中配置以下设置：

1. **启用 GitHub Pages**
   - 转到 **Settings** → **Pages**
   - 在 **Build and deployment** 下，将 **Source** 设置为 **GitHub Actions**
   - 这允许部署工作流直接发布

2. **Actions 权限**
   - 转到 **Settings** → **Actions** → **General**
   - 在 **Workflow permissions** 下，选择 **Read and write permissions**
   - 勾选 **Allow GitHub Actions to create and approve pull requests**（可选）

3. **分支保护（可选）**
   - 如果您在 `main` 上有分支保护规则，请确保允许 `github-actions[bot]` 推送到受保护的分支

### 手动部署（可选）

如果需要手动部署：

```bash
mkdocs gh-deploy --force
```

这将构建站点并推送到 `gh-pages` 分支。

## 添加新页面

1. 在 `docs/` 目录中创建新的 `.md` 文件（英文和中文版本）
2. 将页面添加到 `mkdocs.yml` 的 `nav` 部分：

```yaml
nav:
  - Home: index.md
  - Installation: installation.md
  - User Guide: usage.md
  - API Reference: api.md
  - New Page: new-page.md  # 在此添加
```

## API 文档

API 参考（`docs/api.md` 和 `docs/api.zh.md`）使用 [mkdocstrings](https://mkdocstrings.github.io/) 从 Python 文档字符串自动生成文档。

### 记录新方法

向客户端添加新的公共方法时：

1. 使用 Google 风格添加适当的文档字符串：

```python
def new_method(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    方法的简短描述。

    如需要可添加更长的描述。

    Args:
        param1: param1 的描述。
        param2: param2 的描述。默认为 None。

    Returns:
        返回值的描述。

    Raises:
        ValueError: 当提供无效参数时。

    Example:
        >>> result = client.new_method("test")
        >>> print(result)
    """
    pass
```

2. 将方法添加到 `docs/api.md` 和 `docs/api.zh.md` 的成员列表中：

```markdown
::: openwebui_chat_client.OpenWebUIClient
    options:
      members:
        - existing_method
        - new_method  # 在此添加
```

## Markdown 扩展

文档支持许多 Markdown 扩展。完整列表请参见 `mkdocs.yml`。

### 带语法高亮的代码块

```python
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-token",
    default_model_id="gpt-4.1"
)
```

### 提示框

```markdown
!!! note "注意"
    这是一个注意事项。

!!! warning "警告"
    这是一个警告。

!!! tip "提示"
    这是一个提示。
```

### 标签式内容

```markdown
=== "Python"

    ```python
    print("Hello")
    ```

=== "JavaScript"

    ```javascript
    console.log("Hello");
    ```
```

## 多语言支持

本项目使用 `mkdocs-static-i18n` 插件实现中英文双语支持。

### 文件命名约定

- 英文版本：`filename.md`（默认）
- 中文版本：`filename.zh.md`

### 添加翻译

1. 为每个英文文档创建对应的 `.zh.md` 文件
2. 翻译内容，保持相同的结构和格式
3. 更新内部链接指向正确的语言版本

### 语言切换

站点会自动在导航栏显示语言切换器，用户可以在英文和中文版本之间切换。

## 故障排除

### 常见问题

**使用 "strict" 模式构建失败**

检查：
- 损坏的链接
- `nav` 中引用的缺失文件
- Markdown 语法错误

**API 文档未显示**

确保：
- 已安装软件包：`pip install -e .`
- `:::` 指令中的模块路径正确
- 方法已在 `members` 选项中列出

**页面未更新**

- 清除浏览器缓存
- 检查 GitHub Actions 工作流日志
- 验证部署是否成功完成

## 资源

- [MkDocs 文档](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/)
