#!/usr/bin/env python3
"""
TTS Worker - Multi-threaded TTS Client with Checkpoint & Resume
Xử lý file SRT với nhiều workers song song, tự động resume khi bị gián đoạn

Features:
- Multi-threaded processing (configurable workers)
- Checkpoint & Resume (lưu tiến trình, tiếp tục khi bị lỗi)
- Worker pool pattern (worker xong → tự động lấy task tiếp theo)
- Progress tracking (biết đang xử lý câu nào)

Usage:
    # Chạy với 1 workers, server khác
    python3 tts_worker.py --workers 1 --server http://10.0.67.77:5000

    # Chạy với 2 workers
    python tts_worker.py --workers 2 --srt srt.srt

    # Chạy với 3 workers, server khác
    python tts_worker.py --workers 3 --srt srt.srt --server http://10.0.67.77:8080

    # Resume sau khi bị lỗi (tự động đọc checkpoint)
    python tts_worker.py --workers 2 --srt srt.srt
"""

import requests
import json
import re
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime


class TTSWorker:
    """TTS Worker với checkpoint và multi-threading"""

    def __init__(
        self,
        srt_file,
        output_dir,
        checkpoint_file,
        server_url,
        speed=0.75,
        num_workers=2,
    ):
        self.srt_file = Path(srt_file)
        self.output_dir = Path(output_dir)
        self.checkpoint_file = Path(checkpoint_file)
        self.server_url = server_url
        self.speed = speed
        self.num_workers = num_workers

        # Thread-safe locks
        self.checkpoint_lock = Lock()
        self.stats_lock = Lock()

        # Statistics
        self.stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": set(),
            "start_time": None,
        }

        # Load checkpoint
        self.checkpoint = self.load_checkpoint()

        # Parse SRT
        self.texts = self.parse_srt()

        print(f"\n{'='*60}")
        print(f"🚀 TTS WORKER - Multi-threaded Processing")
        print(f"{'='*60}")
        print(f"📄 SRT File: {self.srt_file}")
        print(f"📂 Output: {self.output_dir}")
        print(f"🌐 Server: {self.server_url}")
        print(f"⚡ Speed: {self.speed}")
        print(f"👷 Workers: {self.num_workers}")
        print(f"📝 Total texts: {len(self.texts)}")
        print(f"✅ Completed: {len(self.checkpoint['completed'])}")
        print(f"🔄 Remaining: {len(self.texts) - len(self.checkpoint['completed'])}")
        print(f"{'='*60}\n")

    def parse_srt(self):
        """Parse SRT file và trả về list các đoạn text"""
        with open(self.srt_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Pattern để tìm text trong SRT
        pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.+?)(?=\n\n|\n\d+\n|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)
        texts = [match.strip().replace("\n", " ") for match in matches]

        return texts

    def load_checkpoint(self):
        """Load checkpoint từ file"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Đảm bảo có đầy đủ fields
                if "completed" not in data:
                    data["completed"] = []
                if "in_progress" not in data:
                    data["in_progress"] = []
                if "failed" not in data:
                    data["failed"] = []
                return data
        else:
            return {
                "completed": [],
                "in_progress": [],
                "failed": [],
                "last_updated": None,
            }

    def save_checkpoint(self):
        """Lưu checkpoint vào file (thread-safe)"""
        with self.checkpoint_lock:
            self.checkpoint["last_updated"] = datetime.now().isoformat()
            self.checkpoint["in_progress"] = list(self.stats["in_progress"])

            # Tạo thư mục nếu chưa có
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(self.checkpoint, f, indent=2, ensure_ascii=False)

    def mark_in_progress(self, index):
        """Đánh dấu task đang xử lý"""
        with self.stats_lock:
            self.stats["in_progress"].add(index)
        self.save_checkpoint()

    def mark_completed(self, index):
        """Đánh dấu task hoàn thành"""
        with self.stats_lock:
            self.stats["in_progress"].discard(index)
            self.stats["completed"] += 1

        with self.checkpoint_lock:
            if index not in self.checkpoint["completed"]:
                self.checkpoint["completed"].append(index)
                self.checkpoint["completed"].sort()

        self.save_checkpoint()

    def mark_failed(self, index, error):
        """Đánh dấu task thất bại"""
        with self.stats_lock:
            self.stats["in_progress"].discard(index)
            self.stats["failed"] += 1

        with self.checkpoint_lock:
            failed_entry = {
                "index": index,
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }
            self.checkpoint["failed"].append(failed_entry)

        self.save_checkpoint()

    def call_tts_api(self, text, index):
        """
        Gọi TTS API để chuyển đổi text thành audio

        Args:
            text: Text cần chuyển đổi
            index: Index của text trong SRT

        Returns:
            dict: Kết quả xử lý
        """
        output_path = self.output_dir / f"audio_{index:04d}.wav"

        start_time = time.time()

        try:
            print(f"[Task {index}] 🚀 Bắt đầu xử lý...")
            print(f"[Task {index}] 📝 Text: {text[:60]}...")

            # Đánh dấu đang xử lý
            self.mark_in_progress(index)

            # Gọi API
            payload = {
                "text": text,
                "speed": self.speed,
            }

            response = requests.post(
                f"{self.server_url}/tts",
                json=payload,
                timeout=120,
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                # Lưu file
                with open(output_path, "wb") as f:
                    f.write(response.content)

                file_size = len(response.content) / 1024 / 1024  # MB

                print(
                    f"[Task {index}] ✅ Thành công! ({duration:.1f}s, {file_size:.2f}MB)"
                )

                # Đánh dấu hoàn thành
                self.mark_completed(index)

                return {
                    "index": index,
                    "success": True,
                    "duration": duration,
                    "file_size": file_size,
                    "output_path": str(output_path),
                }
            else:
                error = f"HTTP {response.status_code}"
                print(f"[Task {index}] ❌ Lỗi: {error}")
                self.mark_failed(index, error)

                return {
                    "index": index,
                    "success": False,
                    "duration": duration,
                    "error": error,
                }

        except Exception as e:
            duration = time.time() - start_time
            print(f"[Task {index}] ❌ Exception: {e}")
            self.mark_failed(index, str(e))

            return {
                "index": index,
                "success": False,
                "duration": duration,
                "error": str(e),
            }

    def get_pending_tasks(self):
        """Lấy danh sách các task chưa hoàn thành"""
        completed_set = set(self.checkpoint["completed"])
        pending = [i for i in range(len(self.texts)) if i not in completed_set]
        return pending

    def run(self):
        """Chạy worker pool để xử lý tất cả tasks"""
        # Tạo thư mục output
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Lấy danh sách tasks chưa hoàn thành
        pending_tasks = self.get_pending_tasks()

        if not pending_tasks:
            print("✅ Tất cả tasks đã hoàn thành!")
            return

        print(
            f"🔄 Bắt đầu xử lý {len(pending_tasks)} tasks với {self.num_workers} workers...\n"
        )

        self.stats["total"] = len(pending_tasks)
        self.stats["start_time"] = time.time()

        results = []

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit initial batch
            futures = {}
            for i in range(min(self.num_workers, len(pending_tasks))):
                task_index = pending_tasks[i]
                text = self.texts[task_index]
                future = executor.submit(self.call_tts_api, text, task_index)
                futures[future] = task_index

            next_task_idx = self.num_workers

            # Process as they complete
            while futures:
                done = as_completed(futures)
                for future in done:
                    task_index = futures.pop(future)
                    result = future.result()
                    results.append(result)

                    # Print progress
                    self.print_progress()

                    # Submit next task if available
                    if next_task_idx < len(pending_tasks):
                        new_task_index = pending_tasks[next_task_idx]
                        new_text = self.texts[new_task_index]
                        new_future = executor.submit(
                            self.call_tts_api, new_text, new_task_index
                        )
                        futures[new_future] = new_task_index
                        next_task_idx += 1
                        print(f"🔄 Worker freed! Submitting task {new_task_index}...\n")

                    break  # Process one at a time

        # Print final summary
        self.print_summary(results)

    def print_progress(self):
        """In tiến trình hiện tại"""
        with self.stats_lock:
            total = self.stats["total"]
            completed = self.stats["completed"]
            failed = self.stats["failed"]
            in_progress = len(self.stats["in_progress"])

            if self.stats["start_time"]:
                elapsed = time.time() - self.stats["start_time"]
                if completed > 0:
                    avg_time = elapsed / completed
                    remaining = total - completed - failed
                    eta = avg_time * remaining
                    print(
                        f"📊 Progress: {completed}/{total} completed, {failed} failed, {in_progress} in progress"
                    )
                    print(f"⏱️  Elapsed: {elapsed/60:.1f}m, ETA: {eta/60:.1f}m\n")

    def print_summary(self, results):
        """In tổng kết"""
        total_duration = time.time() - self.stats["start_time"]

        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        print(f"✅ Thành công: {self.stats['completed']}/{self.stats['total']}")
        print(f"❌ Thất bại: {self.stats['failed']}/{self.stats['total']}")
        print(f"⏱️  Tổng thời gian: {total_duration/60:.1f} phút")

        if self.stats["completed"] > 0:
            avg_time = total_duration / self.stats["completed"]
            print(f"⏱️  Trung bình: {avg_time:.1f}s/task")

        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="TTS Worker - Multi-threaded TTS processing with checkpoint"
    )

    SCRIPT_DIR = Path(__file__).resolve().parent
    SRT_FILE = SCRIPT_DIR / "srt.srt"

    parser.add_argument(
        "--srt",
        type=str,
        default=SRT_FILE,
        help="Đường dẫn đến file SRT",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Số lượng workers song song (default: 2)",
    )
    parser.add_argument(
        "--server",
        type=str,
        default="http://10.0.67.77:8080",
        help="URL của TTS server hoặc Load Balancer (default: http://10.0.67.77:8080)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.75,
        help="Tốc độ đọc (default: 0.75)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output_audio",
        help="Thư mục output (default: output_audio)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="File checkpoint (default: <output>/.checkpoint.json)",
    )

    args = parser.parse_args()

    # Xác định checkpoint file
    if args.checkpoint is None:
        checkpoint_file = Path(args.output) / ".checkpoint.json"
    else:
        checkpoint_file = Path(args.checkpoint)

    # Tạo worker và chạy
    worker = TTSWorker(
        srt_file=args.srt,
        output_dir=args.output,
        checkpoint_file=checkpoint_file,
        server_url=args.server,
        speed=args.speed,
        num_workers=args.workers,
    )

    try:
        worker.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Bị gián đoạn bởi user (Ctrl+C)")
        print("💾 Checkpoint đã được lưu. Chạy lại script để tiếp tục.\n")
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        print("💾 Checkpoint đã được lưu. Chạy lại script để tiếp tục.\n")
        raise


if __name__ == "__main__":
    main()
