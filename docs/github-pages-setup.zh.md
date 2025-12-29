# GitHub Pages 设置指南

本指南说明如何为 openwebui-chat-client 文档设置 GitHub Pages。

## 前提条件

- 具有启用 GitHub Pages 的仓库管理员访问权限
- `docs/` 目录中的文档文件
- `mkdocs.yml` 配置文件

## 分步设置

### 1. 启用 GitHub Pages

1. 导航到您的仓库设置页面：
   ```
   https://github.com/Fu-Jie/openwebui-chat-client/settings/pages
   ```

2. 在 **"构建和部署"** 部分：
   - **来源**：选择 "GitHub Actions"
   - 这允许工作流直接部署到 GitHub Pages

3. 如果进行了任何更改，请点击 **"保存"**

### 2. 验证工作流权限

部署工作流需要特定权限：

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

这些已在 `.github/workflows/deploy.yml` 中配置。

### 3. 触发部署

当以下情况发生时，文档将自动部署：

- 您向 `main` 或 `master` 分支推送影响以下内容的更改：
  - `docs/` 目录中的文件
  - `mkdocs.yml` 文件
  - `openwebui_chat_client/` 中的 Python 客户端代码
  - 工作流文件本身

您也可以手动触发部署：

1. 转到 Actions 标签页
2. 选择 "Deploy Documentation" 工作流
3. 点击 "Run workflow"
4. 选择分支并点击 "Run workflow"

### 4. 访问您的文档

成功部署后，您的文档将在以下地址可用：

```
https://fu-jie.github.io/openwebui-chat-client/
```

## 故障排除

### 错误："HttpError: Not Found (404)"

**症状**：部署作业失败，显示：
```
Creating Pages deployment failed: HttpError: Not Found
Failed to create deployment (status: 404)
```

**解决方案**：
1. 验证仓库设置中已启用 GitHub Pages
2. 确保选择 "GitHub Actions" 作为来源
3. 检查您是否具有仓库的管理员访问权限

### 错误："Permission denied"

**症状**：工作流因权限错误而失败。

**解决方案**：
1. 验证工作流具有正确的权限
2. 检查仓库设置 → Actions → General → Workflow permissions
3. 确保启用了 "Read and write permissions"

### 构建成功但部署失败

**症状**：`build` 作业成功，但 `deploy` 作业失败。

**解决方案**：
1. 这通常表示 GitHub Pages 配置不正确
2. 按照上述 "启用 GitHub Pages" 部分的步骤操作
3. 确保选择 "GitHub Actions" 作为来源，而不是分支

### 文档未更新

**症状**：推送了更改但文档站点未更新。

**解决方案**：
1. 检查工作流是否被触发（Actions 标签页）
2. 验证您的更改是否影响了工作流触发器中列出的路径
3. 检查工作流日志中的任何构建错误
4. 尝试手动触发工作流

## 工作流详情

部署工作流由两个作业组成：

### 构建作业
- 检出仓库
- 设置 Python 3.11
- 安装 MkDocs 和依赖项
- 构建文档站点
- 将构建的站点作为工件上传

### 部署作业
- 从构建作业下载工件
- 使用官方 `deploy-pages` 操作部署到 GitHub Pages
- 在 `github-pages` 环境中运行

## 配置文件

- **工作流**：`.github/workflows/deploy.yml`
- **MkDocs 配置**：`mkdocs.yml`
- **文档源**：`docs/` 目录

## 最佳实践

1. **先在本地测试**：推送前，先在本地测试您的文档：
   ```bash
   pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-static-i18n
   mkdocs serve
   ```
   然后访问 `http://localhost:8000` 预览。

2. **使用 `--strict` 模式**：工作流使用 `mkdocs build --strict` 将警告视为错误。

3. **审查更改**：始终检查 Actions 标签页以确保部署成功。

4. **缓存依赖项**：工作流缓存 pip 依赖项以加快构建速度。

## 多语言支持

本项目使用 `mkdocs-static-i18n` 插件支持中英文双语文档：

- **英文版本**：`https://fu-jie.github.io/openwebui-chat-client/` (默认)
- **中文版本**：`https://fu-jie.github.io/openwebui-chat-client/zh/`

### 添加新的翻译页面

1. 创建带有 `.zh.md` 后缀的中文版本文件（例如：`index.md` → `index.zh.md`）
2. 翻译内容，保持结构一致
3. 确保内部链接指向正确的语言版本

## 其他资源

- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
- [MkDocs 文档](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocs-static-i18n 插件](https://ultrabug.github.io/mkdocs-static-i18n/)
