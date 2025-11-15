# ⚡ QUICK START - TTS WORKER

## 🚀 Chạy ngay trong 3 bước

### **Bước 1: Chạy server (trên server 10.0.67.77)**

```bash
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./start_with_loadbalancer.sh
```

### **Bước 2: Chạy worker (trên Mac Mini)**

```bash
cd /Users/tvan.huu/Desktop/F5-TTS-Vietnamese
python tts_worker.py --workers 2 --srt srt.srt
```

### **Bước 3: Xem kết quả**

```bash
ls -lh output_audio/
```

**→ Xong!** 🎉

---

## 📊 Output mẫu

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
```

---

## 🔄 Nếu bị lỗi giữa chừng

### **Chỉ cần chạy lại:**

```bash
python tts_worker.py --workers 2 --srt srt.srt
```

**→ Tự động tiếp tục từ chỗ dừng!** ✅

---

## ⚙️ Tùy chỉnh

### **Chạy nhanh hơn (3 workers):**

```bash
python tts_worker.py --workers 3 --srt srt.srt
```

### **Server khác:**

```bash
python tts_worker.py --workers 2 --srt srt.srt --server http://10.0.67.77:5000
```

### **Tốc độ đọc khác:**

```bash
python tts_worker.py --workers 2 --srt srt.srt --speed 1.0
```

---

## 📋 Xem checkpoint

```bash
cat output_audio/.checkpoint.json | python -m json.tool
```

---

## 🧪 Test nhanh

```bash
./test_worker.sh
```

---

## 📚 Đọc thêm

- **`README_TTS_WORKER.md`** - Hướng dẫn đầy đủ
- **`HUONG_DAN_TTS_WORKER.md`** - Chi tiết tính năng
- **`CHECKPOINT_FORMAT.md`** - Format checkpoint
- **`SO_SANH_FILES.md`** - So sánh với file cũ
- **`TONG_KET_TTS_WORKER.md`** - Tổng kết

---

**Chúc bạn thành công!** 🚀

