# 🚀 Multi-Server Setup - Tăng tốc TTS xử lý

## 📋 Tổng quan

Chạy nhiều TTS server instances trên cùng 1 máy để tăng tốc độ xử lý.

### ⚡ Hiệu năng:

| Setup | Thời gian (10 requests) | Tốc độ |
|-------|------------------------|--------|
| **1 Server** | ~230s (3.8 phút) | 1x |
| **3 Servers** | ~77s (1.3 phút) | **3x** ⚡ |
| **4 Servers** | ~58s (1 phút) | **4x** 🚀 |

### 💾 Yêu cầu RAM:

- **1 Server**: ~3-4GB RAM
- **3 Servers**: ~9-12GB RAM
- **4 Servers**: ~12-16GB RAM

**Mac Mini M1 16GB** → Khuyến nghị chạy **3 servers** (an toàn)

---

## 🎯 Cách sử dụng

### Bước 1: Cấp quyền thực thi cho scripts

```bash
chmod +x start_multiple_servers.sh
chmod +x stop_servers.sh
```

### Bước 2: Khởi động nhiều servers

```bash
./start_multiple_servers.sh
```

**Output:**
```
🚀 Starting Multiple F5-TTS Servers...
======================================
🔄 Starting 3 servers...
  ✅ Starting server on port 5000
  ✅ Starting server on port 5001
  ✅ Starting server on port 5002

✅ All servers started!
Servers running on ports:
  - http://localhost:5000
  - http://localhost:5001
  - http://localhost:5002

💡 Wait ~30 seconds for all models to load...
```

### Bước 3: Đợi models load xong (~30 giây)

Kiểm tra logs:
```bash
tail -f logs/server_*.log
```

Hoặc check health:
```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

### Bước 4: Chạy benchmark để test

```bash
python benchmark_multiserver.py
```

### Bước 5: Sử dụng client với load balancing

```bash
python tts_client_loadbalanced.py
```

**Client sẽ tự động:**
- ✅ Phân phối request đến 3 servers (round-robin)
- ✅ Xử lý song song 3 request cùng lúc
- ✅ Tăng tốc ~3x so với 1 server

### Bước 6: Dừng tất cả servers

```bash
./stop_servers.sh
```

---

## 📁 Files được tạo

### Scripts:
- `start_multiple_servers.sh` - Khởi động nhiều servers
- `stop_servers.sh` - Dừng tất cả servers
- `tts_client_loadbalanced.py` - Client với load balancing
- `benchmark_multiserver.py` - Benchmark để test hiệu năng

### Logs:
- `logs/server_5000.log` - Log của server port 5000
- `logs/server_5001.log` - Log của server port 5001
- `logs/server_5002.log` - Log của server port 5002
- `logs/server_5000.pid` - PID của server port 5000
- ...

---

## ⚙️ Tùy chỉnh

### Thay đổi số lượng servers:

Sửa file `start_multiple_servers.sh`:
```bash
# Thay đổi dòng này:
NUM_SERVERS=3  # Đổi thành 2, 4, 5...
```

**Lưu ý:** Mỗi server tốn ~3-4GB RAM!

### Thay đổi danh sách servers trong client:

Sửa file `tts_client_loadbalanced.py`:
```python
SERVERS = [
    "http://10.0.67.77:5000",
    "http://10.0.67.77:5001",
    "http://10.0.67.77:5002",
    # Thêm server thứ 4 nếu cần:
    # "http://10.0.67.77:5003",
]
```

---

## 🔍 Troubleshooting

### Lỗi: "Address already in use"
```bash
# Dừng tất cả servers cũ
./stop_servers.sh

# Hoặc kill thủ công
pkill -f "python.*api_server.py"
```

### Lỗi: "Out of memory"
```bash
# Giảm số lượng servers
# Sửa NUM_SERVERS=2 trong start_multiple_servers.sh
```

### Check RAM usage:
```bash
# macOS
top -l 1 | grep PhysMem

# Hoặc dùng Activity Monitor
```

### Server không response:
```bash
# Check logs
tail -f logs/server_5000.log

# Restart servers
./stop_servers.sh
./start_multiple_servers.sh
```

---

## 📊 So sánh hiệu năng

### Trước (1 server):
```
Request 1 → [23s] → Done
Request 2 → [23s] → Done
Request 3 → [23s] → Done
...
Request 10 → [23s] → Done
Total: 230s
```

### Sau (3 servers):
```
Request 1 → Server 1 → [23s] → Done
Request 2 → Server 2 → [23s] → Done  } Cùng lúc
Request 3 → Server 3 → [23s] → Done

Request 4 → Server 1 → [23s] → Done
Request 5 → Server 2 → [23s] → Done  } Cùng lúc
Request 6 → Server 3 → [23s] → Done

...

Total: ~77s (3x nhanh hơn!)
```

---

## 🎉 Kết luận

✅ **Đơn giản**: Chỉ cần chạy 1 script
✅ **Hiệu quả**: Tăng tốc 3-4x
✅ **Linh hoạt**: Dễ dàng scale lên/xuống
✅ **An toàn**: Mỗi server độc lập, không conflict

**Lưu ý:** Đây là giải pháp tạm thời cho 1 máy. Nếu cần scale lớn hơn, nên dùng Docker + Kubernetes hoặc deploy lên nhiều máy khác nhau.

