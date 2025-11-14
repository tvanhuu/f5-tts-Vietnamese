# 🔀 HƯỚNG DẪN SỬ DỤNG LOAD BALANCER

## 🎯 Kiến trúc

```
┌─────────────────┐
│   Mac Mini      │
│   (Client)      │
└────────┬────────┘
         │
         │ HTTP Request
         │ http://10.0.67.77:8080/tts
         ▼
┌─────────────────────────────────────┐
│  Server (10.0.67.77)                │
│                                     │
│  ┌───────────────────────┐          │
│  │   Load Balancer       │          │
│  │   Port: 8080          │          │
│  │   (Round-Robin)       │          │
│  └──────────┬────────────┘          │
│             │                       │
│    ┌────────┼────────┐              │
│    │        │        │              │
│    ▼        ▼        ▼              │
│  ┌───┐   ┌───┐   ┌───┐             │
│  │ 1 │   │ 2 │   │ 3 │             │
│  │   │   │   │   │   │             │
│  │TTS│   │TTS│   │TTS│             │
│  │   │   │   │   │   │             │
│  └───┘   └───┘   └───┘             │
│  5000    5001    5002              │
└─────────────────────────────────────┘
```

**Lợi ích:**
- ✅ Client chỉ cần gọi **1 địa chỉ duy nhất**: `http://10.0.67.77:8080`
- ✅ Load Balancer **tự động chia tải** vào 3 servers
- ✅ **Đơn giản hóa** code client (không cần quản lý nhiều servers)
- ✅ **Dễ scale**: Thêm server chỉ cần sửa config Load Balancer

---

## 📋 BƯỚC 1: Copy files lên Server

Từ **Mac Mini**, copy các files mới:

```bash
scp load_balancer.py itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
scp start_with_loadbalancer.sh itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
scp stop_all.sh itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
scp api_server.py itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
```

---

## 📋 BƯỚC 2: Khởi động trên Server

SSH vào server:

```bash
ssh itsw@10.0.67.77
```

Chạy script:

```bash
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Cấp quyền thực thi
chmod +x start_with_loadbalancer.sh stop_all.sh

# Khởi động (với virtual environment)
VENV_PATH=/Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env ./start_with_loadbalancer.sh
```

**Output mong đợi:**

```
🚀 Starting F5-TTS Multi-Server with Load Balancer...
============================================================
✅ Using specified virtual environment: /Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env/bin/python

🧹 Cleaning up old processes...

🔄 Starting 3 backend servers...
  ✅ Starting TTS server on port 5000
  ✅ Starting TTS server on port 5001
  ✅ Starting TTS server on port 5002

⏳ Waiting 10 seconds for servers to initialize...

🔀 Starting Load Balancer on port 8080...

✅ All services started!
============================================================
🔀 Load Balancer:
   http://localhost:8080
   http://0.0.0.0:8080 (accessible from other machines)

🖥️  Backend TTS Servers:
   1. http://localhost:5000
   2. http://localhost:5001
   3. http://localhost:5002

📊 Check status:
   curl http://localhost:8080/health

💡 From other machines, use:
   http://10.0.67.77:8080
============================================================
```

---

## 📋 BƯỚC 3: Kiểm tra trên Server

Đợi ~30 giây để models load, sau đó test:

```bash
# Test Load Balancer health
curl http://localhost:8080/health | python3 -m json.tool
```

**Output mong đợi:**

```json
{
  "status": "ok",
  "load_balancer": "F5-TTS Load Balancer",
  "backend_servers": 3,
  "backends": {
    "http://localhost:5000": {
      "status": "ok",
      "response": {
        "status": "ok",
        "model": "F5-TTS Vietnamese",
        "message": "Model đã được load và sẵn sàng"
      }
    },
    "http://localhost:5001": {
      "status": "ok",
      "response": {...}
    },
    "http://localhost:5002": {
      "status": "ok",
      "response": {...}
    }
  },
  "stats": {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
  }
}
```

✅ Nếu thấy tất cả backends `"status": "ok"` → Thành công!

---

## 📋 BƯỚC 4: Chạy Client từ Mac Mini

Quay lại **Mac Mini**:

```bash
cd /Users/tvan.huu/Desktop/F5-TTS-Vietnamese

# Chạy client đơn giản (chỉ gọi Load Balancer)
python tts_client_simple.py
```

