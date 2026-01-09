#!/bin/bash
# 本地CI/CD环境设置脚本
# 创建虚拟环境并安装所有必需的依赖

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================
# 主流程
# ============================================

print_header "🔧 设置本地CI/CD环境"

# 检查Python版本
print_info "检查Python版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python版本: $PYTHON_VERSION"

# 检查是否已存在虚拟环境
if [ -d "venv" ]; then
    print_info "检测到已存在的虚拟环境"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "删除旧的虚拟环境..."
        rm -rf venv
    else
        print_info "使用现有虚拟环境"
    fi
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    print_info "创建虚拟环境..."
    python3 -m venv venv
    print_success "虚拟环境创建成功"
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 升级pip
print_info "升级pip..."
pip install --upgrade pip

# 安装项目依赖
print_header "📦 安装项目依赖"

print_info "安装核心依赖..."
pip install -e .

print_info "安装测试依赖..."
pip install -e ".[test]"

print_info "安装开发依赖..."
pip install -e ".[dev]"

# 验证安装
print_header "✅ 验证安装"

echo "核心依赖:"
pip show requests python-dotenv httpx | grep "Name:\|Version:"

echo ""
echo "测试工具:"
pip show pytest pytest-cov responses | grep "Name:\|Version:"

echo ""
echo "代码质量工具:"
pip show black isort ruff mypy bandit pip-audit | grep "Name:\|Version:"

# 创建便捷脚本
print_header "🔧 创建便捷脚本"

# 确保scripts目录存在
mkdir -p scripts

# 给脚本添加执行权限
chmod +x scripts/local_ci_check.sh 2>/dev/null || true

print_success "环境设置完成！"

# 显示使用说明
print_header "📖 使用说明"

cat << 'EOF'
虚拟环境已创建并激活。

常用命令:

1. 激活虚拟环境:
   source venv/bin/activate

2. 运行完整CI检查:
   bash scripts/local_ci_check.sh

3. 单独运行各项检查:
   - 格式化: black openwebui_chat_client/ tests/
   - 导入排序: isort openwebui_chat_client/ tests/
   - 代码检查: ruff check openwebui_chat_client/ tests/
   - 类型检查: mypy openwebui_chat_client/
   - 安全扫描: bandit -r openwebui_chat_client/
   - 单元测试: pytest tests/ -v

4. 自动修复格式问题:
   black openwebui_chat_client/ tests/
   isort openwebui_chat_client/ tests/

5. 查看测试覆盖率:
   pytest tests/ --cov=openwebui_chat_client --cov-report=html
   open htmlcov/index.html

6. 退出虚拟环境:
   deactivate

EOF

print_info "现在可以运行: bash scripts/local_ci_check.sh"
