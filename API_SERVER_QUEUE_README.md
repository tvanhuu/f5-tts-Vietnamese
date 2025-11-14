# 🚀 F5-TTS API Server với Queue System

## ✨ Tính năng mới

### 🎯 Queue System
- ✅ **Hỗ trợ nhiều request đồng thời** - Client có thể gửi nhiều request cùng lúc
- ✅ **Xử lý tuần tự an toàn** - Server xử lý từng request một để tránh conflict
- ✅ **Sync & Async mode** - Chọn chờ kết quả ngay hoặc lấy sau
- ✅ **Thread-safe** - Sử dụng lock để bảo vệ model
- ✅ **Tracking & Stats** - Theo dõi số lượng request, queue size

## 📋 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "model": "F5-TTS Vietnamese",
  "message": "Model đã được load và sẵn sàng",
  "stats": {
    "total_requests": 10,
    "completed_requests": 8,
    "failed_requests": 0,
    "queue_size": 2,
    "processing": true
  }
}
```

### 2. Text-to-Speech (Sync Mode - Mặc định)
```bash
curl --location 'http://10.0.67.77:5000/tts' \
--header 'Content-Type: application/json' \
--data '{
    "text": "Xin chào, đây là test",
    "speed": 0.75
}'
```

**Response:** File audio .wav

### 3. Text-to-Speech (Async Mode)
```bash
curl --location 'http://10.0.67.77:5000/tts' \
--header 'Content-Type: application/json' \
--data '{
    "text": "Xin chào, đây là test",
    "speed": 0.75,
    "async": true
}'
```

**Response:**
```json
{
  "request_id": "abc-123-def-456",
  "status": "queued",
  "queue_position": 3
}
```

### 4. Check Status (cho Async Mode)
```bash
GET /tts/status/<request_id>
```

**Response:**
```json
{
  "request_id": "abc-123-def-456",
  "status": "completed",
  "result": {
    "output_path": "outputs/abc-123-def-456.wav",
    "sample_rate": 24000,
    "duration": 2.5,
    "processing_time": 18.5
  }
}
```

## 🔧 Cách sử dụng

### Khởi động server
```bash
python api_server.py
```

### Sử dụng với Python client

#### Sync Mode (Chờ kết quả ngay)
```python
import requests

response = requests.post('http://10.0.67.77:5000/tts', json={
    'text': 'Xin chào',
    'speed': 0.75
})

with open('output.wav', 'wb') as f:
    f.write(response.content)
```

#### Async Mode (Gửi nhiều request cùng lúc)
```python
import requests
import time

# Gửi nhiều request
request_ids = []
for i, text in enumerate(texts):
    response = requests.post('http://10.0.67.77:5000/tts', json={
        'text': text,
        'speed': 0.75,
        'async': True
    })
    data = response.json()
    request_ids.append(data['request_id'])
    print(f"Queued {i+1}: {data['request_id']}")

# Đợi và lấy kết quả
for request_id in request_ids:
    while True:
        response = requests.get(f'http://10.0.67.77:5000/tts/status/{request_id}')
        data = response.json()
        
        if data['status'] == 'completed':
            print(f"✓ Completed: {request_id}")
            break
        elif data['status'] == 'failed':
            print(f"✗ Failed: {request_id}")
            break
        
        time.sleep(1)  # Đợi 1 giây rồi check lại
```

## 🎯 Lợi ích của Queue System

### Trước (Không có queue):
- ❌ Gửi 2 request cùng lúc → 1 thành công, 1 lỗi
- ❌ Client phải đợi từng request xong mới gửi tiếp
- ❌ Tổng thời gian: 234s cho 10 request

### Sau (Có queue):
- ✅ Gửi 10 request cùng lúc → Tất cả thành công
- ✅ Server tự động xếp hàng và xử lý tuần tự
- ✅ Client không cần đợi, có thể làm việc khác
- ✅ Tổng thời gian: Vẫn 234s nhưng UX tốt hơn nhiều!

## 📊 So sánh

| Tính năng | Trước | Sau |
|-----------|-------|-----|
| Nhiều request cùng lúc | ❌ Lỗi | ✅ OK |
| Client phải đợi | ✅ Phải | ⚡ Tùy chọn |
| Thread-safe | ❌ Không | ✅ Có |
| Tracking | ❌ Không | ✅ Có stats |
| Async support | ❌ Không | ✅ Có |

## 🚀 Chạy benchmark

```bash
# Test với queue system mới
python benchmark_parallel.py
```

Kết quả mong đợi: Tất cả request đều thành công!

