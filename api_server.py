"""
Flask API Server cho F5-TTS với Queue System
Model được khởi tạo 1 lần khi server start, sau đó tái sử dụng cho mọi request
Queue system cho phép xử lý nhiều request song song một cách an toàn
"""

from flask import Flask, request, jsonify, send_file
import sys
from pathlib import Path
import uuid
import os
import threading
import queue
import time
from datetime import datetime
import argparse

# Thêm đường dẫn src vào sys.path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from f5_tts.api import F5TTS

app = Flask(__name__)

# ====== QUEUE SYSTEM ======
# Queue để lưu các request đang chờ xử lý
request_queue = queue.Queue()

# Dictionary để lưu kết quả của các request
results = {}

# Lock để đảm bảo thread-safe khi truy cập model
model_lock = threading.Lock()

# Thống kê
stats = {
    "total_requests": 0,
    "completed_requests": 0,
    "failed_requests": 0,
    "queue_size": 0,
    "processing": False,
}

# ====== KHỞI TẠO MODEL 1 LẦN KHI SERVER START ======
print("🟢 Đang khởi tạo F5-TTS model...")

# Lấy đường dẫn thư mục hiện tại (root của project)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn relative từ root
CKPT_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "model_last.pt")
VOCAB_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "config.json")
DEFAULT_REF_AUDIO = "ref3.mp3"
DEFAULT_REF_TEXT = "hiệu quả là có thể khống chế đại tiện của mục tiêu"

print(f"📂 Model checkpoint: {CKPT_FILE}")
print(f"📂 Vocab file: {VOCAB_FILE}")

# Model global - khởi tạo 1 lần duy nhất
tts_model = F5TTS(
    model="F5TTS_Base",
    ckpt_file=CKPT_FILE,
    vocab_file=VOCAB_FILE,
)

print("✅ Model đã sẵn sàng! Server có thể nhận request.\n")

# Tạo thư mục lưu output
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_queue():
    """
    Worker thread để xử lý các request trong queue
    Chạy liên tục và xử lý từng request một
    """
    print("🔄 Queue worker started...")

    while True:
        try:
            # Lấy request từ queue (block nếu queue rỗng)
            job = request_queue.get(timeout=1)

            if job is None:  # Poison pill để dừng worker
                break

            request_id = job["request_id"]
            text = job["text"]
            ref_audio = job["ref_audio"]
            ref_text = job["ref_text"]
            speed = job["speed"]
            output_path = job["output_path"]

            stats["processing"] = True
            stats["queue_size"] = request_queue.qsize()

            print(f"🔊 Processing [{request_id}]: {text[:50]}...")

            try:
                # Sử dụng lock để đảm bảo chỉ 1 thread truy cập model tại 1 thời điểm
                with model_lock:
                    start_time = time.time()

                    wav, sr, spec = tts_model.infer(
                        ref_file=ref_audio,
                        ref_text=ref_text,
                        gen_text=text,
                        file_wave=str(output_path),
                        speed=speed,
                    )

                    duration = time.time() - start_time

                # Lưu kết quả thành công
                results[request_id] = {
                    "status": "completed",
                    "output_path": output_path,
                    "sample_rate": sr,
                    "duration": len(wav) / sr,
                    "processing_time": duration,
                    "error": None,
                }

                stats["completed_requests"] += 1
                print(f"   ✅ Completed [{request_id}] in {duration:.2f}s")

            except Exception as e:
                # Lưu kết quả lỗi
                results[request_id] = {"status": "failed", "error": str(e)}
                stats["failed_requests"] += 1
                print(f"   ❌ Failed [{request_id}]: {str(e)}")

            finally:
                stats["processing"] = False
                request_queue.task_done()

        except queue.Empty:
            # Queue rỗng, tiếp tục chờ
            stats["processing"] = False
            stats["queue_size"] = 0
            continue
        except Exception as e:
            print(f"❌ Queue worker error: {str(e)}")


# Khởi động worker thread
worker_thread = threading.Thread(target=process_queue, daemon=True)
worker_thread.start()


@app.route("/health", methods=["GET"])
def health_check():
    """Kiểm tra server có hoạt động không"""
    return jsonify(
        {
            "status": "ok",
            "model": "F5-TTS Vietnamese",
            "message": "Model đã được load và sẵn sàng",
            "stats": stats,
        }
    )


