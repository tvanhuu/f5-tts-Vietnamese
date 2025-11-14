#!/usr/bin/env python3
"""
Script test đơn giản với menu tương tác
Dễ sử dụng cho người mới

Usage:
    python test_simple.py
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


# ===== CẤU HÌNH =====
SERVER_URL = "http://10.0.67.77:5000"  # Thay đổi nếu cần
OUTPUT_DIR = Path("test_output")
SPEED = 0.75

# Các câu test
TEST_TEXTS = [
    "Xin chào, đây là câu test thứ nhất.",
    "Câu test thứ hai dài hơn một chút để kiểm tra.",
    "Câu test thứ ba, ngắn gọn.",
]


def call_tts(text, output_file, request_id):
    """Gọi TTS API"""
    start = time.time()
    
    print(f"\n[{request_id}] 🚀 Đang gửi request...")
    print(f"[{request_id}] 📝 Text: {text[:40]}...")
    
    try:
        response = requests.post(
            f"{SERVER_URL}/tts",
            json={"text": text, "speed": SPEED},
            timeout=120,
        )
        
        duration = time.time() - start
        
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            size_mb = len(response.content) / 1024 / 1024
            print(f"[{request_id}] ✅ Thành công! ({duration:.1f}s, {size_mb:.1f}MB)")
            return True, duration
        else:
            print(f"[{request_id}] ❌ Lỗi: HTTP {response.status_code}")
            return False, duration
    
    except Exception as e:
        duration = time.time() - start
        print(f"[{request_id}] ❌ Exception: {e}")
        return False, duration


def test_1_request():
    """Test gửi 1 request"""
    print("\n" + "="*60)
    print("🧪 TEST 1 REQUEST")
    print("="*60)
    
    text = TEST_TEXTS[0]
    output_file = OUTPUT_DIR / "test_1.wav"
    
    overall_start = time.time()
    success, duration = call_tts(text, output_file, 1)
    overall_duration = time.time() - overall_start
    
    print("\n" + "="*60)
    print("📊 KẾT QUẢ")
    print("="*60)
    print(f"✅ Thành công: {1 if success else 0}/1")
    print(f"⏱️  Tổng thời gian: {overall_duration:.1f}s")
    print("="*60 + "\n")


def test_2_requests_sequential():
    """Test gửi 2 requests tuần tự"""
    print("\n" + "="*60)
    print("🧪 TEST 2 REQUESTS - TUẦN TỰ")
    print("="*60)
    
    overall_start = time.time()
    results = []
    
    for i in range(2):
        text = TEST_TEXTS[i]
        output_file = OUTPUT_DIR / f"test_2_seq_{i+1}.wav"
        success, duration = call_tts(text, output_file, i+1)
        results.append(success)
    
    overall_duration = time.time() - overall_start
    
    print("\n" + "="*60)
    print("📊 KẾT QUẢ")
    print("="*60)
    print(f"✅ Thành công: {sum(results)}/2")
    print(f"⏱️  Tổng thời gian: {overall_duration:.1f}s")
    print(f"⏱️  Trung bình: {overall_duration/2:.1f}s/request")
    print("="*60 + "\n")


def test_2_requests_parallel():
    """Test gửi 2 requests song song"""
    print("\n" + "="*60)
    print("🧪 TEST 2 REQUESTS - SONG SONG")
    print("="*60)
    
    overall_start = time.time()
    
    # Chuẩn bị tasks
    tasks = []
    for i in range(2):
        text = TEST_TEXTS[i]
        output_file = OUTPUT_DIR / f"test_2_par_{i+1}.wav"
        tasks.append((text, output_file, i+1))
    
    # Chạy song song
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(call_tts, *task) for task in tasks]
        for future in futures:
            success, duration = future.result()
            results.append(success)
    
    overall_duration = time.time() - overall_start
    
    print("\n" + "="*60)
    print("📊 KẾT QUẢ")
    print("="*60)
    print(f"✅ Thành công: {sum(results)}/2")
    print(f"⏱️  Tổng thời gian: {overall_duration:.1f}s")
    print(f"💡 Nếu có Load Balancer, thời gian sẽ ~bằng 1 request")
    print(f"💡 Nếu không có Load Balancer, request 2 sẽ bị lỗi hoặc chờ")
    print("="*60 + "\n")


def test_3_requests_parallel():
    """Test gửi 3 requests song song"""
    print("\n" + "="*60)
    print("🧪 TEST 3 REQUESTS - SONG SONG")
    print("="*60)
    
    overall_start = time.time()
    
    # Chuẩn bị tasks
    tasks = []
    for i in range(3):
        text = TEST_TEXTS[i]
        output_file = OUTPUT_DIR / f"test_3_par_{i+1}.wav"
        tasks.append((text, output_file, i+1))
    
    # Chạy song song
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(call_tts, *task) for task in tasks]
        for future in futures:
            success, duration = future.result()
            results.append(success)
    
    overall_duration = time.time() - overall_start
    
    print("\n" + "="*60)
    print("📊 KẾT QUẢ")
    print("="*60)
    print(f"✅ Thành công: {sum(results)}/3")
    print(f"⏱️  Tổng thời gian: {overall_duration:.1f}s")
    print(f"💡 Với 3 servers + Load Balancer, thời gian ~bằng 1 request")
    print("="*60 + "\n")


def main():
    # Tạo thư mục output
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("🧪 TTS API TEST - SIMPLE MODE")
    print("="*60)
    print(f"🌐 Server: {SERVER_URL}")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"⚡ Speed: {SPEED}")
    print("="*60)
    
    # Menu
    while True:
        print("\n📋 MENU:")
        print("  1. Test 1 request")
        print("  2. Test 2 requests (tuần tự)")
        print("  3. Test 2 requests (song song)")
        print("  4. Test 3 requests (song song)")
        print("  5. Thay đổi server URL")
        print("  0. Thoát")
        
        choice = input("\n👉 Chọn (0-5): ").strip()
        
        if choice == "1":
            test_1_request()
        elif choice == "2":
            test_2_requests_sequential()
        elif choice == "3":
            test_2_requests_parallel()
        elif choice == "4":
            test_3_requests_parallel()
        elif choice == "5":
            global SERVER_URL
            new_url = input(f"Nhập URL mới (hiện tại: {SERVER_URL}): ").strip()
            if new_url:
                SERVER_URL = new_url
                print(f"✅ Đã đổi sang: {SERVER_URL}")
        elif choice == "0":
            print("\n👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()

