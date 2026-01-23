#!/bin/bash
# Run parallel chat integration tests

set -e  # Exit on error

echo "🧪 Running Parallel Chat Integration Tests"
echo "=========================================="
echo ""

# Check environment variables
if [ -z "$OUI_AUTH_TOKEN" ]; then
    echo "❌ Error: OUI_AUTH_TOKEN not set"
    echo "   Set it with: export OUI_AUTH_TOKEN='your_token_here'"
    exit 1
fi

if [ -z "$OUI_PARALLEL_MODELS" ]; then
    echo "⚠️  Warning: OUI_PARALLEL_MODELS not set, using default"
    export OUI_PARALLEL_MODELS="gpt-4.1,gemini-2.5-flash"
fi

echo "✅ Environment configured:"
echo "   Base URL: ${OUI_BASE_URL:-http://localhost:3000}"
echo "   Default Model: ${OUI_DEFAULT_MODEL:-gpt-4.1}"
echo "   Parallel Models: $OUI_PARALLEL_MODELS"
echo ""

# Run simple demo first
echo "📝 Running simple parallel chat demo..."
echo "----------------------------------------"
python examples/chat_features/parallel_chat_simple.py
SIMPLE_EXIT=$?

if [ $SIMPLE_EXIT -eq 0 ]; then
    echo "✅ Simple demo passed"
else
    echo "❌ Simple demo failed with exit code $SIMPLE_EXIT"
    exit $SIMPLE_EXIT
fi

echo ""
echo "📝 Running comprehensive integration tests..."
echo "----------------------------------------------"
python examples/chat_features/parallel_chat_with_history.py
FULL_EXIT=$?

if [ $FULL_EXIT -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed!"
    exit 0
else
    echo ""
    echo "❌ Integration tests failed with exit code $FULL_EXIT"
    exit $FULL_EXIT
fi
