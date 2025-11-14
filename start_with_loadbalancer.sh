#!/bin/bash

# Script để chạy Multi-Server + Load Balancer
# Load Balancer sẽ tự động phân phối requests đến các servers

echo "🚀 Starting F5-TTS Multi-Server with Load Balancer..."
echo "============================================================"

# Cấu hình
NUM_SERVERS=3
START_PORT=5000
LOAD_BALANCER_PORT=8080

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
    else
        echo "❌ Error: Python not found!"
        exit 1
    fi
fi

# Tạo thư mục logs
mkdir -p logs

# Kill các process cũ
echo "🧹 Cleaning up old processes..."
pkill -f "python.*api_server.py" 2>/dev/null || true
pkill -f "python.*load_balancer.py" 2>/dev/null || true
sleep 2

echo ""
echo "🔄 Starting $NUM_SERVERS backend servers..."

# Khởi động các TTS servers
for i in $(seq 0 $((NUM_SERVERS - 1))); do
    PORT=$((START_PORT + i))
    LOG_FILE="logs/server_${PORT}.log"
    
    echo "  ✅ Starting TTS server on port $PORT"
    
    nohup $PYTHON_CMD api_server.py --port $PORT > "$LOG_FILE" 2>&1 &
    
    # Lưu PID
    echo $! > "logs/server_${PORT}.pid"
    
    sleep 2
done

echo ""
echo "⏳ Waiting 10 seconds for servers to initialize..."
sleep 10

echo ""
echo "🔀 Starting Load Balancer on port $LOAD_BALANCER_PORT..."

# Khởi động Load Balancer
nohup $PYTHON_CMD load_balancer.py --port $LOAD_BALANCER_PORT > "logs/load_balancer.log" 2>&1 &
echo $! > "logs/load_balancer.pid"

sleep 3

echo ""
echo "✅ All services started!"
echo "============================================================"
echo "🔀 Load Balancer:"
echo "   http://localhost:$LOAD_BALANCER_PORT"
echo "   http://0.0.0.0:$LOAD_BALANCER_PORT (accessible from other machines)"
echo ""
echo "🖥️  Backend TTS Servers:"
for i in $(seq 0 $((NUM_SERVERS - 1))); do
    PORT=$((START_PORT + i))
    echo "   $((i+1)). http://localhost:$PORT"
done
echo ""
echo "📊 Check status:"
echo "   curl http://localhost:$LOAD_BALANCER_PORT/health"
echo ""
echo "📋 Check logs:"
echo "   tail -f logs/load_balancer.log"
echo "   tail -f logs/server_*.log"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop_all.sh"
echo ""
echo "💡 From other machines, use:"
echo "   http://10.0.67.77:$LOAD_BALANCER_PORT"
echo "============================================================"

