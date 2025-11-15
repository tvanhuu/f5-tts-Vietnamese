# 🔀 F5-TTS với Load Balancer - Hướng dẫn nhanh

## 🎯 Bạn muốn gì?

**Trước đây:**
- ❌ Client phải quản lý 3 địa chỉ servers
- ❌ Client phải tự chia tải (round-robin)
- ❌ Code phức tạp

**Bây giờ:**
- ✅ Client chỉ cần gọi **1 địa chỉ duy nhất**: `http://10.0.67.77:8080`
- ✅ Load Balancer **tự động chia tải** vào 3 servers
- ✅ Code client **đơn giản**

---

## 🚀 HƯỚNG DẪN NHANH (3 BƯỚC)

### **Bước 1: Deploy lên Server** (từ Mac Mini)

```bash
./deploy_to_server.sh
```

### **Bước 2: Khởi động trên Server**

```bash
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
chmod +x start_with_loadbalancer.sh stop_all.sh

# Khởi động
VENV_PATH=/Users/itsw/Desktop/F5-TTS-Vietnamese_1/f5tts-env ./start_with_loadbalancer.sh

# Đợi 30 giây
sleep 30

# Test
curl http://localhost:8080/health
```

### **Bước 3: Chạy Client** (từ Mac Mini)

```bash
python tts_client_simple.py
```

**Xong!** 🎉

---

## 📊 Kiến trúc

```
Mac Mini (Client)
    │
    │ Gọi http://10.0.67.77:8080/tts
    ▼
Server (10.0.67.77)
    │
    ├─ Load Balancer (Port 8080)
    │   │
    │   ├─ TTS Server 1 (Port 5000)
    │   ├─ TTS Server 2 (Port 5001)
    │   └─ TTS Server 3 (Port 5002)
```

---

## 📁 Files mới

| File | Mô tả |
|------|-------|
| `load_balancer.py` | Load Balancer (Round-Robin) |
| `start_with_loadbalancer.sh` | Start 3 servers + Load Balancer |
| `stop_all.sh` | Stop tất cả services |
| `tts_client_simple.py` | Client đơn giản (chỉ gọi Load Balancer) |
| `HUONG_DAN_LOAD_BALANCER.md` | Hướng dẫn chi tiết |

---

## 🎯 So sánh

### **Cách cũ (tts_client_loadbalanced.py):**

```python
# Client phải quản lý 3 servers
SERVERS = [
    "http://10.0.67.77:5000",
    "http://10.0.67.77:5001",
    "http://10.0.67.77:5002",
]

# Client phải tự chia tải
server_cycle = itertools.cycle(SERVERS)
server = next(server_cycle)
```

### **Cách mới (tts_client_simple.py):**

```python
# Client chỉ cần 1 địa chỉ
LOAD_BALANCER_URL = "http://10.0.67.77:8080"

# Gọi đơn giản
call_tts_api(LOAD_BALANCER_URL, text, output_path)
```

**→ Đơn giản hơn nhiều!** ✅

---

## 🛑 Dừng services

```bash
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
./stop_all.sh
```

---

## 📊 Xem thống kê

```bash
curl http://10.0.67.77:8080/health | python3 -m json.tool
```

Output:
```json
{
  "status": "ok",
  "backend_servers": 3,
  "stats": {
    "total_requests": 10,
    "successful_requests": 10,
    "server_stats": {
      "http://localhost:5000": {"requests": 4},
      "http://localhost:5001": {"requests": 3},
      "http://localhost:5002": {"requests": 3}
    }
  }
}
```

---

## 🎉 Lợi ích

1. ✅ **Client đơn giản**: Chỉ cần 1 địa chỉ
2. ✅ **Tự động chia tải**: Load Balancer lo hết
3. ✅ **Dễ scale**: Thêm server chỉ cần sửa Load Balancer
4. ✅ **Monitoring**: Stats qua `/health`
5. ✅ **Fault tolerance**: 1 server chết vẫn còn 2 server

---

## 📚 Tài liệu chi tiết

Xem file `HUONG_DAN_LOAD_BALANCER.md` để biết thêm chi tiết!

---

## 🆘 Troubleshooting

### Lỗi: "Connection refused"

Kiểm tra Load Balancer có chạy không:
```bash
ssh itsw@10.0.67.77
ps aux | grep load_balancer
```

### Lỗi: Backend servers không response

Kiểm tra logs:
```bash
tail -f logs/load_balancer.log
tail -f logs/server_*.log
```

### Restart tất cả

```bash
./stop_all.sh
sleep 2
VENV_PATH=/path/to/venv ./start_with_loadbalancer.sh
```

---

**Chúc bạn thành công!** 🚀