**Client sẽ:**
- ✅ Gọi `http://10.0.67.77:8080/tts` cho mỗi request
- ✅ Load Balancer tự động chia tải vào 3 servers
- ✅ Xử lý tuần tự từng request (đơn giản)

**Output:**

```
🚀 TTS CLIENT - Simple Mode
============================================================
📁 SRT File: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt
📂 Output: output_audio
⚡ Speed: 0.75
🔀 Load Balancer: http://10.0.67.77:8080
============================================================

Đang đọc file SRT: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt
Tìm thấy 10 đoạn text

[ ] 1. cậu cao, nghe nói nhà cậu đã vỡ nợ...
[ ] 2. nhà tôi đúng là có chút vấn đề...
...

📊 Cần xử lý: 10/10 đoạn
============================================================

🔄 Bắt đầu xử lý...

[1/10] Processing: cậu cao, nghe nói nhà cậu đã vỡ nợ...
  ✅ Success in 23.2s → audio_0001.wav

[2/10] Processing: nhà tôi đúng là có chút vấn đề...
  ✅ Success in 22.8s → audio_0002.wav

...
```

---

## 📊 BƯỚC 5: Xem thống kê Load Balancer

Từ **Mac Mini** hoặc **Server**:

```bash
curl http://10.0.67.77:8080/health | python3 -m json.tool
```

Sẽ thấy stats:

```json
{
  "stats": {
    "total_requests": 10,
    "successful_requests": 10,
    "failed_requests": 0,
    "server_stats": {
      "http://localhost:5000": {
        "requests": 4,
        "failures": 0
      },
      "http://localhost:5001": {
        "requests": 3,
        "failures": 0
      },
      "http://localhost:5002": {
        "requests": 3,
        "failures": 0
      }
    }
  }
}
```

✅ Requests được **phân phối đều** vào 3 servers!

---

## 🛑 BƯỚC 6: Dừng tất cả services

Trên **Server**:

```bash
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./stop_all.sh
```

---

## 🚀 NÂNG CAO: Client song song

Nếu muốn client gửi **nhiều requests song song** (tận dụng tối đa 3 servers):

Sử dụng `tts_client_loadbalanced.py` nhưng sửa để chỉ gọi Load Balancer:

```python
# Sửa dòng 130-135
SERVERS = [
    "http://10.0.67.77:8080",  # Chỉ cần 1 địa chỉ Load Balancer
]

# Nhưng vẫn dùng 3 workers để gửi song song
MAX_WORKERS = 3  # Gửi 3 requests song song
```

Khi đó:
- Client gửi 3 requests song song đến Load Balancer
- Load Balancer chia vào 3 servers khác nhau
- → Tận dụng tối đa 3 servers!

---

## ✅ TÓM TẮT

| Thành phần | Địa chỉ | Mô tả |
|------------|---------|-------|
| **Load Balancer** | `http://10.0.67.77:8080` | Điểm vào duy nhất |
| **TTS Server 1** | `http://10.0.67.77:5000` | Backend (internal) |
| **TTS Server 2** | `http://10.0.67.77:5001` | Backend (internal) |
| **TTS Server 3** | `http://10.0.67.77:5002` | Backend (internal) |

**Client chỉ cần biết:** `http://10.0.67.77:8080` ✅

---

## 🎉 LỢI ÍCH

1. ✅ **Đơn giản hóa client**: Chỉ cần 1 địa chỉ
2. ✅ **Tự động chia tải**: Load Balancer lo việc phân phối
3. ✅ **Dễ scale**: Thêm server chỉ cần sửa `load_balancer.py`
4. ✅ **Monitoring**: Xem stats qua `/health` endpoint
5. ✅ **Fault tolerance**: Nếu 1 server chết, vẫn còn 2 server khác

---

## 🔧 Troubleshooting

### Load Balancer không start

Kiểm tra logs:
```bash
tail -f logs/load_balancer.log
```

### Backend servers không response

Kiểm tra từng server:
```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

### Port 8080 đã được sử dụng

Sửa port trong `start_with_loadbalancer.sh`:
```bash
LOAD_BALANCER_PORT=9090  # Đổi sang port khác
```

Và trong `tts_client_simple.py`:
```python
LOAD_BALANCER_URL = "http://10.0.67.77:9090"
```

