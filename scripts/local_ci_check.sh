#!/bin/bash
# 本地CI/CD检查脚本
# 模拟GitHub Actions工作流在本地运行

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查是否在虚拟环境中
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "未检测到虚拟环境！"
        print_info "请先运行: source venv/bin/activate"
        exit 1
    fi
    print_success "虚拟环境已激活: $VIRTUAL_ENV"
}

# 步骤计数器
STEP=0
TOTAL_STEPS=7
FAILED_STEPS=()

next_step() {
    STEP=$((STEP + 1))
    print_header "步骤 $STEP/$TOTAL_STEPS: $1"
}

# 记录失败的步骤
record_failure() {
    FAILED_STEPS+=("$1")
}

# ============================================
# 主流程开始
# ============================================

print_header "🚀 本地CI/CD检查开始"
echo "模拟GitHub Actions工作流"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查虚拟环境
check_venv

# ============================================
# 步骤1: 检查依赖安装
# ============================================
next_step "检查依赖安装"

if pip show black isort ruff mypy bandit pip-audit pytest pytest-cov > /dev/null 2>&1; then
    print_success "所有开发依赖已安装"
else
    print_warning "部分依赖未安装，正在安装..."
    pip install -e ".[dev,test]" || {
        print_error "依赖安装失败"
        record_failure "依赖安装"
    }
fi

# ============================================
# 步骤2: 代码格式化检查 (Black)
# ============================================
next_step "代码格式化检查 (Black)"

if black --check --diff openwebui_chat_client/ tests/ 2>&1; then
    print_success "Black格式化检查通过"
else
    print_error "Black格式化检查失败"
    print_info "运行以下命令修复: black openwebui_chat_client/ tests/"
    record_failure "Black格式化"
fi

# ============================================
# 步骤3: 导入排序检查 (isort)
# ============================================
next_step "导入排序检查 (isort)"

if isort --check-only --diff openwebui_chat_client/ tests/ 2>&1; then
    print_success "isort导入排序检查通过"
else
    print_error "isort导入排序检查失败"
    print_info "运行以下命令修复: isort openwebui_chat_client/ tests/"
    record_failure "isort导入排序"
fi

# ============================================
# 步骤4: 代码检查 (Ruff)
# ============================================
next_step "代码检查 (Ruff)"

if ruff check openwebui_chat_client/ tests/ 2>&1; then
    print_success "Ruff代码检查通过"
else
    print_error "Ruff代码检查失败"
    print_info "运行以下命令查看详情: ruff check openwebui_chat_client/ tests/ --show-fixes"
    record_failure "Ruff代码检查"
fi

# ============================================
# 步骤5: 类型检查 (mypy) - 非阻断
# ============================================
next_step "类型检查 (mypy) - 非阻断"

if mypy openwebui_chat_client/ --ignore-missing-imports --no-error-summary 2>&1; then
    print_success "mypy类型检查通过"
else
    print_warning "mypy类型检查发现问题（非阻断）"
fi

# ============================================
# 步骤6: 安全扫描 (Bandit) - 非阻断
# ============================================
next_step "安全扫描 (Bandit) - 非阻断"

if bandit -r openwebui_chat_client/ -ll -ii 2>&1; then
    print_success "Bandit安全扫描通过"
else
    print_warning "Bandit安全扫描发现问题（非阻断）"
fi

# ============================================
# 步骤7: 单元测试
# ============================================
next_step "单元测试"

# 设置测试环境变量
export OPENWEBUI_BASE_URL="http://localhost:3000"
export OPENWEBUI_TOKEN="test-token-for-ci"
export OPENWEBUI_DEFAULT_MODEL="test-model"

print_info "运行单元测试..."
if python -m pytest tests/ -v --tb=short 2>&1; then
    print_success "单元测试通过"
else
    print_error "单元测试失败"
    record_failure "单元测试"
fi

# ============================================
# 生成总结报告
# ============================================
print_header "📊 CI/CD检查总结"

if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    print_success "所有检查通过！ 🎉"
    echo ""
    print_info "你的代码已准备好提交到GitHub"
    exit 0
else
    print_error "以下检查失败:"
    for step in "${FAILED_STEPS[@]}"; do
        echo "  - $step"
    done
    echo ""
    print_info "请修复上述问题后再提交代码"
    exit 1
fi
