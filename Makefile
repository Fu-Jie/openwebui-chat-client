# Makefile for openwebui-chat-client
# 提供便捷的开发命令

.PHONY: help setup clean test lint format check coverage ci install dev

# 默认目标
help:
	@echo "openwebui-chat-client 开发命令"
	@echo ""
	@echo "环境设置:"
	@echo "  make setup          - 创建虚拟环境并安装所有依赖"
	@echo "  make install        - 安装项目依赖"
	@echo "  make dev            - 安装开发依赖"
	@echo ""
	@echo "代码质量:"
	@echo "  make format         - 自动格式化代码 (black + isort)"
	@echo "  make lint           - 运行代码检查 (ruff)"
	@echo "  make typecheck      - 运行类型检查 (mypy)"
	@echo "  make security       - 运行安全扫描 (bandit)"
	@echo "  make check          - 运行所有检查但不修复"
	@echo "  make fix            - 自动修复所有可修复的问题"
	@echo ""
	@echo "测试:"
	@echo "  make test           - 运行单元测试"
	@echo "  make coverage       - 运行测试并生成覆盖率报告"
	@echo "  make test-verbose   - 运行详细测试输出"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci             - 运行完整的CI检查（模拟GitHub Actions）"
	@echo ""
	@echo "清理:"
	@echo "  make clean          - 清理生成的文件"
	@echo "  make clean-all      - 清理所有文件（包括虚拟环境）"

# 环境设置
setup:
	@echo "🔧 设置开发环境..."
	@bash scripts/setup_local_ci.sh

install:
	@echo "📦 安装项目依赖..."
	@pip install -e .

dev:
	@echo "📦 安装开发依赖..."
	@pip install -e ".[dev,test]"

# 代码格式化
format:
	@echo "🎨 格式化代码..."
	@black openwebui_chat_client/ tests/
	@isort openwebui_chat_client/ tests/
	@echo "✅ 格式化完成"

# 代码检查
lint:
	@echo "🔍 运行Ruff检查..."
	@ruff check openwebui_chat_client/ tests/

typecheck:
	@echo "🔬 运行类型检查..."
	@mypy openwebui_chat_client/ --ignore-missing-imports --no-error-summary || true

security:
	@echo "🔒 运行安全扫描..."
	@bandit -r openwebui_chat_client/ -ll -ii || true

check:
	@echo "✅ 运行所有检查..."
	@black --check openwebui_chat_client/ tests/
	@isort --check-only openwebui_chat_client/ tests/
	@ruff check openwebui_chat_client/ tests/

fix:
	@echo "🔧 自动修复代码问题..."
	@bash scripts/fix_code_quality.sh

# 测试
test:
	@echo "🧪 运行单元测试..."
	@export OPENWEBUI_BASE_URL="http://localhost:3000" && \
	 export OPENWEBUI_TOKEN="test-token-for-ci" && \
	 export OPENWEBUI_DEFAULT_MODEL="test-model" && \
	 pytest tests/ -v

test-verbose:
	@echo "🧪 运行详细测试..."
	@export OPENWEBUI_BASE_URL="http://localhost:3000" && \
	 export OPENWEBUI_TOKEN="test-token-for-ci" && \
	 export OPENWEBUI_DEFAULT_MODEL="test-model" && \
	 pytest tests/ -vv --tb=long

coverage:
	@echo "📊 运行测试并生成覆盖率..."
	@bash scripts/run_tests_with_coverage.sh

# CI检查
ci:
	@echo "🚀 运行完整CI检查..."
	@bash scripts/local_ci_check.sh

# 清理
clean:
	@echo "🧹 清理生成的文件..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf coverage.xml
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成"

clean-all: clean
	@echo "🧹 清理所有文件（包括虚拟环境）..."
	@rm -rf venv/
	@echo "✅ 完全清理完成"
