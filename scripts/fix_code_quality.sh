#!/bin/bash
# 自动修复代码质量问题
# 运行格式化工具自动修复可修复的问题

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

print_header "🔧 自动修复代码质量问题"

# 1. 运行Black格式化
print_header "步骤1: Black代码格式化"
black openwebui_chat_client/ tests/
print_success "Black格式化完成"

# 2. 运行isort导入排序
print_header "步骤2: isort导入排序"
isort openwebui_chat_client/ tests/
print_success "isort排序完成"

# 3. 运行Ruff自动修复
print_header "步骤3: Ruff自动修复"
ruff check openwebui_chat_client/ tests/ --fix || true
print_success "Ruff自动修复完成"

print_header "✅ 自动修复完成"
echo "建议运行以下命令验证:"
echo "  bash scripts/local_ci_check.sh"
