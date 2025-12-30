# Documentation Development Guide

This guide explains how to develop and maintain the documentation site for `openwebui-chat-client`.

## Prerequisites

Install the documentation dependencies:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-static-i18n
```

## Local Development

### Build and Serve Locally

To preview the documentation locally:

```bash
mkdocs serve
```

This starts a local server at `http://127.0.0.1:8000/` with hot-reloading.

### Build for Production

To build the static site:

```bash
mkdocs build
```

The site will be generated in the `site/` directory.

### Build with Strict Mode

To build with strict mode (recommended before deployment):

```bash
mkdocs build --strict
```

This will fail on any warnings, helping catch issues early.

## Documentation Structure

The documentation supports English and Chinese (中文) languages using the `mkdocs-static-i18n` plugin.

```
docs/
├── index.md              # Homepage (English)
├── index.zh.md           # Homepage (Chinese)
├── installation.md       # Installation guide (English)
├── installation.zh.md    # Installation guide (Chinese)
├── usage.md              # User guide (English)
├── usage.zh.md           # User guide (Chinese)
├── api.md                # API reference (English)
├── api.zh.md             # API reference (Chinese)
├── github-pages-setup.md # GitHub Pages setup (English)
├── github-pages-setup.zh.md # GitHub Pages setup (Chinese)
├── DEVELOPMENT.md        # Development guide (English)
└── DEVELOPMENT.zh.md     # Development guide (Chinese)

mkdocs.yml                # MkDocs configuration (includes i18n settings)
```

### Multilingual File Naming Convention

- **English files**: `filename.md` (default language, no suffix)
- **Chinese files**: `filename.zh.md` (with `.zh` suffix)

### Documentation URLs

- **English**: `https://fu-jie.github.io/openwebui-chat-client/`
- **Chinese**: `https://fu-jie.github.io/openwebui-chat-client/zh/`

## GitHub Pages Deployment

### Automatic Deployment

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The GitHub Actions workflow (`.github/workflows/deploy.yml`) handles this.

### Required GitHub Repository Settings

To enable GitHub Pages deployment, configure the following settings in your repository:

1. **Enable GitHub Pages**
   - Go to **Settings** → **Pages**
   - Under **Build and deployment**, set **Source** to **GitHub Actions**
   - This allows the deployment workflow to publish directly

2. **Actions Permissions**
   - Go to **Settings** → **Actions** → **General**
   - Under **Workflow permissions**, select **Read and write permissions**
   - Check **Allow GitHub Actions to create and approve pull requests** (optional)

3. **Branch Protection (Optional)**
   - If you have branch protection rules on `main`, ensure the `github-actions[bot]` is allowed to push to the protected branch

### Manual Deployment (Optional)

If you need to deploy manually:

```bash
mkdocs gh-deploy --force
```

This builds the site and pushes it to the `gh-pages` branch.

## Adding New Pages

1. Create a new `.md` file in the `docs/` directory
2. Add the page to `mkdocs.yml` under the `nav` section:

```yaml
nav:
  - Home: index.md
  - Installation: installation.md
  - User Guide: usage.md
  - API Reference: api.md
  - New Page: new-page.md  # Add here
```

## API Documentation

The API reference (`docs/api.md`) uses [mkdocstrings](https://mkdocstrings.github.io/) to automatically generate documentation from Python docstrings.

### Documenting New Methods

When adding new public methods to the client:

1. Add proper docstrings following Google style:

```python
def new_method(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Short description of the method.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to None.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When an invalid parameter is provided.

    Example:
        ```python
        result = client.new_method("test")
        print(result)
        ```
    """
    pass
```

2. Add the method to the members list in `docs/api.md`:

```markdown
::: openwebui_chat_client.OpenWebUIClient
    options:
      members:
        - existing_method
        - new_method  # Add here
```

## Markdown Extensions

The documentation supports many Markdown extensions. See `mkdocs.yml` for the full list.

### Code Blocks with Syntax Highlighting

```python
client = OpenWebUIClient(
    base_url="http://localhost:3000",
    token="your-token",
    default_model_id="gpt-4.1"
)
```

### Admonitions

```markdown
!!! note
    This is a note.

!!! warning
    This is a warning.

!!! tip
    This is a tip.
```

### Tabbed Content

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

## Troubleshooting

### Common Issues

**Build fails with "strict" mode**

Check for:
- Broken links
- Missing files referenced in `nav`
- Syntax errors in Markdown

**API docs not showing**

Ensure:
- The package is installed: `pip install -e .`
- The module path is correct in `:::` directive
- The method is listed in the `members` option

**Pages not updating**

- Clear browser cache
- Check the GitHub Actions workflow logs
- Verify the deployment completed successfully

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/)

## Multilingual Documentation

### Adding Translations

When adding a new documentation page:

1. Create the English version: `docs/new-page.md`
2. Create the Chinese version: `docs/new-page.zh.md`
3. Update `mkdocs.yml` navigation if needed
4. Add navigation translations in `nav_translations` section

### Translation Guidelines

- Keep the document structure identical between languages
- Do not translate code blocks, file names, or command examples
- Maintain consistent terminology (see the terminology table in `.github/copilot-instructions.md`)
- Update internal links to point to the correct language version

### Testing Multilingual Build

```bash
# Build and verify both languages
mkdocs build --strict

# Preview locally
mkdocs serve
```

The English version is available at `http://localhost:8000/` and Chinese at `http://localhost:8000/zh/`.
