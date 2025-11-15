# 📋 HƯỚNG DẪN CHẠY MULTI-SERVER

## 🎯 Trên máy SERVER (10.0.67.77)

### Bước 1: Copy files từ Mac Mini

Từ **Mac Mini**, chạy:
```bash
scp start_multiple_servers.sh itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
scp stop_servers.sh itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
scp api_server.py itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
```

### Bước 2: SSH vào máy server

```bash
ssh itsw@10.0.67.77
```

### Bước 3: Chạy multi-server

Có 2 cách:

#### **CÁCH 1: Chỉ định đường dẫn virtual environment** (Khuyến nghị)

```bash
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Cấp quyền thực thi
chmod +x start_multiple_servers.sh stop_servers.sh

# Chạy với đường dẫn virtual environment
VENV_PATH=/Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env ./start_multiple_servers.sh
```

#### **CÁCH 2: Activate virtual environment trước**

```bash
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Activate virtual environment
source f5tts-env/bin/activate

# Chạy script (sẽ tự động dùng python trong venv)
chmod +x start_multiple_servers.sh stop_servers.sh
./start_multiple_servers.sh
```

### Bước 4: Kiểm tra logs

```bash
# Đợi vài giây
sleep 5

# Xem logs
tail -f logs/server_5000.log

# Hoặc xem tất cả
tail -f logs/server_*.log
```

### Bước 5: Đợi models load (~30 giây)

```bash
# Đợi
sleep 30

# Test servers
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

Nếu thấy response JSON với `"status": "ok"` → Thành công! ✅

---

## 🖥️ Trên máy CLIENT (Mac Mini)

### Bước 1: Kiểm tra file client

File `tts_client_loadbalanced.py` đã được cấu hình để gọi 3 servers:
```python
SERVERS = [
    "http://10.0.67.77:5000",
    "http://10.0.67.77:5001",
    "http://10.0.67.77:5002",
]
```

### Bước 2: Chạy client

```bash
cd /Users/tvan.huu/Desktop/F5-TTS-Vietnamese

# Activate virtual environment (nếu cần)
source f5tts-env/bin/activate

# Chạy client
python tts_client_loadbalanced.py
```

### Kết quả mong đợi:

```
🚀 TTS CLIENT với LOAD BALANCING
============================================================
📁 SRT File: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt
📂 Output: output_audio
⚡ Speed: 0.75
🖥️  Servers: 3
   1. http://10.0.67.77:5000
   2. http://10.0.67.77:5001
   3. http://10.0.67.77:5002
🔀 Max parallel requests: 3
============================================================

📊 Cần xử lý: 10/10 đoạn
⏱️  Ước tính: ~77s với 3 servers
   (So với 1 server: ~230s)
   → Tăng tốc: ~3x

🔄 Bắt đầu xử lý...

✅ [1/10] Server1 | 22.5s | cậu cao, nghe nói nhà cậu đã vỡ nợ...
✅ [2/10] Server2 | 23.1s | nhà tôi đúng là có chút vấn đề...
✅ [3/10] Server3 | 22.8s | tôi đã bán một ít đồ cổ...
...

📊 KẾT QUẢ
============================================================
✅ Thành công: 10/10
⏱️  Tổng thời gian: 76.8s (1.3 phút)
🚀 Tăng tốc: ~3x so với 1 server
============================================================
```

---

## 🛑 Dừng servers

Trên **máy server** (10.0.67.77):

```bash
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./stop_servers.sh
```

---

## ❓ Troubleshooting

### Lỗi: "virtual environment not found"

**Giải pháp:** Chỉ định đường dẫn virtual environment:
```bash
VENV_PATH=/Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env ./start_multiple_servers.sh
```

### Lỗi: "ModuleNotFoundError: No module named 'flask'"

**Nguyên nhân:** Script đang dùng system python thay vì virtual environment

**Giải pháp:** Activate virtual environment trước:
```bash
source /Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env/bin/activate
./start_multiple_servers.sh
```

### Lỗi: "FileNotFoundError: model_last.pt"

**Nguyên nhân:** Đường dẫn model trong `api_server.py` không đúng

**Giải pháp:** Sửa file `api_server.py`, dòng 47:
```python
CKPT_FILE = "/Users/itsw/Desktop/F5-TTS-Vietnamese_1/path/to/model_last.pt"
```

### Servers không response

**Kiểm tra:**
```bash
# Xem logs
tail -f logs/server_*.log

# Kiểm tra process
ps aux | grep api_server.py

# Restart
./stop_servers.sh
./start_multiple_servers.sh
```

---

## 🎉 Tóm tắt

1. **Copy files** từ Mac Mini → Server
2. **SSH** vào server
3. **Chạy** `VENV_PATH=/path/to/venv ./start_multiple_servers.sh`
4. **Đợi** 30 giây
5. **Quay lại Mac Mini**, chạy `python tts_client_loadbalanced.py`
6. **Tận hưởng** tốc độ 3x! 🚀

