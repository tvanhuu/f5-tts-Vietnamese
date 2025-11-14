#!/usr/bin/env python3
"""
Script test để gửi 1 hoặc nhiều requests cùng lúc
Dùng để test Load Balancer hoặc single server

Usage:
    python test_requests.py --num 1      # Gửi 1 request
    python test_requests.py --num 2      # Gửi 2 requests song song
    python test_requests.py --num 3      # Gửi 3 requests song song
"""

import requests
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def call_tts_api(server_url, text, output_path, request_id, speed=1.0):
    """
    Gọi TTS API và lưu file audio
    
    Args:
        server_url: URL của server hoặc Load Balancer
        text: Text cần chuyển thành giọng nói
        output_path: Đường dẫn file output
        request_id: ID của request (để tracking)
        speed: Tốc độ đọc
    
    Returns:
        dict: Kết quả với thông tin chi tiết
    """
    start_time = time.time()
    
    try:
        print(f"[Request {request_id}] 🚀 Bắt đầu gửi...")
        print(f"[Request {request_id}] 📝 Text: {text[:50]}...")
        
        payload = {
            "text": text,
            "speed": speed,
        }

        response = requests.post(
            f"{server_url}/tts",
            json=payload,
            timeout=120,
        )

        duration = time.time() - start_time

        if response.status_code == 200:
            # Lưu file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024 / 1024  # MB
            
            print(f"[Request {request_id}] ✅ Thành công!")
            print(f"[Request {request_id}] ⏱️  Thời gian: {duration:.2f}s")
            print(f"[Request {request_id}] 💾 Kích thước: {file_size:.2f} MB")
            print(f"[Request {request_id}] 📁 File: {output_path}")
            
            return {
                "request_id": request_id,
                "success": True,
                "duration": duration,
                "file_size": file_size,
                "output_path": str(output_path),
                "text": text,
            }
        else:
            print(f"[Request {request_id}] ❌ Lỗi: HTTP {response.status_code}")
            return {
                "request_id": request_id,
                "success": False,
                "duration": duration,
                "error": f"HTTP {response.status_code}",
            }

    except Exception as e:
        duration = time.time() - start_time
        print(f"[Request {request_id}] ❌ Exception: {e}")
        return {
            "request_id": request_id,
            "success": False,
            "duration": duration,
            "error": str(e),
        }


def test_sequential(server_url, num_requests, output_dir, speed):
    """Test gửi requests tuần tự (lần lượt)"""
    print("\n" + "="*60)
    print(f"🔄 TEST TUẦN TỰ - {num_requests} requests")
    print("="*60 + "\n")
    
    texts = [
        "Xin chào, đây là câu thứ nhất để test hệ thống.",
        "Câu thứ hai này dài hơn một chút để kiểm tra khả năng xử lý của server.",
        "Đây là câu thứ ba, ngắn gọn.",
        "Câu thứ tư với nội dung khác nhau.",
        "Câu cuối cùng để kết thúc bài test.",
    ]
    
    results = []
    overall_start = time.time()
    
    for i in range(num_requests):
        text = texts[i % len(texts)]
        output_path = output_dir / f"test_sequential_{i+1}.wav"
        
        result = call_tts_api(server_url, text, output_path, i+1, speed)
        results.append(result)
        print()
    
    overall_duration = time.time() - overall_start
    
    return results, overall_duration


def test_parallel(server_url, num_requests, output_dir, speed):
    """Test gửi requests song song (cùng lúc)"""
    print("\n" + "="*60)
    print(f"⚡ TEST SONG SONG - {num_requests} requests")
    print("="*60 + "\n")
    
    texts = [
        "Xin chào, đây là câu thứ nhất để test hệ thống.",
        "Câu thứ hai này dài hơn một chút để kiểm tra khả năng xử lý của server.",
        "Đây là câu thứ ba, ngắn gọn.",
        "Câu thứ tư với nội dung khác nhau.",
        "Câu cuối cùng để kết thúc bài test.",
    ]
    
    overall_start = time.time()
    
    # Tạo tasks
    tasks = []
    for i in range(num_requests):
        text = texts[i % len(texts)]
        output_path = output_dir / f"test_parallel_{i+1}.wav"
        tasks.append((server_url, text, output_path, i+1, speed))
    
    # Chạy song song
    results = []
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [
            executor.submit(call_tts_api, *task)
            for task in tasks
        ]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print()
    
    overall_duration = time.time() - overall_start
    
    # Sort results by request_id
    results.sort(key=lambda x: x["request_id"])
    
    return results, overall_duration


def print_summary(results, overall_duration, mode):
    """In tổng kết kết quả"""
    print("\n" + "="*60)
    print(f"📊 TỔNG KẾT - {mode}")
    print("="*60)
    
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    
    print(f"✅ Thành công: {success_count}/{len(results)}")
    print(f"❌ Thất bại: {fail_count}/{len(results)}")
    print(f"⏱️  Tổng thời gian: {overall_duration:.2f}s")
    
    if success_count > 0:
        avg_duration = sum(r["duration"] for r in results if r["success"]) / success_count
        print(f"⏱️  Trung bình mỗi request: {avg_duration:.2f}s")
        
        total_size = sum(r.get("file_size", 0) for r in results if r["success"])
        print(f"💾 Tổng dung lượng: {total_size:.2f} MB")
    
    print("="*60 + "\n")
    
    # Chi tiết từng request
    print("📋 CHI TIẾT:")
    for r in results:
        if r["success"]:
            print(f"  [{r['request_id']}] ✅ {r['duration']:.2f}s - {r['file_size']:.2f}MB")
        else:
            print(f"  [{r['request_id']}] ❌ {r['duration']:.2f}s - {r.get('error', 'Unknown error')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Test TTS API với 1 hoặc nhiều requests")
    parser.add_argument("--num", type=int, default=1, help="Số lượng requests (default: 1)")
    parser.add_argument("--mode", choices=["sequential", "parallel"], default="parallel",
                        help="Chế độ: sequential (tuần tự) hoặc parallel (song song)")
    parser.add_argument("--server", type=str, default="http://10.0.67.77:5000",
                        help="URL của server hoặc Load Balancer")
    parser.add_argument("--speed", type=float, default=0.75, help="Tốc độ đọc (default: 0.75)")
    args = parser.parse_args()
    
    # Tạo thư mục output
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("🧪 TTS API TEST")
    print("="*60)
    print(f"🌐 Server: {args.server}")
    print(f"📊 Số requests: {args.num}")
    print(f"🔄 Chế độ: {args.mode}")
    print(f"⚡ Speed: {args.speed}")
    print(f"📂 Output: {output_dir}")
    print("="*60)
    
    # Chạy test
    if args.mode == "sequential":
        results, duration = test_sequential(args.server, args.num, output_dir, args.speed)
        print_summary(results, duration, "TUẦN TỰ")
    else:
        results, duration = test_parallel(args.server, args.num, output_dir, args.speed)
        print_summary(results, duration, "SONG SONG")


if __name__ == "__main__":
    main()

