#!/bin/bash
# 覆盖率分析脚本

set -e

echo "🔍 运行覆盖率分析..."
echo "================================"

# 运行测试并生成覆盖率
coverage run -m pytest tests/ -v --tb=short

echo ""
echo "📊 覆盖率总览"
echo "================================"
coverage report

echo ""
echo "📉 覆盖率最低的10个文件"
echo "================================"
coverage report --sort=cover | head -15

echo ""
echo "📄 生成HTML报告..."
coverage html

echo ""
echo "✅ 完成！"
echo ""
echo "📌 下一步："
echo "  1. 打开 htmlcov/index.html 查看详细报告"
echo "  2. 红色高亮的代码是未覆盖的部分"
echo "  3. 优先为覆盖率最低的文件添加测试"
echo ""
echo "💡 提示："
echo "  - 当前覆盖率: $(coverage report | grep TOTAL | awk '{print $4}')"
echo "  - 目标覆盖率: 80%"
echo "  - 查看详细指南: COVERAGE_IMPROVEMENT_GUIDE.md"
