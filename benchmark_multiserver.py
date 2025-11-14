#!/usr/bin/env python3
"""
Benchmark script để test hiệu năng của multi-server setup
So sánh tốc độ giữa 1 server vs nhiều servers
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools


# Test texts
TEST_TEXTS = [
    "cậu cao, nghe nói nhà cậu đã vỡ nợ, sao còn có tiền mua vật liệu đắt tiền như vậy?",
    "nhà tôi đúng là có chút vấn đề, nhưng mấy thứ này đều là tôi tự kiếm được.",
    "tôi đã bán một ít đồ cổ kiếm được chút tiền.",
    "đồ cổ? cậu còn có đồ cổ à?",
    "ừ, nhà tôi trước đây cũng giàu có, để lại ít đồ cổ.",
    "các loại vật liệu đắt tiền này, cậu mua về làm gì?",
    "gần đây cấp trên không hiểu sao lại chú ý đến tôi.",
    "tôi cảm thấy hơi nguy hiểm, nên muốn luyện một ít bùa hộ mệnh.",
    "bùa hộ mệnh? cậu còn biết vẽ bùa à?",
    "biết một chút, tự học được.",
]


def check_server_health(server_url):
    """Kiểm tra server có sẵn sàng không"""
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def call_tts(server_url, text, timeout=60):
    """Gọi TTS API và đo thời gian"""
    start = time.time()
    try:
        response = requests.post(
            f"{server_url}/tts",
            json={"text": text, "speed": 0.75},
            timeout=timeout
        )
        duration = time.time() - start
        success = response.status_code == 200
        return success, duration
    except Exception as e:
        duration = time.time() - start
        return False, duration


def benchmark_single_server(server_url, texts):
    """Benchmark với 1 server (tuần tự)"""
    print(f"\n📊 Benchmark: 1 Server (Sequential)")
    print(f"   Server: {server_url}")
    print(f"   Requests: {len(texts)}")
    print("-" * 60)
    
    durations = []
    success_count = 0
    
    start_time = time.time()
    
    for i, text in enumerate(texts, 1):
        print(f"   [{i}/{len(texts)}] Processing...", end=" ", flush=True)
        success, duration = call_tts(server_url, text)
        
        if success:
            success_count += 1
            durations.append(duration)
            print(f"✅ {duration:.1f}s")
        else:
            print(f"❌ {duration:.1f}s")
    
    total_time = time.time() - start_time
    
    print("-" * 60)
    print(f"✅ Success: {success_count}/{len(texts)}")
    print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    if durations:
        print(f"📈 Avg per request: {statistics.mean(durations):.1f}s")
    
    return {
        "total_time": total_time,
        "success_count": success_count,
        "total_requests": len(texts),
        "durations": durations
    }


def process_request_parallel(args):
    """Xử lý 1 request (cho parallel execution)"""
    i, text, server_url = args
    success, duration = call_tts(server_url, text)
    return i, success, duration, server_url


def benchmark_multi_server(servers, texts):
    """Benchmark với nhiều servers (parallel)"""
    print(f"\n📊 Benchmark: {len(servers)} Servers (Parallel)")
    for idx, server in enumerate(servers, 1):
        print(f"   Server {idx}: {server}")
    print(f"   Requests: {len(texts)}")
    print("-" * 60)
    
    # Round-robin assignment
    server_cycle = itertools.cycle(servers)
    tasks = [(i, text, next(server_cycle)) for i, text in enumerate(texts)]
    
    durations = []
    success_count = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=len(servers)) as executor:
        futures = {executor.submit(process_request_parallel, task): task for task in tasks}
        
        for future in as_completed(futures):
            i, success, duration, server_url = future.result()
            server_num = servers.index(server_url) + 1
            
            if success:
                success_count += 1
                durations.append(duration)
                print(f"   [{i+1}/{len(texts)}] Server{server_num} ✅ {duration:.1f}s")
            else:
                print(f"   [{i+1}/{len(texts)}] Server{server_num} ❌ {duration:.1f}s")
    
    total_time = time.time() - start_time
    
    print("-" * 60)
    print(f"✅ Success: {success_count}/{len(texts)}")
    print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    if durations:
        print(f"📈 Avg per request: {statistics.mean(durations):.1f}s")
    
    return {
        "total_time": total_time,
        "success_count": success_count,
        "total_requests": len(texts),
        "durations": durations
    }


def main():
    # Cấu hình
    SERVERS = [
        "http://10.0.67.77:5000",
        "http://10.0.67.77:5001",
        "http://10.0.67.77:5002",
    ]
    
    print("\n" + "=" * 60)
    print("🚀 MULTI-SERVER BENCHMARK")
    print("=" * 60)
    
    # Kiểm tra servers
    print("\n🔍 Checking servers...")
    available_servers = []
    for server in SERVERS:
        if check_server_health(server):
            print(f"   ✅ {server}")
            available_servers.append(server)
        else:
            print(f"   ❌ {server} (not available)")
    
    if not available_servers:
        print("\n❌ No servers available! Please start servers first:")
        print("   ./start_multiple_servers.sh")
        return
    
    print(f"\n✅ Found {len(available_servers)} available server(s)")
    
    # Benchmark 1: Single server
    result_single = benchmark_single_server(available_servers[0], TEST_TEXTS)
    
    # Benchmark 2: Multi server (nếu có nhiều hơn 1)
    if len(available_servers) > 1:
        result_multi = benchmark_multi_server(available_servers, TEST_TEXTS)
        
        # So sánh
        print("\n" + "=" * 60)
        print("📊 COMPARISON")
        print("=" * 60)
        print(f"1 Server:  {result_single['total_time']:.1f}s")
        print(f"{len(available_servers)} Servers: {result_multi['total_time']:.1f}s")
        
        speedup = result_single['total_time'] / result_multi['total_time']
        print(f"\n🚀 Speedup: {speedup:.2f}x")
        print(f"⏱️  Time saved: {result_single['total_time'] - result_multi['total_time']:.1f}s")
        print("=" * 60 + "\n")
    else:
        print("\n⚠️  Only 1 server available. Start more servers to see speedup!")
        print("   ./start_multiple_servers.sh")
        print()


if __name__ == "__main__":
    main()

