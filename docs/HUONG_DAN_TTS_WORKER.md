# 🚀 HƯỚNG DẪN TTS WORKER

## 🎯 Tính năng

`tts_worker.py` là file hoàn chỉnh kết hợp tất cả tính năng từ `tts_client.py` và `test_requests.py`:

### ✅ **Tính năng chính:**

1. **Multi-threaded Processing** - Chạy nhiều workers song song
2. **Worker Pool Pattern** - Worker xong → Tự động lấy task tiếp theo
3. **Checkpoint & Resume** - Lưu tiến trình, tiếp tục khi bị lỗi
4. **Progress Tracking** - Biết đang xử lý câu nào, còn bao nhiêu
5. **Error Handling** - Xử lý lỗi mạng, timeout, server error
6. **ETA Calculation** - Tính thời gian còn lại

---

## 🚀 CÁCH SỬ DỤNG

### **1. Chạy cơ bản với 2 workers**

```bash
python tts_worker.py --workers 2 --srt srt.srt
```

**Output:**
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
[Task 2] 📝 Text: một mặt là trước đó đã thực hiện...
```

---

### **2. Chạy với 3 workers (nhanh hơn)**

```bash
python tts_worker.py --workers 3 --srt srt.srt
```

**Lợi ích:**
- 2 workers → ~75 phút (150 tasks / 2 workers)
- 3 workers → ~50 phút (150 tasks / 3 workers)

---

### **3. Chạy với server khác**

```bash
# Với Load Balancer
python tts_worker.py --workers 3 --srt srt.srt --server http://10.0.67.77:8080

# Với single server
python tts_worker.py --workers 1 --srt srt.srt --server http://10.0.67.77:5000
```

---

### **4. Resume sau khi bị lỗi**

```bash
# Lần 1: Chạy được 50 tasks rồi bị lỗi mạng
python tts_worker.py --workers 2 --srt srt.srt
# ... xử lý được 50/150 tasks
# Ctrl+C hoặc lỗi mạng

# Lần 2: Chạy lại → Tự động tiếp tục từ task 51
python tts_worker.py --workers 2 --srt srt.srt

# Output:
# ✅ Completed: 50
# 🔄 Remaining: 100
# 🔄 Bắt đầu xử lý 100 tasks với 2 workers...
```

---

## 📊 CHECKPOINT FORMAT

File checkpoint: `output_audio/.checkpoint.json`

```json
{
  "completed": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  "in_progress": [10, 11],
  "failed": [
    {
      "index": 15,
      "error": "Connection timeout",
      "timestamp": "2025-11-14T22:00:15.123456"
    }
  ],
  "last_updated": "2025-11-14T22:00:30.123456"
}
```

### **Giải thích:**

| Field | Mô tả |
|-------|-------|
| `completed` | Danh sách index các task đã hoàn thành |
| `in_progress` | Danh sách index các task đang xử lý |
| `failed` | Danh sách các task bị lỗi (với thông tin lỗi) |
| `last_updated` | Thời gian cập nhật checkpoint cuối cùng |

---

## 🔄 WORKER POOL PATTERN

### **Cách hoạt động:**

```
Ban đầu:
Worker 1 → Task 0
Worker 2 → Task 1

Sau khi Worker 1 xong Task 0:
Worker 1 → Task 2  ← Tự động lấy task tiếp theo!
Worker 2 → Task 1 (vẫn đang xử lý)

Sau khi Worker 2 xong Task 1:
Worker 1 → Task 2 (vẫn đang xử lý)
Worker 2 → Task 3  ← Tự động lấy task tiếp theo!

