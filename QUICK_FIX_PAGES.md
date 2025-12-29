# Quick Fix: Enable GitHub Pages (404 Error)

## ⚡ One-Time Setup Required

Your documentation workflow is failing because **GitHub Pages is not enabled**.

### 🔧 How to Fix (Takes 30 seconds)

1. **Go to repository settings:**
   
   👉 https://github.com/Fu-Jie/openwebui-chat-client/settings/pages

2. **Enable Pages:**
   - Find "Build and deployment" section
   - Set Source to: **"GitHub Actions"**
   - Save

3. **Re-run workflow:**
   - Go to Actions tab
   - Select the failed "Deploy Documentation" workflow
   - Click "Re-run all jobs"

### ✅ Expected Result

After enabling Pages, your documentation will be available at:

🌐 **https://fu-jie.github.io/openwebui-chat-client/**

---

## 📚 Need More Help?

See the detailed guide: `docs/github-pages-setup.md`

## 🤔 Why This Happens

The workflow needs GitHub Pages to be enabled before it can deploy. This is a one-time repository configuration step that can only be done through the GitHub UI, not through code changes.

---

**Note:** This is a repository setting, not a code issue. The workflow configuration is correct and ready to work once Pages is enabled.
