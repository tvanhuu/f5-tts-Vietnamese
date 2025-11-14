# 📋 CHECKPOINT FORMAT - Chi tiết

## 🎯 Mục đích

File checkpoint lưu trạng thái xử lý để:
- ✅ Biết task nào đã hoàn thành
- ✅ Biết task nào đang xử lý
- ✅ Biết task nào bị lỗi
- ✅ Resume khi bị gián đoạn

---

## 📁 Vị trí file

```
output_audio/.checkpoint.json
```

---

## 📊 FORMAT

### **Ví dụ 1: Ban đầu (chưa xử lý gì)**

```json
{
  "completed": [],
  "in_progress": [],
  "failed": [],
  "last_updated": null
}
```

---

### **Ví dụ 2: Đang xử lý (2 workers)**

```json
{
  "completed": [0, 1, 2, 3, 4],
  "in_progress": [5, 6],
  "failed": [],
  "last_updated": "2025-11-14T22:00:30.123456"
}
```

**Giải thích:**
- Task 0-4: Đã hoàn thành ✅
- Task 5-6: Đang xử lý 🔄
- Chưa có task nào bị lỗi

---

### **Ví dụ 3: Có lỗi**

```json
{
  "completed": [0, 1, 2, 3, 4, 6, 7, 8],
  "in_progress": [9, 10],
  "failed": [
    {
      "index": 5,
      "error": "Connection timeout",
      "timestamp": "2025-11-14T22:00:15.123456"
    }
  ],
  "last_updated": "2025-11-14T22:01:00.123456"
}
```

**Giải thích:**
- Task 0-4, 6-8: Đã hoàn thành ✅
- Task 5: Bị lỗi ❌ (Connection timeout)
- Task 9-10: Đang xử lý 🔄

---

### **Ví dụ 4: Nhiều lỗi**

```json
{
  "completed": [0, 1, 2, 3, 4, 6, 7, 8, 11, 12],
  "in_progress": [13, 14],
  "failed": [
    {
      "index": 5,
      "error": "Connection timeout",
      "timestamp": "2025-11-14T22:00:15.123456"
    },
    {
      "index": 9,
      "error": "HTTP 500",
      "timestamp": "2025-11-14T22:00:45.123456"
    },
    {
      "index": 10,
      "error": "Read timeout",
      "timestamp": "2025-11-14T22:01:10.123456"
    }
  ],
  "last_updated": "2025-11-14T22:02:00.123456"
}
```

**Giải thích:**
- Task 5: Lỗi connection timeout
- Task 9: Lỗi server (HTTP 500)
- Task 10: Lỗi read timeout

---

## 🔄 CÁCH HOẠT ĐỘNG

### **Khi bắt đầu xử lý:**

```python
# Đọc checkpoint
checkpoint = load_checkpoint()
# → {"completed": [0, 1, 2], "in_progress": [], "failed": [...]}

# Tính pending tasks
all_tasks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
completed = [0, 1, 2]
pending = [3, 4, 5, 6, 7, 8, 9]  # Chưa hoàn thành

# Bắt đầu xử lý từ task 3
```

---

### **Khi task bắt đầu:**

```python
# Task 3 bắt đầu
mark_in_progress(3)

# Checkpoint:
{
  "completed": [0, 1, 2],
  "in_progress": [3],  # ← Thêm vào
  "failed": [],
  "last_updated": "2025-11-14T22:00:30.123456"
}
```

---

### **Khi task hoàn thành:**

```python
# Task 3 hoàn thành
mark_completed(3)

# Checkpoint:
{
  "completed": [0, 1, 2, 3],  # ← Thêm vào
  "in_progress": [],  # ← Xóa khỏi in_progress
  "failed": [],
  "last_updated": "2025-11-14T22:00:55.123456"
}
```

---

### **Khi task bị lỗi:**

```python
# Task 4 bị lỗi
mark_failed(4, "Connection timeout")

# Checkpoint:
{
  "completed": [0, 1, 2, 3],
  "in_progress": [],  # ← Xóa khỏi in_progress
  "failed": [  # ← Thêm vào
    {
      "index": 4,
      "error": "Connection timeout",
      "timestamp": "2025-11-14T22:01:20.123456"
    }
  ],
  "last_updated": "2025-11-14T22:01:20.123456"
}
```

---

## 🛠️ XỬ LÝ CHECKPOINT

### **1. Xem checkpoint**

```bash
cat output_audio/.checkpoint.json | python -m json.tool
```

---

### **2. Xóa checkpoint (chạy lại từ đầu)**

```bash
rm output_audio/.checkpoint.json
python tts_worker.py --workers 2 --srt srt.srt
```

---

### **3. Sửa checkpoint thủ công**

```bash
# Mở file
nano output_audio/.checkpoint.json

# Xóa task bị lỗi khỏi failed để xử lý lại
# Hoặc thêm task vào completed để bỏ qua
```

**Ví dụ:** Bỏ qua task 5 (không xử lý nữa)

```json
{
  "completed": [0, 1, 2, 3, 4, 5],  # ← Thêm 5 vào đây
  "in_progress": [],
  "failed": [
    // Xóa entry của task 5
  ],
  "last_updated": "2025-11-14T22:02:00.123456"
}
```

---

### **4. Xử lý lại các task bị lỗi**

```bash
# Xem task nào bị lỗi
cat output_audio/.checkpoint.json | grep -A 3 "failed"

# Xóa các task bị lỗi khỏi failed
# Chạy lại → Sẽ xử lý lại các task đó
python tts_worker.py --workers 2 --srt srt.srt
```

---

## 📊 THỐNG KÊ TỪ CHECKPOINT

### **Script Python để phân tích checkpoint:**

```python
import json

with open("output_audio/.checkpoint.json", "r") as f:
    checkpoint = json.load(f)

total_completed = len(checkpoint["completed"])
total_failed = len(checkpoint["failed"])
total_in_progress = len(checkpoint["in_progress"])

print(f"✅ Completed: {total_completed}")
print(f"❌ Failed: {total_failed}")
print(f"🔄 In progress: {total_in_progress}")

# Danh sách task bị lỗi
print("\n❌ Failed tasks:")
for failed in checkpoint["failed"]:
    print(f"  Task {failed['index']}: {failed['error']}")
```

---

## 🎯 TÓM TẮT

### **Các trường trong checkpoint:**

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `completed` | `list[int]` | Danh sách index task đã hoàn thành |
| `in_progress` | `list[int]` | Danh sách index task đang xử lý |
| `failed` | `list[dict]` | Danh sách task bị lỗi (với thông tin chi tiết) |
| `last_updated` | `string` | Timestamp cập nhật cuối cùng (ISO format) |

### **Failed entry format:**

```json
{
  "index": 5,
  "error": "Connection timeout",
  "timestamp": "2025-11-14T22:00:15.123456"
}
```

---

**Checkpoint giúp bạn không bao giờ mất công!** 💾

