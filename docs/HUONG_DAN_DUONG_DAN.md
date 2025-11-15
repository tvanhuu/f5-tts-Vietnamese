# 📂 HƯỚNG DẪN ĐƯỜNG DẪN FILE

## 🎯 Vấn đề đã giải quyết

### **Trước đây:**

```python
CKPT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
VOCAB_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
```

❌ **Vấn đề:**
- Đường dẫn cố định (hardcoded)
- Chỉ chạy được trên máy Mac Mini của bạn
- Không chạy được trên server (10.0.67.77) vì đường dẫn khác
- Khó chia sẻ code cho người khác

---

### **Bây giờ:**

```python
# Lấy đường dẫn thư mục hiện tại (root của project)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn relative từ root
CKPT_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "model_last.pt")
VOCAB_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "config.json")
```

✅ **Lợi ích:**
- Đường dẫn tự động (relative path)
- Chạy được trên mọi máy
- Chỉ cần đúng cấu trúc thư mục

---

## 📁 CẤU TRÚC THƯ MỤC YÊU CẦU

### **Trên Mac Mini:**

```
/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/
├── api_server.py                    ← Script chính
├── load_balancer.py
├── F5-TTS-Vietnamese/               ← Thư mục model
│   ├── model_last.pt                ← Model checkpoint
│   └── config.json                  ← Vocab file
├── ref3.mp3
└── logs/
```

### **Trên Server (10.0.67.77):**

```
/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
├── api_server.py                    ← Script chính
├── load_balancer.py
├── F5-TTS-Vietnamese/               ← Thư mục model
│   ├── model_last.pt                ← Model checkpoint
│   └── config.json                  ← Vocab file
├── ref3.mp3
└── logs/
```

✅ **Cấu trúc giống nhau → Code chạy được trên cả 2 máy!**

---

## 🔍 CÁCH HOẠT ĐỘNG

### **Khi chạy `api_server.py`:**

```python
# 1. Lấy đường dẫn của file api_server.py
__file__ = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/api_server.py"

# 2. Lấy thư mục chứa file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# → SCRIPT_DIR = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese"

# 3. Ghép đường dẫn
CKPT_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "model_last.pt")
# → CKPT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
```

### **Trên server (10.0.67.77):**

```python
# 1. Lấy đường dẫn của file api_server.py
__file__ = "/Users/itsw/Desktop/F5-TTS-Vietnamese_1/api_server.py"

# 2. Lấy thư mục chứa file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# → SCRIPT_DIR = "/Users/itsw/Desktop/F5-TTS-Vietnamese_1"

# 3. Ghép đường dẫn
CKPT_FILE = os.path.join(SCRIPT_DIR, "F5-TTS-Vietnamese", "model_last.pt")
# → CKPT_FILE = "/Users/itsw/Desktop/F5-TTS-Vietnamese_1/F5-TTS-Vietnamese/model_last.pt"
```

✅ **Tự động thích ứng với đường dẫn khác nhau!**

---

## 🚀 KIỂM TRA

### **Khi server start, sẽ log ra:**

```
🟢 Đang khởi tạo F5-TTS model...
📂 Model checkpoint: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt
📂 Vocab file: /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json
✅ Model đã sẵn sàng! Server có thể nhận request.
```

✅ **Kiểm tra xem đường dẫn có đúng không!**

---

## 🔧 TROUBLESHOOTING

### **Lỗi: FileNotFoundError**

```
FileNotFoundError: [Errno 2] No such file or directory: '.../F5-TTS-Vietnamese/model_last.pt'
```

**Nguyên nhân:** Cấu trúc thư mục không đúng.

**Giải pháp:**

```bash
# Kiểm tra cấu trúc
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
ls -la F5-TTS-Vietnamese/

# Phải thấy:
# model_last.pt
# config.json
```

Nếu không có, copy files:

```bash
# Từ Mac Mini
scp -r F5-TTS-Vietnamese/ itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/
```

---

### **Lỗi: Đường dẫn sai**

```
📂 Model checkpoint: /wrong/path/model_last.pt
```

**Nguyên nhân:** Chạy script từ thư mục khác.

**Giải pháp:**

```bash
# Phải cd vào thư mục chứa api_server.py
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Rồi mới chạy
python api_server.py --port 5000
```

---

## 📝 TÓM TẮT

### **Đã sửa:**

- ✅ Đường dẫn từ **absolute** → **relative**
- ✅ Tự động thích ứng với mọi máy
- ✅ Thêm log để kiểm tra đường dẫn

### **Yêu cầu:**

- ✅ Cấu trúc thư mục phải đúng
- ✅ Thư mục `F5-TTS-Vietnamese/` phải có `model_last.pt` và `config.json`
- ✅ Chạy script từ đúng thư mục

### **Deploy lên server:**

```bash
# Copy file đã sửa
scp api_server.py itsw@10.0.67.77:/Users/itsw/Desktop/F5-TTS-Vietnamese_1/

# SSH và test
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1
python api_server.py --port 5000

# Xem log để kiểm tra đường dẫn
# Phải thấy:
# 📂 Model checkpoint: /Users/itsw/Desktop/F5-TTS-Vietnamese_1/F5-TTS-Vietnamese/model_last.pt
# 📂 Vocab file: /Users/itsw/Desktop/F5-TTS-Vietnamese_1/F5-TTS-Vietnamese/config.json
```

---

**Chúc bạn deploy thành công!** 🚀

