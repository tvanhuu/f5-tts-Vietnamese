#!/usr/bin/env python3
"""
TTS Client đơn giản - Chỉ cần gọi Load Balancer
Load Balancer sẽ tự động chia tải vào các servers

Usage:
    python tts_client_simple.py
"""

import requests
import time
import json
from pathlib import Path


def parse_srt(srt_file_path):
    """Parse file SRT và trích xuất tất cả text"""
    with open(srt_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    texts = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Bỏ qua dòng số thứ tự
        if line.isdigit():
            i += 1
            # Bỏ qua dòng timestamp
            if i < len(lines) and "-->" in lines[i]:
                i += 1
                # Đọc text (có thể nhiều dòng)
                text_lines = []
                while i < len(lines) and lines[i].strip() != "":
                    text_lines.append(lines[i].strip())
                    i += 1
                if text_lines:
                    texts.append(" ".join(text_lines))
        i += 1

    return texts


def call_tts_api(server_url, text, output_path, speed=1.0):
    """
    Gọi TTS API và lưu file audio

    Args:
        server_url: URL của Load Balancer
        text: Text cần chuyển thành giọng nói
        output_path: Đường dẫn file output
        speed: Tốc độ đọc (0.5 - 2.0)

    Returns:
        bool: True nếu thành công
    """
    try:
        payload = {
            "text": text,
            "speed": speed,
        }

        response = requests.post(
            f"{server_url}/tts",
            json=payload,
            timeout=120,
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def load_checkpoint(checkpoint_file):
    """Load checkpoint từ file JSON"""
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))
    return set()


def save_checkpoint(checkpoint_file, completed):
    """Lưu checkpoint vào file JSON"""
    with open(checkpoint_file, "w") as f:
        json.dump({"completed": list(completed)}, f, indent=2)


def main():
    # ===== CẤU HÌNH =====
    LOAD_BALANCER_URL = "http://10.0.67.77:8080"  # Địa chỉ Load Balancer
    SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"
    OUTPUT_DIR = Path("output_audio")
    CHECKPOINT_FILE = OUTPUT_DIR / ".checkpoint.json"
    SPEED = 0.75

    # ===== KHỞI TẠO =====
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("🚀 TTS CLIENT - Simple Mode")
    print("=" * 60)
    print(f"📁 SRT File: {SRT_FILE}")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"⚡ Speed: {SPEED}")
    print(f"🔀 Load Balancer: {LOAD_BALANCER_URL}")
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
        preview = text[:50] + "..." if len(text) > 50 else text
        print(f"[{status}] {i+1:2d}. {preview}")

    # Tính toán remaining
    remaining = [i for i in range(len(texts)) if i not in completed]

    if not remaining:
        print("\n✅ Tất cả đã hoàn thành!")
        return

    print(f"\n📊 Cần xử lý: {len(remaining)}/{len(texts)} đoạn")
    print("=" * 60 + "\n")

    # Xử lý tuần tự (Load Balancer sẽ tự động chia tải)
    print("🔄 Bắt đầu xử lý...\n")
    overall_start = time.time()

    success_count = 0
    fail_count = 0

    for idx, i in enumerate(remaining, 1):
        text = texts[i]
        output_filename = f"audio_{i+1:04d}.wav"
        output_path = OUTPUT_DIR / output_filename

        preview = text[:60] + "..." if len(text) > 60 else text
        print(f"[{idx}/{len(remaining)}] Processing: {preview}")

        start_time = time.time()
        success = call_tts_api(LOAD_BALANCER_URL, text, output_path, SPEED)
        duration = time.time() - start_time

        if success:
            print(f"  ✅ Success in {duration:.1f}s → {output_filename}\n")
            completed.add(i)
            save_checkpoint(CHECKPOINT_FILE, completed)
            success_count += 1
        else:
            print(f"  ❌ Failed after {duration:.1f}s\n")
            fail_count += 1

    overall_duration = time.time() - overall_start

    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ")
    print("=" * 60)
    print(f"✅ Thành công: {success_count}/{len(remaining)}")
    print(f"❌ Thất bại: {fail_count}/{len(remaining)}")
    print(
        f"⏱️  Tổng thời gian: {overall_duration:.1f}s ({overall_duration/60:.1f} phút)"
    )

    # Tính dung lượng
    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.wav"))
    print(f"💾 Tổng dung lượng: {total_size / 1024 / 1024:.1f} MB")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
