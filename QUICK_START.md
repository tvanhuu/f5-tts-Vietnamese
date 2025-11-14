# 🚀 QUICK START - Multi-Server TTS Setup

## 📝 Tóm tắt

Hệ thống TTS với queue system và multi-server để tăng tốc độ xử lý **3-4x**.

---

## ⚡ CÁCH DÙNG NHANH (3 bước)

### 1️⃣ Khởi động 3 servers:
```bash
./start_multiple_servers.sh
```

### 2️⃣ Đợi 30 giây để models load

### 3️⃣ Chạy client:
```bash
python tts_client_loadbalanced.py
```

**Xong!** 🎉

---

## 📊 KẾT QUẢ MONG ĐỢI

### Trước (1 server):
- ⏱️ 10 requests: ~230s (3.8 phút)
- 🐌 Chậm, phải đợi từng request

### Sau (3 servers):
- ⏱️ 10 requests: ~77s (1.3 phút)
- 🚀 Nhanh gấp 3x
- ✅ Gửi tất cả request cùng lúc

---

## 🛑 DỪNG SERVERS

```bash
./stop_servers.sh
```

---

## 🧪 TEST HIỆU NĂNG

```bash
python benchmark_multiserver.py
```

Kết quả sẽ hiển thị:
- ✅ Số request thành công
- ⏱️ Thời gian xử lý
- 🚀 Tốc độ tăng bao nhiêu lần

---

## 📁 CÁC FILE QUAN TRỌNG

### Scripts chính:
- `start_multiple_servers.sh` - Khởi động servers
- `stop_servers.sh` - Dừng servers
- `tts_client_loadbalanced.py` - Client với load balancing
- `benchmark_multiserver.py` - Test hiệu năng

### Server:
- `api_server.py` - Server với queue system (đã sửa)

### Logs:
- `logs/server_5000.log` - Log server 1
- `logs/server_5001.log` - Log server 2
- `logs/server_5002.log` - Log server 3

---

## 🔧 TÙY CHỈNH

### Thay đổi số servers:

Sửa `start_multiple_servers.sh`:
```bash
NUM_SERVERS=3  # Đổi thành 2, 4, 5...
```

**Lưu ý RAM:**
- 2 servers: ~6-8GB
- 3 servers: ~9-12GB ✅ (Khuyến nghị cho Mac Mini M1 16GB)
- 4 servers: ~12-16GB

---

## ❓ TROUBLESHOOTING

### Lỗi "Address already in use":
```bash
./stop_servers.sh
./start_multiple_servers.sh
```

### Server không response:
```bash
# Check logs
tail -f logs/server_*.log

# Restart
./stop_servers.sh
./start_multiple_servers.sh
```

### Out of memory:
```bash
# Giảm số servers xuống 2
# Sửa NUM_SERVERS=2 trong start_multiple_servers.sh
```

---

## 📚 TÀI LIỆU CHI TIẾT

- `MULTI_SERVER_README.md` - Hướng dẫn chi tiết multi-server
- `API_SERVER_QUEUE_README.md` - Hướng dẫn queue system

---

## 🎯 WORKFLOW HOÀN CHỈNH

```
1. Start servers
   └─> ./start_multiple_servers.sh

2. Wait 30s for models to load
   └─> tail -f logs/server_*.log

3. Run client
   └─> python tts_client_loadbalanced.py

4. Check results
   └─> ls output_audio/

5. Stop servers
   └─> ./stop_servers.sh
```

---

## ✅ CHECKLIST

- [x] Queue system trong api_server.py
- [x] Multi-server startup script
- [x] Load-balanced client
- [x] Benchmark script
- [x] Checkpoint/resume system
- [x] Logs và monitoring

---

## 🎉 TỔNG KẾT

### Đã giải quyết:
✅ **Vấn đề conflict** khi gọi nhiều API cùng lúc
✅ **Tăng tốc 3x** với multi-server
✅ **Resume từ checkpoint** khi bị gián đoạn
✅ **Load balancing** tự động

### Hiệu năng:
- 🚀 **3x nhanh hơn** với 3 servers
- ⚡ **Xử lý song song** nhiều request
- 💾 **Tối ưu RAM** (3 servers = 12GB)

### Dễ sử dụng:
- 🎯 **1 lệnh** để start servers
- 🎯 **1 lệnh** để chạy client
- 🎯 **1 lệnh** để stop servers

**Enjoy!** 🎊

