# 📁 CUSTOM OUTPUT DIRECTORY - Tùy chỉnh thư mục lưu file

## 🎯 Tính năng

Bây giờ bạn có thể **tùy chỉnh thư mục lưu file audio** khi gọi API TTS.

---

## ✅ CÁCH SỬ DỤNG

### **1. Endpoint `/tts` - Với custom output_dir**

**Request:**
```json
{
    "text": "Xin chào",
    "speed": 0.75,
    "output_dir": "my_custom_folder"
}
```

**Hành vi:**
- Tạo thư mục `my_custom_folder/` nếu chưa tồn tại
- Lưu file audio vào `my_custom_folder/xxx.wav`
- Gửi file cho client
- **Xóa file ngay sau khi gửi xong** ✅

---

### **2. Endpoint `/tts/json` - Với custom output_dir**

**Request:**
```json
{
    "text": "Xin chào",
    "speed": 0.75,
    "output_dir": "my_custom_folder"
}
```

**Response:**
```json
{
    "success": true,
    "file_path": "my_custom_folder/xxx.wav",
    "sample_rate": 24000,
    "duration": 2.5,
    "text": "Xin chào"
}
```

**Hành vi:**
- Tạo thư mục `my_custom_folder/` nếu chưa tồn tại
- Lưu file audio vào `my_custom_folder/xxx.wav`
- Trả về JSON với đường dẫn file
- **Không xóa file** (deprecated endpoint)

---

## 🚀 VÍ DỤ

### **Python - Dùng custom folder**

```python
import requests

# Gửi request với custom output_dir
response = requests.post(
    "http://10.0.67.77:5000/tts",
    json={
        "text": "Xin chào",
        "speed": 0.75,
        "output_dir": "audio_output"  # ← Custom folder
    }
)

# Lưu file
with open("output.wav", "wb") as f:
    f.write(response.content)

# File trên server:
# - Đã được lưu vào: audio_output/xxx.wav
# - Đã bị xóa tự động ✅
```

---

### **Python - Không dùng custom folder (mặc định)**

```python
import requests

# Gửi request không có output_dir
response = requests.post(
    "http://10.0.67.77:5000/tts",
    json={
        "text": "Xin chào",
        "speed": 0.75,
        # Không có output_dir → Dùng thư mục mặc định "outputs/"
    }
)

# File trên server:
# - Đã được lưu vào: outputs/xxx.wav (mặc định)
# - Đã bị xóa tự động ✅
```

---

### **cURL - Dùng custom folder**

```bash
curl -X POST http://10.0.67.77:5000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Xin chào",
    "speed": 0.75,
    "output_dir": "audio_output"
  }' \
  --output output.wav

# File trên server:
# - Đã được lưu vào: audio_output/xxx.wav
# - Đã bị xóa tự động ✅
```

---

## 📊 SO SÁNH

| Tham số | Giá trị | Thư mục lưu file |
|---------|---------|------------------|
| `output_dir` không có | N/A | `outputs/` (mặc định) |
| `output_dir: "my_folder"` | `"my_folder"` | `my_folder/` |
| `output_dir: "data/audio"` | `"data/audio"` | `data/audio/` |
| `output_dir: "/tmp/tts"` | `"/tmp/tts"` | `/tmp/tts/` (absolute path) |

---

## 🔍 USE CASES

### **Use Case 1: Phân loại theo ngày**

```python
from datetime import datetime

# Tạo folder theo ngày
today = datetime.now().strftime("%Y-%m-%d")
output_dir = f"audio_{today}"

response = requests.post(
    "http://10.0.67.77:5000/tts",
    json={
        "text": "Xin chào",
        "output_dir": output_dir  # audio_2025-11-14
    }
)

# File được lưu vào: audio_2025-11-14/xxx.wav
```

---

### **Use Case 2: Phân loại theo user**

```python
user_id = "user_123"
output_dir = f"users/{user_id}/audio"

response = requests.post(
    "http://10.0.67.77:5000/tts",
    json={
        "text": "Xin chào",
        "output_dir": output_dir  # users/user_123/audio
    }
)

# File được lưu vào: users/user_123/audio/xxx.wav
```

---

### **Use Case 3: Temporary folder**

```python
import tempfile

# Dùng temp folder của hệ thống
temp_dir = tempfile.gettempdir()
output_dir = f"{temp_dir}/tts_audio"

response = requests.post(
    "http://10.0.67.77:5000/tts",
    json={
        "text": "Xin chào",
        "output_dir": output_dir  # /tmp/tts_audio
    }
)

# File được lưu vào: /tmp/tts_audio/xxx.wav
# Và bị xóa tự động sau khi gửi ✅
```

---

## ⚠️  LƯU Ý

### **1. Thư mục được tạo tự động**

Nếu thư mục chưa tồn tại, server sẽ tự động tạo:

```python
output_dir.mkdir(parents=True, exist_ok=True)
```

---

### **2. Đường dẫn tương đối vs tuyệt đối**

**Đường dẫn tương đối:**
```json
{"output_dir": "my_folder"}
```
→ Lưu vào: `<server_root>/my_folder/`

**Đường dẫn tuyệt đối:**
```json
{"output_dir": "/tmp/tts"}
```
→ Lưu vào: `/tmp/tts/`

---

### **3. Endpoint `/tts` vẫn xóa file**

Dù bạn dùng custom folder hay không, endpoint `/tts` **vẫn xóa file sau khi gửi**.

---

### **4. Endpoint `/tts/json` không xóa file**

Endpoint `/tts/json` **không xóa file**, dù bạn dùng custom folder hay không.

---

## 🎉 TÓM TẮT

### **Đã thêm:**
- ✅ Tham số `output_dir` cho endpoint `/tts`
- ✅ Tham số `output_dir` cho endpoint `/tts/json`
- ✅ Tự động tạo thư mục nếu chưa tồn tại
- ✅ Hỗ trợ đường dẫn tương đối và tuyệt đối

### **Lợi ích:**
- ✅ Linh hoạt tùy chỉnh thư mục lưu file
- ✅ Phân loại file theo ngày, user, project, etc.
- ✅ Dễ dàng quản lý file
- ✅ Backward compatible (không có `output_dir` → Dùng mặc định)

---

**Bây giờ bạn có thể tùy chỉnh thư mục lưu file!** 📁✨

