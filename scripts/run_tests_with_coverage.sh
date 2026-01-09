#!/bin/bash
# 运行测试并生成覆盖率报告

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ 未检测到虚拟环境！"
    echo "请先运行: source venv/bin/activate"
    exit 1
fi

print_header "🧪 运行测试并生成覆盖率报告"

# 设置测试环境变量
export OPENWEBUI_BASE_URL="http://localhost:3000"
export OPENWEBUI_TOKEN="test-token-for-ci"
export OPENWEBUI_DEFAULT_MODEL="test-model"

# 运行测试
pytest tests/ -v \
    --cov=openwebui_chat_client \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml

print_success "测试完成"

# 显示覆盖率摘要
print_header "📊 覆盖率摘要"
coverage report --show-missing

# 提示打开HTML报告
print_header "📄 HTML报告"
echo "HTML覆盖率报告已生成: htmlcov/index.html"
echo ""
echo "在浏览器中打开:"
echo "  macOS:   open htmlcov/index.html"
echo "  Linux:   xdg-open htmlcov/index.html"
echo "  Windows: start htmlcov/index.html"
