#!/bin/bash

# Script để chạy nhiều TTS server instances cùng lúc
# Mỗi server chạy trên 1 port riêng
#
# Usage:
#   ./start_multiple_servers.sh                    # Auto-detect venv
#   VENV_PATH=/path/to/venv ./start_multiple_servers.sh  # Specify venv

echo "🚀 Starting Multiple F5-TTS Servers..."
echo "======================================"

# Số lượng server muốn chạy (tùy chỉnh theo RAM)
# Mac Mini M1 16GB → Khuyến nghị 3-4 servers
NUM_SERVERS=3
START_PORT=5000

# Lấy đường dẫn tuyệt đối của thư mục hiện tại
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tìm Python executable (ưu tiên virtual environment)
PYTHON_CMD=""

# 1. Kiểm tra biến môi trường VENV_PATH (nếu user chỉ định)
if [ -n "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/python" ]; then
    PYTHON_CMD="$VENV_PATH/bin/python"
    echo "✅ Using specified virtual environment: $PYTHON_CMD"
else
    # 2. Thử tìm tự động trong thư mục hiện tại
    VENV_NAMES=("f5tts-env" "venv" "env" ".venv" ".env" "virtualenv")

    for venv_name in "${VENV_NAMES[@]}"; do
        if [ -f "$SCRIPT_DIR/$venv_name/bin/python" ]; then
            PYTHON_CMD="$SCRIPT_DIR/$venv_name/bin/python"
            echo "✅ Using virtual environment: $PYTHON_CMD"
            break
        fi
    done
fi

# Nếu không tìm thấy venv, dùng system python
if [ -z "$PYTHON_CMD" ]; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "⚠️  Using system python3 (virtual environment not found)"
        echo "⚠️  This may cause 'ModuleNotFoundError' if packages not installed globally"
        echo "💡 Tip: Activate your virtual environment first:"
        echo "   source /path/to/your-env/bin/activate"
        echo "   Then run this script again"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Aborted"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        echo "⚠️  Using system python (virtual environment not found)"
    else
        echo "❌ Error: Python not found!"
        exit 1
    fi
fi

# Tạo thư mục logs nếu chưa có
mkdir -p logs

# Kill các server cũ nếu đang chạy
echo "🧹 Cleaning up old processes..."
pkill -f "python.*api_server.py" 2>/dev/null || true
sleep 2

# Khởi động các server
echo ""
echo "🔄 Starting $NUM_SERVERS servers..."
for i in $(seq 0 $((NUM_SERVERS - 1))); do
    PORT=$((START_PORT + i))
    LOG_FILE="logs/server_${PORT}.log"
    
    echo "  ✅ Starting server on port $PORT (log: $LOG_FILE)"

    # Chạy server trong background và redirect output vào log file
    nohup $PYTHON_CMD api_server.py --port $PORT > "$LOG_FILE" 2>&1 &
    
    # Lưu PID
    echo $! > "logs/server_${PORT}.pid"
    
    # Đợi 2 giây để server khởi động
    sleep 2
done

echo ""
echo "✅ All servers started!"
echo "======================================"
echo "Servers running on ports:"
for i in $(seq 0 $((NUM_SERVERS - 1))); do
    PORT=$((START_PORT + i))
    echo "  - http://localhost:$PORT"
done

echo ""
echo "📊 Check logs:"
echo "  tail -f logs/server_*.log"
echo ""
echo "🛑 To stop all servers:"
echo "  ./stop_servers.sh"
echo ""
echo "💡 Wait ~30 seconds for all models to load..."

