# 🚀 TTS WORKER - Quick Start

## 📝 Giới thiệu

`tts_worker.py` - File hoàn chỉnh để xử lý file SRT thành audio với:
- ✅ Multi-threading (nhiều workers song song)
- ✅ Worker pool pattern (tự động lấy task tiếp theo)
- ✅ Checkpoint & Resume (tiếp tục khi bị lỗi)
- ✅ Progress tracking (theo dõi tiến trình)

---

## 🚀 QUICK START

### **Bước 1: Chạy cơ bản**

```bash
python tts_worker.py --workers 2 --srt srt.srt
```

### **Bước 2: Xem kết quả**

```bash
ls -lh output_audio/
# audio_0000.wav
# audio_0001.wav
# audio_0002.wav
# ...
```

### **Bước 3: Nếu bị lỗi, chạy lại**

```bash
# Chạy lại → Tự động tiếp tục từ chỗ dừng
python tts_worker.py --workers 2 --srt srt.srt
```

---

## 📊 VÍ DỤ OUTPUT

```
============================================================
🚀 TTS WORKER - Multi-threaded Processing
============================================================
📄 SRT File: srt.srt
📂 Output: output_audio
🌐 Server: http://10.0.67.77:8080
⚡ Speed: 0.75
👷 Workers: 2
📝 Total texts: 150
✅ Completed: 0
🔄 Remaining: 150
============================================================

🔄 Bắt đầu xử lý 150 tasks với 2 workers...

[Task 0] 🚀 Bắt đầu xử lý...
[Task 0] 📝 Text: một mặt là trước đó đã thực hiện một lượt quy trình...
[Task 1] 🚀 Bắt đầu xử lý...
[Task 1] 📝 Text: cho ba môn công pháp cấp cao đặc biệt...

[Task 0] ✅ Thành công! (23.5s, 2.1MB)
📊 Progress: 1/150 completed, 0 failed, 1 in progress
⏱️  Elapsed: 0.4m, ETA: 58.5m

🔄 Worker freed! Submitting task 2...

[Task 2] 🚀 Bắt đầu xử lý...
```

---

## 🔄 WORKER POOL PATTERN

### **Cách hoạt động:**

```
Bước 1: Khởi tạo
Worker 1 → Task 0
Worker 2 → Task 1

Bước 2: Worker 1 xong Task 0
Worker 1 → Task 2  ← Tự động lấy task tiếp theo!
Worker 2 → Task 1 (vẫn đang xử lý)

Bước 3: Worker 2 xong Task 1
Worker 1 → Task 2 (vẫn đang xử lý)
Worker 2 → Task 3  ← Tự động lấy task tiếp theo!

... cứ thế cho đến hết
```

**→ Luôn giữ tất cả workers bận rộn!**

---

## 💾 CHECKPOINT

### **File checkpoint:**

```
output_audio/.checkpoint.json
```

### **Format:**

```json
{
  "completed": [0, 1, 2, 3, 4, 5],
  "in_progress": [6, 7],
  "failed": [
    {
      "index": 8,
      "error": "Connection timeout",
      "timestamp": "2025-11-14T22:00:15.123456"
    }
  ],
  "last_updated": "2025-11-14T22:00:30.123456"
}
```

### **Xem checkpoint:**

```bash
cat output_audio/.checkpoint.json | python -m json.tool
```

---

## 🎯 USE CASES

### **1. Xử lý file SRT lớn**

```bash
# 150 đoạn, 2 workers
python tts_worker.py --workers 2 --srt srt.srt
# Thời gian: ~75 phút

# 150 đoạn, 3 workers
python tts_worker.py --workers 3 --srt srt.srt
# Thời gian: ~50 phút
```

---

### **2. Resume sau khi bị lỗi**

```bash
# Lần 1: Chạy được 50/150 tasks rồi mất mạng
python tts_worker.py --workers 2 --srt srt.srt
# ... mất mạng

# Lần 2: Chạy lại → Tự động tiếp tục từ task 51
python tts_worker.py --workers 2 --srt srt.srt
# ✅ Completed: 50
# 🔄 Remaining: 100
```

---

### **3. Chạy với server khác**

```bash
# Load Balancer (3 servers)
python tts_worker.py --workers 3 --srt srt.srt --server http://10.0.67.77:8080

# Single server
python tts_worker.py --workers 1 --srt srt.srt --server http://10.0.67.77:5000
```

---

## 🔧 THAM SỐ

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--srt` | File SRT | **Bắt buộc** |
| `--workers` | Số workers | 2 |
| `--server` | URL server | `http://10.0.67.77:8080` |
| `--speed` | Tốc độ đọc | 0.75 |
| `--output` | Thư mục output | `output_audio` |
| `--checkpoint` | File checkpoint | `<output>/.checkpoint.json` |

---

## 🛑 XỬ LÝ LỖI

### **Lỗi 1: Mất mạng**

```bash
# Chờ mạng ổn rồi chạy lại
python tts_worker.py --workers 2 --srt srt.srt
```

### **Lỗi 2: Ctrl+C**

```bash
# Chạy lại để tiếp tục
python tts_worker.py --workers 2 --srt srt.srt
```

### **Lỗi 3: Server lỗi**

```bash
# Restart server rồi chạy lại client
python tts_worker.py --workers 2 --srt srt.srt
```

---

## 📚 TÀI LIỆU

- **`HUONG_DAN_TTS_WORKER.md`** - Hướng dẫn chi tiết
- **`CHECKPOINT_FORMAT.md`** - Format checkpoint
- **`README_TTS_WORKER.md`** - Quick start (file này)

---

## 🎉 TÓM TẮT

### **So với file cũ:**

| File | Multi-threading | Checkpoint | Worker Pool | Progress |
|------|-----------------|------------|-------------|----------|
| `tts_client.py` | ❌ | ✅ | ❌ | ❌ |
| `test_requests.py` | ✅ | ❌ | ❌ | ❌ |
| **`tts_worker.py`** | ✅ | ✅ | ✅ | ✅ |

### **Lợi ích:**

- ✅ **Nhanh hơn** - Multi-threading với worker pool
- ✅ **An toàn hơn** - Checkpoint & Resume
- ✅ **Rõ ràng hơn** - Progress tracking với ETA
- ✅ **Linh hoạt hơn** - Config workers, server, speed

---

**Chúc bạn xử lý thành công!** 🚀

