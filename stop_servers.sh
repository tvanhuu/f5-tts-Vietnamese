#!/bin/bash

# Script để dừng tất cả TTS servers

echo "🛑 Stopping all F5-TTS servers..."

# Kill tất cả process python chạy api_server.py
pkill -f "python.*api_server.py"

# Xóa các PID files
rm -f logs/server_*.pid

echo "✅ All servers stopped!"

