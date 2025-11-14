# 📚 INDEX - TTS WORKER

## 🎯 Bạn muốn làm gì?

### **1. Chạy ngay (không cần đọc gì)** → [`QUICK_START_WORKER.md`](QUICK_START_WORKER.md)

### **2. Hiểu cách dùng** → [`README_TTS_WORKER.md`](README_TTS_WORKER.md)

### **3. Hiểu chi tiết tính năng** → [`HUONG_DAN_TTS_WORKER.md`](HUONG_DAN_TTS_WORKER.md)

### **4. Hiểu checkpoint** → [`CHECKPOINT_FORMAT.md`](CHECKPOINT_FORMAT.md)

### **5. So sánh với file cũ** → [`SO_SANH_FILES.md`](SO_SANH_FILES.md)

### **6. Xem tổng kết** → [`TONG_KET_TTS_WORKER.md`](TONG_KET_TTS_WORKER.md)

---

## 📁 Danh sách files

### **File chính:**

| File | Mô tả |
|------|-------|
| **`tts_worker.py`** | File Python chính - Multi-threaded TTS worker |
| `test_worker.sh` | Script test nhanh |

### **File hướng dẫn:**

| File | Mô tả | Khi nào đọc |
|------|-------|-------------|
| `QUICK_START_WORKER.md` | Quick start | Muốn chạy ngay |
| `README_TTS_WORKER.md` | Hướng dẫn cơ bản | Muốn hiểu cách dùng |
| `HUONG_DAN_TTS_WORKER.md` | Hướng dẫn chi tiết | Muốn hiểu sâu |
| `CHECKPOINT_FORMAT.md` | Format checkpoint | Muốn hiểu checkpoint |
| `SO_SANH_FILES.md` | So sánh files | Muốn biết khác gì file cũ |
| `TONG_KET_TTS_WORKER.md` | Tổng kết | Muốn xem tổng quan |
| `INDEX_TTS_WORKER.md` | Index (file này) | Muốn tìm file |

---

## 🚀 QUICK REFERENCE

### **Chạy cơ bản:**

```bash
python tts_worker.py --workers 2 --srt srt.srt
```

### **Chạy nhanh hơn:**

```bash
python tts_worker.py --workers 3 --srt srt.srt
```

### **Resume sau khi bị lỗi:**

```bash
python tts_worker.py --workers 2 --srt srt.srt
```

### **Xem checkpoint:**

```bash
cat output_audio/.checkpoint.json | python -m json.tool
```

### **Test nhanh:**

```bash
./test_worker.sh
```

---

## 📊 Tính năng chính

- ✅ **Multi-threading** - Nhiều workers song song
- ✅ **Worker pool** - Tự động lấy task tiếp theo
- ✅ **Checkpoint** - Lưu tiến trình
- ✅ **Resume** - Tiếp tục khi bị lỗi
- ✅ **Progress tracking** - Theo dõi tiến trình
- ✅ **ETA** - Tính thời gian còn lại

---

## 🎯 Use cases

| Use case | File nên dùng |
|----------|---------------|
| Xử lý SRT thực tế | `tts_worker.py` ⭐ |
| Test đơn giản | `tts_client.py` |
| Test Load Balancer | `test_requests.py` |

---

## 🔄 Workflow

```
1. Chạy server (10.0.67.77)
   → ./start_with_loadbalancer.sh

2. Chạy worker (Mac Mini)
   → python tts_worker.py --workers 2 --srt srt.srt

3. Nếu bị lỗi → Chạy lại
   → python tts_worker.py --workers 2 --srt srt.srt

4. Xem kết quả
   → ls -lh output_audio/
```

---

## 📈 Performance

| Workers | Thời gian (150 tasks) |
|---------|-----------------------|
| 1 | ~62.5 phút |
| 2 | ~31.3 phút |
| 3 | ~20.8 phút |

---

## 🛑 Troubleshooting

### **Lỗi: Mất mạng**
→ Chạy lại, tự động resume

### **Lỗi: Ctrl+C**
→ Chạy lại, tự động resume

### **Lỗi: Server lỗi**
→ Restart server, chạy lại client

---

## 📞 Liên hệ

Nếu có vấn đề, xem:
1. `README_TTS_WORKER.md` - Hướng dẫn cơ bản
2. `HUONG_DAN_TTS_WORKER.md` - Hướng dẫn chi tiết
3. `CHECKPOINT_FORMAT.md` - Hiểu checkpoint

---

**Chúc bạn thành công!** 🚀

