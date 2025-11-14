#!/usr/bin/env python3
"""
Script để xử lý nhiều file SRT cùng lúc
Sử dụng multi-server load balancing

Usage:
    python batch_process.py file1.srt file2.srt file3.srt
    python batch_process.py *.srt
"""

import sys
import subprocess
from pathlib import Path
import time


def process_srt_file(srt_file, output_base_dir="batch_output"):
    """
    Xử lý 1 file SRT
    
    Args:
        srt_file: Đường dẫn file SRT
        output_base_dir: Thư mục gốc để lưu output
    
    Returns:
        bool: True nếu thành công
    """
    srt_path = Path(srt_file)
    
    if not srt_path.exists():
        print(f"❌ File không tồn tại: {srt_file}")
        return False
    
    # Tạo thư mục output riêng cho mỗi file SRT
    # Ví dụ: srt.srt → batch_output/srt/
    output_dir = Path(output_base_dir) / srt_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"🎬 Xử lý: {srt_path.name}")
    print(f"📂 Output: {output_dir}")
    print(f"{'='*60}\n")
    
    # Gọi tts_client_loadbalanced.py với tham số
    # (Cần sửa tts_client_loadbalanced.py để nhận command-line args)
    # Tạm thời dùng subprocess để chạy trực tiếp
    
    start_time = time.time()
    
    try:
        # Chạy client (giả sử đã sửa để nhận args)
        # Nếu chưa sửa, cần copy và modify code
        result = subprocess.run(
            [
                "python3",
                "tts_client_loadbalanced.py",
                "--srt", str(srt_path),
                "--output", str(output_dir),
            ],
            capture_output=True,
            text=True,
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Hoàn thành: {srt_path.name} ({duration:.1f}s)")
            return True
        else:
            print(f"❌ Lỗi khi xử lý {srt_path.name}")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py file1.srt file2.srt ...")
        print("       python batch_process.py *.srt")
        sys.exit(1)
    
    srt_files = sys.argv[1:]
    
    print(f"\n🚀 BATCH PROCESSING")
    print(f"{'='*60}")
    print(f"📁 Số file SRT: {len(srt_files)}")
    for i, f in enumerate(srt_files, 1):
        print(f"   {i}. {f}")
    print(f"{'='*60}\n")
    
    # Xử lý từng file
    results = []
    overall_start = time.time()
    
    for srt_file in srt_files:
        success = process_srt_file(srt_file)
        results.append((srt_file, success))
    
    overall_duration = time.time() - overall_start
    
    # Tổng kết
    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ TỔNG HỢP")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, success in results if success)
    fail_count = len(results) - success_count
    
    print(f"✅ Thành công: {success_count}/{len(results)}")
    print(f"❌ Thất bại: {fail_count}/{len(results)}")
    print(f"⏱️  Tổng thời gian: {overall_duration:.1f}s ({overall_duration/60:.1f} phút)")
    print(f"{'='*60}\n")
    
    # Chi tiết
    if fail_count > 0:
        print("❌ Các file thất bại:")
        for srt_file, success in results:
            if not success:
                print(f"   - {srt_file}")
        print()


if __name__ == "__main__":
    main()

