#!/bin/bash

echo "🔍 Checking for virtual environment..."
echo "========================================"
echo ""

# Lấy thư mục hiện tại
CURRENT_DIR="$(pwd)"
echo "📁 Current directory: $CURRENT_DIR"
echo ""

# Tìm các thư mục có thể là virtual environment
echo "🔎 Looking for virtual environment folders..."
for dir in venv env .venv .env f5tts-env virtualenv; do
    if [ -d "$dir" ]; then
        echo "  ✅ Found: $dir/"
        if [ -f "$dir/bin/python" ]; then
            echo "     → Python: $dir/bin/python"
            echo "     → Version: $($dir/bin/python --version 2>&1)"
        fi
    fi
done

echo ""
echo "📦 Checking for Python installations..."
echo "  System python3: $(which python3 2>/dev/null || echo 'Not found')"
echo "  System python: $(which python 2>/dev/null || echo 'Not found')"

echo ""
echo "💡 If you're using a virtual environment, activate it with:"
echo "   source /path/to/your-env/bin/activate"
echo ""