@app.route("/tts", methods=["POST"])
def text_to_speech():
    """
    API endpoint để chuyển text thành speech (với queue system)

    Request body (JSON):
    {
        "text": "Văn bản cần chuyển thành giọng nói",
        "ref_audio": "ref3.mp3" (optional),
        "ref_text": "..." (optional),
        "speed": 1.0 (optional),
        "async": false (optional - nếu true thì trả về request_id ngay)
    }

    Response:
    - File audio .wav (nếu async=false)
    - JSON với request_id (nếu async=true)
    """
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        ref_audio = data.get("ref_audio", DEFAULT_REF_AUDIO)
        ref_text = data.get("ref_text", DEFAULT_REF_TEXT)
        speed = data.get("speed", 1.0)
        is_async = data.get("async", False)

        # Tạo request ID và output path
        request_id = str(uuid.uuid4())
        output_filename = f"{request_id}.wav"
        output_path = OUTPUT_DIR / output_filename

        # Tạo job và thêm vào queue
        job = {
            "request_id": request_id,
            "text": text,
            "ref_audio": ref_audio,
            "ref_text": ref_text,
            "speed": speed,
            "output_path": output_path,
        }

        request_queue.put(job)
        stats["total_requests"] += 1
        stats["queue_size"] = request_queue.qsize()

        print(
            f"� Queued [{request_id}]: {text[:50]}... (Queue size: {stats['queue_size']})"
        )

        # Nếu async, trả về request_id ngay
        if is_async:
            return (
                jsonify(
                    {
                        "request_id": request_id,
                        "status": "queued",
                        "queue_position": stats["queue_size"],
                    }
                ),
                202,
            )

        # Nếu sync, đợi cho đến khi xử lý xong
        max_wait = 300  # Tối đa 5 phút
        start_wait = time.time()

        while request_id not in results:
            if time.time() - start_wait > max_wait:
                return jsonify({"error": "Request timeout"}), 504
            time.sleep(0.1)

        result = results[request_id]

        # Xóa kết quả khỏi memory sau khi lấy
        del results[request_id]

        if result["status"] == "completed":
            # Trả về file audio
            return send_file(
                result["output_path"],
                mimetype="audio/wav",
                as_attachment=True,
                download_name=output_filename,
            )
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/tts/status/<request_id>", methods=["GET"])
def check_status(request_id):
    """
    Kiểm tra trạng thái của request

    Response:
    {
        "request_id": "xxx",
        "status": "queued" | "processing" | "completed" | "failed" | "not_found",
        "result": {...} (nếu completed)
    }
    """
    if request_id in results:
        result = results[request_id]
        return jsonify(
            {
                "request_id": request_id,
                "status": result["status"],
                "result": result if result["status"] == "completed" else None,
                "error": result.get("error"),
            }
        )
    else:
        # Check if still in queue
        return (
            jsonify(
                {
                    "request_id": request_id,
                    "status": "not_found",
                    "message": "Request not found or already retrieved",
                }
            ),
            404,
        )


@app.route("/tts/json", methods=["POST"])
def text_to_speech_json():
    """
    API endpoint trả về thông tin JSON thay vì file

    Response:
    {
        "success": true,
        "file_path": "outputs/xxx.wav",
        "sample_rate": 24000,
        "duration": 2.5
    }
    """
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"]
        ref_audio = data.get("ref_audio", DEFAULT_REF_AUDIO)
        ref_text = data.get("ref_text", DEFAULT_REF_TEXT)
        speed = data.get("speed", 1.0)

        output_filename = f"{uuid.uuid4()}.wav"
        output_path = OUTPUT_DIR / output_filename

        # Sử dụng model đã được khởi tạo sẵn
        wav, sr, spec = tts_model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            file_wave=str(output_path),
            speed=speed,
        )

        duration = len(wav) / sr

        return jsonify(
            {
                "success": True,
                "file_path": str(output_path),
                "sample_rate": sr,
                "duration": duration,
                "text": text,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="F5-TTS API Server với Queue System")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port để chạy server (default: 5000)"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host để bind (default: 0.0.0.0)"
    )
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print(f"🚀 F5-TTS API Server với Queue System [Port {args.port}]")
    print("=" * 50)
    print("Endpoints:")
    print("  - GET  /health              : Kiểm tra server + stats")
    print("  - POST /tts                 : Tạo audio (sync/async)")
    print("  - GET  /tts/status/<id>     : Kiểm tra trạng thái request")
    print("  - POST /tts/json            : Tạo audio (trả về JSON)")
    print("\nQueue System:")
    print("  ✅ Hỗ trợ nhiều request đồng thời")
    print("  ✅ Xử lý tuần tự để tránh conflict")
    print("  ✅ Có thể dùng async mode để không chờ")
    print("=" * 50 + "\n")

    # Chạy server
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
