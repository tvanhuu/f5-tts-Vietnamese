#!/bin/bash

# Script để chạy nhiều TTS server instances cùng lúc
# Mỗi server chạy trên 1 port riêng

echo "🚀 Starting Multiple F5-TTS Servers..."
echo "======================================"

# Số lượng server muốn chạy (tùy chỉnh theo RAM)
# Mac Mini M1 16GB → Khuyến nghị 3-4 servers
NUM_SERVERS=3
START_PORT=5000

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
    nohup python api_server.py --port $PORT > "$LOG_FILE" 2>&1 &
    
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

