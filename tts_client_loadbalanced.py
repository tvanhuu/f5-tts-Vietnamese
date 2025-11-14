#!/usr/bin/env python3
"""
TTS Client với Load Balancing
Tự động phân phối request đến nhiều server để tăng tốc độ xử lý
"""

import requests
import json
import re
import time
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools


def parse_srt(srt_file_path):
    """Parse file SRT và trích xuất tất cả text"""
    with open(srt_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    texts = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.isdigit():
            i += 1
            continue

        if "-->" in line:
            i += 1
            if i < len(lines) and lines[i].strip():
                texts.append(lines[i].strip())
            i += 1
            continue

        i += 1

    return texts


def load_checkpoint(checkpoint_file):
    """Load checkpoint từ file"""
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))
    return set()


def save_checkpoint(checkpoint_file, completed):
    """Lưu checkpoint vào file"""
    with open(checkpoint_file, "w") as f:
        json.dump({"completed": sorted(list(completed))}, f)


def call_tts_api(server_url, text, output_path, speed=0.75, timeout=120):
    """
    Gọi TTS API để chuyển text thành audio

    Args:
        server_url: URL của server (ví dụ: http://localhost:5000)
        text: Text cần chuyển thành giọng nói
        output_path: Đường dẫn lưu file audio
        speed: Tốc độ đọc (default: 0.75)
        timeout: Timeout cho request (giây)

    Returns:
        True nếu thành công, False nếu lỗi
    """
    url = f"{server_url}/tts"
    payload = {"text": text, "speed": speed}

    try:
        response = requests.post(url, json=payload, timeout=timeout)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"      ❌ Error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"      ⏱️  Timeout after {timeout}s")
        return False
    except requests.exceptions.RequestException as e:
        print(f"      ❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"      ❌ Error: {str(e)}")
        return False


def process_single_request(args):
    """
    Xử lý 1 request (dùng cho ThreadPoolExecutor)

    Args:
        args: tuple (index, text, server_url, output_dir, speed)

    Returns:
        tuple (index, success, duration, server_url)
    """
    i, text, server_url, output_dir, speed = args

    output_filename = f"output_{i+1:03d}.wav"
    output_path = output_dir / output_filename

    start_time = time.time()
    success = call_tts_api(server_url, text, output_path, speed)
    duration = time.time() - start_time

    return (i, success, duration, server_url)


def main():
    # ===== CẤU HÌNH =====
    SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"
    OUTPUT_DIR = Path("output_audio")
    CHECKPOINT_FILE = OUTPUT_DIR / ".checkpoint.json"
    SPEED = 0.75

    # Danh sách các server (tự động detect hoặc config thủ công)
    # Nếu server chỉ chạy 1 instance, chỉ dùng 1 URL
    SERVERS = [
        "http://10.0.67.77:5000",
        # Nếu server chạy nhiều instances, thêm vào đây:
        # "http://10.0.67.77:5001",
        # "http://10.0.67.77:5002",
    ]

    # Số lượng worker threads (= số server)
    MAX_WORKERS = len(SERVERS)

    # ===== KHỞI TẠO =====
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("🚀 TTS CLIENT với LOAD BALANCING")
    print("=" * 60)
    print(f"📁 SRT File: {SRT_FILE}")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"⚡ Speed: {SPEED}")
    print(f"🖥️  Servers: {len(SERVERS)}")
    for idx, server in enumerate(SERVERS, 1):
        print(f"   {idx}. {server}")
    print(f"🔀 Max parallel requests: {MAX_WORKERS}")
    print("=" * 60 + "\n")

    # Load checkpoint
    completed = load_checkpoint(CHECKPOINT_FILE)
    if completed:
        print(f"📌 Tìm thấy checkpoint: Đã hoàn thành {len(completed)} đoạn trước đó")
        print("🔄 Tiếp tục từ chỗ đã dừng...\n")

    # Parse SRT
    print(f"Đang đọc file SRT: {SRT_FILE}")
    texts = parse_srt(SRT_FILE)
    print(f"Tìm thấy {len(texts)} đoạn text\n")

    # Hiển thị preview
    for i, text in enumerate(texts):
        status = "✓" if i in completed else " "
        print(f"[{status}] {i+1}. {text}")

    # Tính toán số lượng cần xử lý
    remaining = [i for i in range(len(texts)) if i not in completed]

    if not remaining:
        print("\n✅ Tất cả đã hoàn thành!")
        return

    print(f"\n📊 Cần xử lý: {len(remaining)}/{len(texts)} đoạn")
    print(
        f"⏱️  Ước tính: ~{len(remaining) * 23 / len(SERVERS):.0f}s với {len(SERVERS)} servers"
    )
    print(f"   (So với 1 server: ~{len(remaining) * 23:.0f}s)")
    print(f"   → Tăng tốc: ~{len(SERVERS)}x\n")

    # Chuẩn bị tasks với round-robin server assignment
    server_cycle = itertools.cycle(SERVERS)
    tasks = []
    for i in remaining:
        server_url = next(server_cycle)
        tasks.append((i, texts[i], server_url, OUTPUT_DIR, SPEED))

    # Xử lý song song với ThreadPoolExecutor
    print("🔄 Bắt đầu xử lý...\n")
    overall_start = time.time()

    success_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tất cả tasks
        futures = {
            executor.submit(process_single_request, task): task for task in tasks
        }

        # Xử lý kết quả khi hoàn thành
        for future in as_completed(futures):
            task = futures[future]
            i, text, server_url, _, _ = task

            try:
                idx, success, duration, used_server = future.result()

                if success:
                    success_count += 1
                    completed.add(idx)
                    save_checkpoint(CHECKPOINT_FILE, completed)

                    server_num = SERVERS.index(used_server) + 1
                    print(
                        f"✅ [{success_count + failed_count}/{len(remaining)}] "
                        f"Server{server_num} | {duration:.1f}s | {text[:50]}..."
                    )
                else:
                    failed_count += 1
                    print(
                        f"❌ [{success_count + failed_count}/{len(remaining)}] "
                        f"FAILED | {text[:50]}..."
                    )

            except Exception as e:
                failed_count += 1
                print(f"❌ Exception: {str(e)}")

    overall_duration = time.time() - overall_start

    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ")
    print("=" * 60)
    print(f"✅ Thành công: {success_count}/{len(remaining)}")
    print(f"❌ Thất bại: {failed_count}/{len(remaining)}")
    print(
        f"⏱️  Tổng thời gian: {overall_duration:.1f}s ({overall_duration/60:.1f} phút)"
    )
    print(f"⚡ Tốc độ trung bình: {overall_duration/len(remaining):.1f}s/đoạn")
    print(f"🚀 Tăng tốc: ~{len(SERVERS)}x so với 1 server")
    print("=" * 60 + "\n")

    if failed_count == 0:
        # Xóa checkpoint khi hoàn thành
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
        print("🎉 Hoàn thành tất cả! Checkpoint đã được xóa.\n")
    else:
        print("⚠️  Có lỗi xảy ra. Chạy lại script để retry các đoạn thất bại.\n")


if __name__ == "__main__":
    main()
