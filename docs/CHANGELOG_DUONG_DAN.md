# 📝 CHANGELOG - SỬA ĐƯỜNG DẪN TUYỆT ĐỐI

## 🎯 Tóm tắt

Đã sửa **tất cả đường dẫn tuyệt đối** thành **đường dẫn tương đối** trong project.

---

## ✅ CÁC FILE ĐÃ SỬA

### **1. api_server.py**

**Trước:**
```python
CKPT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
VOCAB_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại (root của project)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn relative từ root
CKPT_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "model_last.pt")
VOCAB_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "config.json")

print(f"📂 Model checkpoint: {CKPT_FILE}")
print(f"📂 Vocab file: {VOCAB_FILE}")
```

---

### **2. tts_client.py**

**Trước:**
```python
SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR = Path(__file__).resolve().parent
SRT_FILE = SCRIPT_DIR / "srt.srt"
```

---

### **3. tts_client_loadbalanced.py**

**Trước:**
```python
SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR = Path(__file__).resolve().parent
SRT_FILE = SCRIPT_DIR / "srt.srt"
```

---

### **4. tts_client_simple.py**

**Trước:**
```python
SRT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR = Path(__file__).resolve().parent
SRT_FILE = SCRIPT_DIR / "srt.srt"
```

---

### **5. infer.sh**

**Trước:**
```bash
f5-tts_infer-cli \
--vocab_file /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json \
--ckpt_file /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt \
```

**Sau:**
```bash
#!/bin/bash

# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

f5-tts_infer-cli \
--vocab_file "$SCRIPT_DIR/F5-TTS-Vietnamese/config.json" \
--ckpt_file "$SCRIPT_DIR/F5-TTS-Vietnamese/model_last.pt" \
```

---

### **6. test_multiple_audio.py**

**Trước:**
```python
ckpt_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
vocab_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR = Path(__file__).resolve().parent
ckpt_file = SCRIPT_DIR / "F5-TTS-Vietnamese" / "model_last.pt"
vocab_file = SCRIPT_DIR / "F5-TTS-Vietnamese" / "config.json"

print(f"📂 Model checkpoint: {ckpt_file}")
print(f"📂 Vocab file: {vocab_file}")
```

---

### **7. tts_service.py**

**Trước:**
```python
ckpt_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
vocab_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
```

**Sau:**
```python
# Lấy đường dẫn thư mục hiện tại
from pathlib import Path
script_dir = Path(__file__).resolve().parent
ckpt_file = script_dir / "F5-TTS-Vietnamese" / "model_last.pt"
vocab_file = script_dir / "F5-TTS-Vietnamese" / "config.json"

print(f"📂 Model checkpoint: {ckpt_file}")
print(f"📂 Vocab file: {vocab_file}")
```

---

## 🎯 LỢI ÍCH

### **Trước khi sửa:**
- ❌ Chỉ chạy được trên máy Mac Mini
- ❌ Không chạy được trên server (10.0.67.77)
- ❌ Khó chia sẻ code
- ❌ Phải sửa đường dẫn mỗi khi deploy

### **Sau khi sửa:**
- ✅ Chạy được trên mọi máy
- ✅ Tự động thích ứng với đường dẫn
- ✅ Dễ chia sẻ code
- ✅ Không cần sửa gì khi deploy

---

## 📁 CẤU TRÚC THƯ MỤC YÊU CẦU

Để code chạy được, cần đảm bảo cấu trúc thư mục như sau:

```
<project_root>/
├── api_server.py
├── load_balancer.py
├── tts_client.py
├── tts_client_loadbalanced.py
├── tts_client_simple.py
├── test_multiple_audio.py
├── tts_service.py
├── infer.sh
├── srt.srt                          ← File SRT
├── ref3.mp3                         ← File audio tham chiếu
├── F5-TTS-Vietnamese/               ← Thư mục model
│   ├── model_last.pt                ← Model checkpoint
│   └── config.json                  ← Vocab file
└── output_audio/                    ← Thư mục output
```

✅ **Cấu trúc này phải giống nhau trên cả Mac Mini và Server!**

---

## 🚀 KIỂM TRA

### **Trên Mac Mini:**

```bash
cd /Users/tvan.huu/Desktop/F5-TTS-Vietnamese

# Test api_server.py
python api_server.py --port 5000

# Phải thấy log:
# 📂 Model checkpoint: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt
# 📂 Vocab file: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json
```

### **Trên Server (10.0.67.77):**

```bash
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Test api_server.py
python api_server.py --port 5000

# Phải thấy log:
# 📂 Model checkpoint: /Users/itsw/Desktop/F5-TTS-Vietnamese_1/F5-TTS-Vietnamese/model_last.pt
# 📂 Vocab file: /Users/itsw/Desktop/F5-TTS-Vietnamese_1/F5-TTS-Vietnamese/config.json
```

✅ **Đường dẫn tự động thích ứng!**

---

## 📝 TÓM TẮT

- ✅ Đã sửa **7 files**
- ✅ Tất cả đường dẫn tuyệt đối → đường dẫn tương đối
- ✅ Thêm log để kiểm tra đường dẫn
- ✅ Code chạy được trên mọi máy

---

**Chúc bạn deploy thành công!** 🚀

