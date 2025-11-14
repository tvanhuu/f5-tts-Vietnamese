#!/bin/bash

echo "🛑 Stopping all F5-TTS services..."
echo "===================================="

# Kill load balancer
echo "🔀 Stopping Load Balancer..."
pkill -f "python.*load_balancer.py" 2>/dev/null || true

# Kill TTS servers
echo "🖥️  Stopping TTS Servers..."
pkill -f "python.*api_server.py" 2>/dev/null || true

# Remove PID files
rm -f logs/load_balancer.pid
rm -f logs/server_*.pid

sleep 1

echo ""
echo "✅ All services stopped!"
echo "===================================="

