# GitHub Pages Setup Guide

This guide explains how to set up GitHub Pages for the openwebui-chat-client documentation.

## Prerequisites

- Repository admin access to enable GitHub Pages
- Documentation files in the `docs/` directory
- `mkdocs.yml` configuration file

## Step-by-Step Setup

### 1. Enable GitHub Pages

1. Navigate to your repository's settings page:
   ```
   https://github.com/Fu-Jie/openwebui-chat-client/settings/pages
   ```

2. Under **"Build and deployment"** section:
   - **Source**: Select "GitHub Actions"
   - This allows the workflow to deploy directly to GitHub Pages

3. Click **"Save"** if you made any changes

### 2. Verify Workflow Permissions

The deploy workflow requires specific permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

These are already configured in `.github/workflows/deploy.yml`.

### 3. Trigger the Deployment

The documentation will be automatically deployed when:

- You push changes to the `main` or `master` branch that affect:
  - Files in `docs/` directory
  - `mkdocs.yml` file
  - Python client code in `openwebui_chat_client/`
  - The workflow file itself

You can also manually trigger the deployment:

1. Go to the Actions tab
2. Select "Deploy Documentation" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

### 4. Access Your Documentation

Once deployed successfully, your documentation will be available at:

```
https://fu-jie.github.io/openwebui-chat-client/
```

## Troubleshooting

### Error: "HttpError: Not Found (404)"

**Symptom**: The deploy job fails with:
```
Creating Pages deployment failed: HttpError: Not Found
Failed to create deployment (status: 404)
```

**Solution**:
1. Verify GitHub Pages is enabled in repository settings
2. Ensure "GitHub Actions" is selected as the source
3. Check that you have admin access to the repository

### Error: "Permission denied"

**Symptom**: The workflow fails with permission errors.

**Solution**:
1. Verify the workflow has the correct permissions
2. Check repository settings → Actions → General → Workflow permissions
3. Ensure "Read and write permissions" is enabled

### Build Succeeds but Deploy Fails

**Symptom**: The `build` job succeeds, but the `deploy` job fails.

**Solution**:
1. This usually indicates GitHub Pages is not properly configured
2. Follow the steps in "Enable GitHub Pages" section above
3. Make sure to select "GitHub Actions" as the source, not a branch

### Documentation Not Updating

**Symptom**: Changes pushed but documentation site not updated.

**Solution**:
1. Check if the workflow was triggered (Actions tab)
2. Verify your changes affect the paths listed in the workflow triggers
3. Check workflow logs for any build errors
4. Try manually triggering the workflow

## Workflow Details

The deployment workflow consists of two jobs:

### Build Job
- Checks out the repository
- Sets up Python 3.11
- Installs MkDocs and dependencies
- Builds the documentation site
- Uploads the built site as an artifact

### Deploy Job
- Downloads the artifact from the build job
- Deploys to GitHub Pages using the official `deploy-pages` action
- Runs in the `github-pages` environment

## Configuration Files

- **Workflow**: `.github/workflows/deploy.yml`
- **MkDocs Config**: `mkdocs.yml`
- **Documentation Source**: `docs/` directory

## Best Practices

1. **Test Locally First**: Before pushing, test your documentation locally:
   ```bash
   pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-static-i18n
   mkdocs serve
   ```
   Then visit `http://localhost:8000` to preview.

2. **Use `--strict` Mode**: The workflow uses `mkdocs build --strict` to catch warnings as errors.

3. **Review Changes**: Always check the Actions tab to ensure successful deployment.

4. **Cache Dependencies**: The workflow caches pip dependencies to speed up builds.

## Multilingual Support

This project uses the `mkdocs-static-i18n` plugin to support English and Chinese documentation:

- **English version**: `https://fu-jie.github.io/openwebui-chat-client/` (default)
- **Chinese version**: `https://fu-jie.github.io/openwebui-chat-client/zh/`

### Adding New Translated Pages

1. Create the Chinese version file with `.zh.md` suffix (e.g., `index.md` → `index.zh.md`)
2. Translate the content while keeping the structure consistent
3. Ensure internal links point to the correct language version

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocs-static-i18n Plugin](https://ultrabug.github.io/mkdocs-static-i18n/)
