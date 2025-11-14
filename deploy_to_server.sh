#!/bin/bash

# Script để deploy files lên máy server

SERVER_USER="itsw"
SERVER_IP="10.0.67.77"
SERVER_PATH="/Users/itsw/Desktop/F5-TTS-Vietnamese_1"

echo "🚀 Deploying to server..."
echo "================================"
echo "Server: $SERVER_USER@$SERVER_IP"
echo "Path: $SERVER_PATH"
echo ""

# Copy files
echo "📦 Copying files..."
scp api_server.py $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp load_balancer.py $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp start_with_loadbalancer.sh $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp stop_all.sh $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp start_multiple_servers.sh $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp stop_servers.sh $SERVER_USER@$SERVER_IP:$SERVER_PATH/

echo ""
echo "✅ Files copied!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. SSH to server:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "2. Run on server (with Load Balancer):"
echo "   cd $SERVER_PATH"
echo "   chmod +x start_with_loadbalancer.sh stop_all.sh"
echo "   VENV_PATH=$SERVER_PATH/f5tts-env ./start_with_loadbalancer.sh"
echo ""
echo "3. Wait 30 seconds for models to load"
echo ""
echo "4. Test from server:"
echo "   curl http://localhost:8080/health"
echo ""
echo "5. Back on Mac Mini, run client:"
echo "   python tts_client_simple.py"
echo ""
echo "💡 Client chỉ cần gọi: http://10.0.67.77:8080"
echo "   Load Balancer sẽ tự động chia tải vào 3 servers!"
echo ""

