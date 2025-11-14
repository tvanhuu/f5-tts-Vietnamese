#!/usr/bin/env python3
"""
Script để kết nối đến TTS API và chuyển đổi text từ file SRT thành audio
"""

import requests
import json
import re
import time
import os
from pathlib import Path


def parse_srt(srt_file_path):
    """
    Parse file SRT và trích xuất tất cả text

    Args:
        srt_file_path: Đường dẫn đến file SRT

    Returns:
        List các đoạn text từ file SRT
    """
    with open(srt_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern để tìm text (bỏ qua số thứ tự và timestamp)
    # Format SRT: số thứ tự -> timestamp -> text -> dòng trống
    lines = content.strip().split("\n")
    texts = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Bỏ qua dòng số thứ tự
        if line.isdigit():
            i += 1
            continue

        # Bỏ qua dòng timestamp
        if "-->" in line:
            i += 1
            # Dòng tiếp theo là text
            if i < len(lines) and lines[i].strip():
                texts.append(lines[i].strip())
            i += 1
            continue

        i += 1

    return texts


def call_tts_api(text, speed=0.75, api_url="http://10.0.67.77:5000/tts"):
    """
    Gọi TTS API để chuyển đổi text thành audio

    Args:
        text: Text cần chuyển đổi
        speed: Tốc độ đọc (mặc định 0.75)
        api_url: URL của TTS API

    Returns:
        Response object từ API
    """
    headers = {"Content-Type": "application/json"}

    data = {"text": text, "speed": speed}

    print(f"Đang gửi request đến {api_url}...")
    print(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")

    response = requests.post(api_url, headers=headers, json=data)

    return response


def save_audio(response, output_path):
    """
    Lưu audio từ response vào file

    Args:
        response: Response object từ API
        output_path: Đường dẫn file output
    """
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Đã lưu audio vào: {output_path}")
    else:
        print(f"✗ Lỗi: {response.status_code}")
        print(f"Response: {response.text}")


def load_checkpoint(checkpoint_file):
    """
    Load checkpoint để biết đã xử lý đến đâu

    Args:
        checkpoint_file: Đường dẫn file checkpoint

    Returns:
        Set các index đã xử lý xong
    """
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))
    return set()


def save_checkpoint(checkpoint_file, completed_indices):
    """
    Lưu checkpoint

    Args:
        checkpoint_file: Đường dẫn file checkpoint
        completed_indices: Set các index đã xử lý xong
    """
    with open(checkpoint_file, "w") as f:
        json.dump({"completed": list(completed_indices)}, f)


def format_time(seconds):
    """
    Chuyển đổi số giây thành định dạng phút:giây

    Args:
        seconds: Số giây

    Returns:
        String định dạng "X phút Y giây" hoặc "X giây"
    """
    minutes = int(seconds // 60)
    secs = seconds % 60

    if minutes > 0:
        return f"{minutes} phút {secs:.2f} giây"
    else:
        return f"{secs:.2f} giây"


def main():
    # Bắt đầu đo thời gian
    start_time = time.time()

    # Cấu hình
    # Lấy đường dẫn thư mục hiện tại
    SCRIPT_DIR = Path(__file__).resolve().parent
    SRT_FILE = SCRIPT_DIR / "srt.srt"
    API_URL = "http://10.0.67.77:5000/tts"
    SPEED = 0.75
    OUTPUT_DIR = "output_audio"
    CHECKPOINT_FILE = "output_audio/.checkpoint.json"

    # Tạo thư mục output nếu chưa có
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # Load checkpoint để xem đã xử lý đến đâu
    completed = load_checkpoint(CHECKPOINT_FILE)

    if completed:
        print(f"📌 Tìm thấy checkpoint: Đã hoàn thành {len(completed)} đoạn trước đó")
        print(f"🔄 Tiếp tục từ chỗ đã dừng...\n")

    # Parse file SRT
    print(f"Đang đọc file SRT: {SRT_FILE}")
    texts = parse_srt(SRT_FILE)
    print(f"Tìm thấy {len(texts)} đoạn text\n")

    # Hiển thị các đoạn text
    for i, text in enumerate(texts, 1):
        status = "✓" if i in completed else " "
        print(f"[{status}] {i}. {text}")

    print("\n" + "=" * 80 + "\n")

    # Đếm số đoạn cần xử lý
    remaining = len(texts) - len(completed)
    if remaining == 0:
        print("✓ Tất cả đã được xử lý xong!")
        return

    print(f"📊 Cần xử lý: {remaining}/{len(texts)} đoạn\n")

    # Xử lý từng đoạn text
    processed_count = 0
    try:
        for i, text in enumerate(texts, 1):
            # Bỏ qua nếu đã xử lý rồi
            if i in completed:
                continue

            print(f"\n[{i}/{len(texts)}] Đang xử lý...")

            # Đo thời gian cho từng request
            request_start = time.time()

            try:
                # Gọi API
                response = call_tts_api(text.lower(), speed=SPEED, api_url=API_URL)

                # Lưu audio
                output_file = f"{OUTPUT_DIR}/{i:03d}.wav"
                save_audio(response, output_file)

                # Đánh dấu đã hoàn thành
                completed.add(i)
                save_checkpoint(CHECKPOINT_FILE, completed)
                processed_count += 1

                # Hiển thị thời gian xử lý cho request này
                request_time = time.time() - request_start
                print(f"⏱️  Thời gian xử lý: {request_time:.2f} giây")
                print(f"✓ Đã lưu checkpoint ({len(completed)}/{len(texts)})")

            except requests.exceptions.RequestException as e:
                print(f"❌ Lỗi kết nối: {e}")
                print(f"💾 Đã lưu tiến trình. Chạy lại script để tiếp tục từ đoạn {i}")
                raise
            except Exception as e:
                print(f"❌ Lỗi: {e}")
                print(f"💾 Đã lưu tiến trình. Chạy lại script để tiếp tục từ đoạn {i}")
                raise

    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng")
        print(f"💾 Đã lưu tiến trình: {len(completed)}/{len(texts)} đoạn")
        print(f"🔄 Chạy lại script để tiếp tục")
        return

    # Tính tổng thời gian
    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 80)
    print(f"✓ Hoàn thành! Đã tạo {len(texts)} file audio trong thư mục '{OUTPUT_DIR}'")
    if processed_count > 0:
        print(f"⏱️  Tổng thời gian thực thi: {format_time(total_time)}")
        print(
            f"⏱️  Thời gian trung bình mỗi đoạn: {total_time/processed_count:.2f} giây"
        )

    # Xóa checkpoint khi hoàn thành
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print(f"🗑️  Đã xóa checkpoint")


if __name__ == "__main__":
    main()
