# 🎉 SAU KHI CHẠY XONG `tts_client_loadbalanced.py`

## ✅ Kết quả bạn nhận được:

### 1. **Thư mục output_audio/**

```
output_audio/
├── audio_0001.wav  # Đoạn 1
├── audio_0002.wav  # Đoạn 2
├── audio_0003.wav  # Đoạn 3
├── ...
└── audio_0010.wav  # Đoạn 10
```

### 2. **File checkpoint**

```
output_audio/.checkpoint.json  # Lưu tiến trình (để resume nếu bị gián đoạn)
```

### 3. **Thống kê hiển thị trên terminal**

```
📊 KẾT QUẢ
============================================================
✅ Thành công: 10/10
❌ Thất bại: 0/10
⏱️  Tổng thời gian: 76.8s (1.3 phút)
💾 Tổng dung lượng: 45.2 MB
🚀 Tăng tốc: ~3x so với 1 server
============================================================
```

---

## 🎯 BẠN CẦN LÀM GÌ TIẾP THEO?

### **Option 1: Nghe thử audio** 🎧

```bash
# Nghe file đầu tiên
open output_audio/audio_0001.wav

# Hoặc mở thư mục
open output_audio/
```

**Kiểm tra:**
- ✅ Chất lượng giọng nói
- ✅ Tốc độ đọc (speed = 0.75)
- ✅ Phát âm tiếng Việt
- ✅ Độ tự nhiên

---

### **Option 2: Xử lý file SRT khác** 🔄

Nếu bạn có file SRT khác cần xử lý:

#### **Cách 1: Sửa file `tts_client_loadbalanced.py`**

Mở file và sửa dòng 123:

```python
# Cũ
SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"

# Mới
SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/file_moi.srt"
```

Sau đó chạy lại:
```bash
python tts_client_loadbalanced.py
```

#### **Cách 2: Copy file SRT vào thư mục**

```bash
# Copy file SRT mới vào
cp /path/to/file_moi.srt /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/

# Sửa tên trong script
# Chạy lại
python tts_client_loadbalanced.py
```

---

### **Option 3: Ghép audio vào video** 🎬

Nếu bạn có video gốc và muốn thay audio:

#### **Với 1 file audio:**

```bash
ffmpeg -i video_goc.mp4 -i output_audio/audio_0001.wav \
       -c:v copy -map 0:v:0 -map 1:a:0 \
       output_video.mp4
```

#### **Với nhiều file audio (ghép thành 1 file):**

```bash
# Bước 1: Tạo file list
cat > filelist.txt << EOF
file 'output_audio/audio_0001.wav'
file 'output_audio/audio_0002.wav'
file 'output_audio/audio_0003.wav'
file 'output_audio/audio_0004.wav'
file 'output_audio/audio_0005.wav'
file 'output_audio/audio_0006.wav'
file 'output_audio/audio_0007.wav'
file 'output_audio/audio_0008.wav'
file 'output_audio/audio_0009.wav'
file 'output_audio/audio_0010.wav'
EOF

# Bước 2: Ghép audio
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output_full_audio.wav

# Bước 3: Ghép vào video
ffmpeg -i video_goc.mp4 -i output_full_audio.wav \
       -c:v copy -c:a aac -strict experimental \
       video_final.mp4
```

---

### **Option 4: Kiểm tra chất lượng** ✅

```bash
# Xem kích thước files
ls -lh output_audio/

# Xem thông tin audio
ffprobe output_audio/audio_0001.wav

# Đếm số files
ls output_audio/*.wav | wc -l
```

---

### **Option 5: Backup kết quả** 💾

```bash
# Nén thành ZIP
zip -r output_audio_$(date +%Y%m%d_%H%M%S).zip output_audio/

# Hoặc copy sang nơi khác
cp -r output_audio/ /path/to/backup/
```

---

### **Option 6: Dọn dẹp và chạy lại** 🧹

Nếu muốn xử lý lại từ đầu:

```bash
# Xóa output cũ
rm -rf output_audio/

# Chạy lại
python tts_client_loadbalanced.py
```

Hoặc chỉ xóa checkpoint để chạy lại:

```bash
# Xóa checkpoint (giữ lại audio đã tạo)
rm output_audio/.checkpoint.json

# Chạy lại (sẽ skip các file đã tồn tại)
python tts_client_loadbalanced.py
```

---

### **Option 7: Tắt servers (nếu không dùng nữa)** 🛑

Nếu đã xử lý xong và không cần servers nữa:

**Trên máy server (10.0.67.77):**

```bash
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./stop_servers.sh
```

---

## 📊 BENCHMARK (Nếu muốn test hiệu năng)

Chạy benchmark để so sánh 1 server vs 3 servers:

```bash
python benchmark_multiserver.py
```

Kết quả mong đợi:
```
📊 COMPARISON
============================================================
1 Server:  230.5s (3.8 phút)
3 Servers: 76.8s (1.3 phút)

🚀 Speedup: 3.00x
⏱️  Time saved: 153.7s (2.6 phút)
============================================================
```

---

## 🎓 NÂNG CAO

### **Tăng số lượng servers lên 4 hoặc 5**

Nếu máy server có đủ RAM (mỗi server ~3-4GB):

**Trên server:**
```bash
# Sửa start_multiple_servers.sh
# Dòng 15: NUM_SERVERS=3 → NUM_SERVERS=4

# Restart
./stop_servers.sh
VENV_PATH=/path/to/venv ./start_multiple_servers.sh
```

**Trên client:**
```python
# Sửa tts_client_loadbalanced.py
SERVERS = [
    "http://10.0.67.77:5000",
    "http://10.0.67.77:5001",
    "http://10.0.67.77:5002",
    "http://10.0.67.77:5003",  # Thêm server thứ 4
]
```

---

## 🆘 NẾU GẶP VẤN ĐỀ

### **Một số file bị lỗi**

Kiểm tra checkpoint:
```bash
cat output_audio/.checkpoint.json
```

Chạy lại (sẽ tự động retry các file lỗi):
```bash
python tts_client_loadbalanced.py
```

### **Muốn xử lý lại 1 file cụ thể**

Xóa file đó và chạy lại:
```bash
rm output_audio/audio_0005.wav
python tts_client_loadbalanced.py
```

---

## 🎉 TÓM TẮT

Sau khi chạy xong `tts_client_loadbalanced.py`:

1. ✅ **Kiểm tra** output_audio/ có đủ 10 files
2. 🎧 **Nghe thử** vài file để kiểm tra chất lượng
3. 🔄 **Xử lý file SRT khác** (nếu có)
4. 🎬 **Ghép audio vào video** (nếu cần)
5. 💾 **Backup** kết quả
6. 🛑 **Tắt servers** (nếu không dùng nữa)

**Hoàn thành!** 🚀

