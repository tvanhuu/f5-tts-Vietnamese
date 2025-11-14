#!/usr/bin/env python3
"""
Load Balancer cho F5-TTS Multi-Server
Tự động phân phối requests đến các TTS servers theo thuật toán Round-Robin

Usage:
    python load_balancer.py --port 8080
"""

from flask import Flask, request, jsonify, send_file, Response
import requests
import itertools
import argparse
import time
from threading import Lock

app = Flask(__name__)

# ===== CẤU HÌNH =====
# Danh sách các TTS servers backend
BACKEND_SERVERS = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5002",
]

# Round-robin iterator
server_cycle = itertools.cycle(BACKEND_SERVERS)
server_lock = Lock()

# Statistics
stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "server_stats": {server: {"requests": 0, "failures": 0} for server in BACKEND_SERVERS},
}
stats_lock = Lock()


def get_next_server():
    """Lấy server tiếp theo theo thuật toán Round-Robin"""
    with server_lock:
        return next(server_cycle)


def update_stats(server, success):
    """Cập nhật thống kê"""
    with stats_lock:
        stats["total_requests"] += 1
        if success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        stats["server_stats"][server]["requests"] += 1
        if not success:
            stats["server_stats"][server]["failures"] += 1


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    # Kiểm tra health của tất cả backend servers
    backend_health = {}
    for server in BACKEND_SERVERS:
        try:
            resp = requests.get(f"{server}/health", timeout=2)
            backend_health[server] = {
                "status": "ok" if resp.status_code == 200 else "error",
                "response": resp.json() if resp.status_code == 200 else None,
            }
        except Exception as e:
            backend_health[server] = {
                "status": "error",
                "error": str(e),
            }
    
    return jsonify({
        "status": "ok",
        "load_balancer": "F5-TTS Load Balancer",
        "backend_servers": len(BACKEND_SERVERS),
        "backends": backend_health,
        "stats": stats,
    })


@app.route("/tts", methods=["POST"])
def tts():
    """
    TTS endpoint - Forward request đến backend server
    Tự động chọn server theo Round-Robin
    """
    # Lấy server tiếp theo
    server = get_next_server()
    
    print(f"🔀 Forwarding request to: {server}")
    
    try:
        # Forward request đến backend server
        # Giữ nguyên tất cả headers và body
        resp = requests.post(
            f"{server}/tts",
            json=request.get_json(),
            headers={key: value for key, value in request.headers if key != 'Host'},
            timeout=120,  # 2 phút timeout
        )
        
        # Kiểm tra response type
        content_type = resp.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON response
            update_stats(server, resp.status_code == 200)
            return jsonify(resp.json()), resp.status_code
        else:
            # File response (audio)
            update_stats(server, resp.status_code == 200)
            return Response(
                resp.content,
                status=resp.status_code,
                headers=dict(resp.headers),
            )
    
    except Exception as e:
        print(f"❌ Error forwarding to {server}: {e}")
        update_stats(server, False)
        return jsonify({
            "error": "Backend server error",
            "server": server,
            "message": str(e),
        }), 500


@app.route("/tts/json", methods=["POST"])
def tts_json():
    """TTS JSON endpoint - Forward request đến backend server"""
    server = get_next_server()
    
    print(f"🔀 Forwarding JSON request to: {server}")
    
    try:
        resp = requests.post(
            f"{server}/tts/json",
            json=request.get_json(),
            headers={key: value for key, value in request.headers if key != 'Host'},
            timeout=120,
        )
        
        update_stats(server, resp.status_code == 200)
        return jsonify(resp.json()), resp.status_code
    
    except Exception as e:
        print(f"❌ Error forwarding to {server}: {e}")
        update_stats(server, False)
        return jsonify({
            "error": "Backend server error",
            "server": server,
            "message": str(e),
        }), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F5-TTS Load Balancer")
    parser.add_argument("--port", type=int, default=8080, help="Port to run load balancer (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🔀 F5-TTS LOAD BALANCER")
    print("="*60)
    print(f"🌐 Listening on: {args.host}:{args.port}")
    print(f"🖥️  Backend servers: {len(BACKEND_SERVERS)}")
    for i, server in enumerate(BACKEND_SERVERS, 1):
        print(f"   {i}. {server}")
    print(f"🔄 Algorithm: Round-Robin")
    print("="*60 + "\n")
    
    app.run(host=args.host, port=args.port, debug=False, threaded=True)