... cứ thế cho đến hết
```

**→ Luôn giữ tất cả workers bận rộn!**

---

## 📈 PROGRESS TRACKING

### **Thông tin hiển thị:**

```
📊 Progress: 45/150 completed, 2 failed, 2 in progress
⏱️  Elapsed: 22.5m, ETA: 52.5m
```

| Thông tin | Mô tả |
|-----------|-------|
| `45/150 completed` | Đã hoàn thành 45/150 tasks |
| `2 failed` | 2 tasks bị lỗi |
| `2 in progress` | 2 tasks đang xử lý |
| `Elapsed: 22.5m` | Đã chạy được 22.5 phút |
| `ETA: 52.5m` | Còn khoảng 52.5 phút nữa |

---

## 🔧 CÁC THAM SỐ

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--srt` | Đường dẫn file SRT | **Bắt buộc** |
| `--workers` | Số workers song song | 2 |
| `--server` | URL server/Load Balancer | `http://10.0.67.77:8080` |
| `--speed` | Tốc độ đọc | 0.75 |
| `--output` | Thư mục output | `output_audio` |
| `--checkpoint` | File checkpoint | `<output>/.checkpoint.json` |

---

## 💡 USE CASES

### **Use Case 1: Xử lý file SRT lớn**

```bash
# File SRT có 500 đoạn, dùng 3 workers
python tts_worker.py --workers 3 --srt large.srt

# Ước tính: 500 tasks / 3 workers × 25s/task ≈ 70 phút
```

---

### **Use Case 2: Resume sau khi bị lỗi mạng**

```bash
# Lần 1: Chạy được 200/500 tasks rồi mất mạng
python tts_worker.py --workers 3 --srt large.srt
# ... mất mạng

# Lần 2: Chạy lại → Tự động tiếp tục từ task 201
python tts_worker.py --workers 3 --srt large.srt
# ✅ Completed: 200
# 🔄 Remaining: 300
```

---

### **Use Case 3: Xử lý lại các task bị lỗi**

```bash
# Xem checkpoint để biết task nào bị lỗi
cat output_audio/.checkpoint.json

# Xóa task bị lỗi khỏi completed để xử lý lại
# Hoặc xóa toàn bộ checkpoint để chạy lại từ đầu
rm output_audio/.checkpoint.json

# Chạy lại
python tts_worker.py --workers 2 --srt srt.srt
```

---

## 🛑 XỬ LÝ LỖI

### **Lỗi 1: Mất mạng giữa chừng**

```
[Task 45] ❌ Exception: Connection timeout
📊 Progress: 44/150 completed, 1 failed, 1 in progress
```

**Giải pháp:**
```bash
# Chờ mạng ổn định rồi chạy lại
python tts_worker.py --workers 2 --srt srt.srt
# → Tự động tiếp tục từ task 46
```

---

### **Lỗi 2: Server bị lỗi**

```
[Task 50] ❌ Lỗi: HTTP 500
```

**Giải pháp:**
```bash
# Kiểm tra server
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./stop_all.sh
./start_with_loadbalancer.sh

# Chạy lại client
python tts_worker.py --workers 2 --srt srt.srt
```

---

### **Lỗi 3: Ctrl+C (gián đoạn bởi user)**

```
^C
⚠️  Bị gián đoạn bởi user (Ctrl+C)
💾 Checkpoint đã được lưu. Chạy lại script để tiếp tục.
```

**Giải pháp:**
```bash
# Chạy lại để tiếp tục
python tts_worker.py --workers 2 --srt srt.srt
```

---

## 📝 TÓM TẮT

### **So sánh với file cũ:**

| Tính năng | `tts_client.py` | `test_requests.py` | `tts_worker.py` ✅ |
|-----------|-----------------|--------------------|--------------------|
| Multi-threading | ❌ | ✅ | ✅ |
| Worker pool | ❌ | ❌ | ✅ |
| Checkpoint | ✅ | ❌ | ✅ |
| Resume | ✅ | ❌ | ✅ |
| Progress tracking | ❌ | ❌ | ✅ |
| ETA calculation | ❌ | ❌ | ✅ |
| Error handling | ✅ | ✅ | ✅ |
| In-progress tracking | ❌ | ❌ | ✅ |

---

**Chúc bạn xử lý thành công!** 🚀

