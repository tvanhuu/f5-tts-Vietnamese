# 🧪 HƯỚNG DẪN TEST TTS API

## 📁 Files test

| File | Mô tả | Độ khó |
|------|-------|--------|
| `test_simple.py` | Test với menu tương tác (dễ nhất) | ⭐ |
| `test_requests.py` | Test với command-line arguments | ⭐⭐ |

---

## 🎯 MỤC ĐÍCH TEST

### **Test 1: Gửi 1 request**
- ✅ Kiểm tra server có hoạt động không
- ✅ Đo thời gian xử lý 1 request
- ✅ Kiểm tra chất lượng audio

### **Test 2: Gửi 2 requests song song**
- ✅ Kiểm tra server có xử lý được đồng thời không
- ✅ So sánh với/không có Load Balancer

**Kết quả mong đợi:**

| Trường hợp | Kết quả |
|------------|---------|
| **1 server, không Load Balancer** | Request 2 sẽ **lỗi** hoặc **chờ** request 1 xong |
| **3 servers + Load Balancer** | Cả 2 requests **thành công**, thời gian ~bằng 1 request |

### **Test 3: Gửi 3 requests song song**
- ✅ Test tối đa throughput
- ✅ Kiểm tra Load Balancer chia tải đều

---

## 🚀 CÁCH 1: TEST ĐỠN GIẢN (test_simple.py)

### **Chạy:**

```bash
python test_simple.py
```

### **Menu:**

```
🧪 TTS API TEST - SIMPLE MODE
============================================================
🌐 Server: http://10.0.67.77:5000
📂 Output: test_output
⚡ Speed: 0.75
============================================================

📋 MENU:
  1. Test 1 request
  2. Test 2 requests (tuần tự)
  3. Test 2 requests (song song)
  4. Test 3 requests (song song)
  5. Thay đổi server URL
  0. Thoát

👉 Chọn (0-5):
```

### **Ví dụ sử dụng:**

#### **Bước 1: Test 1 request**

Chọn `1`:

```
🧪 TEST 1 REQUEST
============================================================

[1] 🚀 Đang gửi request...
[1] 📝 Text: Xin chào, đây là câu test thứ nhất...
[1] ✅ Thành công! (23.5s, 2.1MB)

📊 KẾT QUẢ
============================================================
✅ Thành công: 1/1
⏱️  Tổng thời gian: 23.5s
============================================================
```

✅ Server hoạt động tốt!

---

#### **Bước 2: Test 2 requests song song (không Load Balancer)**

Chọn `3`:

```
🧪 TEST 2 REQUESTS - SONG SONG
============================================================

[1] 🚀 Đang gửi request...
[1] 📝 Text: Xin chào, đây là câu test thứ nhất...
[2] 🚀 Đang gửi request...
[2] 📝 Text: Câu test thứ hai dài hơn một chút...

[1] ✅ Thành công! (23.2s, 2.1MB)
[2] ❌ Lỗi: HTTP 500

📊 KẾT QUẢ
============================================================
✅ Thành công: 1/2
⏱️  Tổng thời gian: 23.5s
💡 Nếu có Load Balancer, thời gian sẽ ~bằng 1 request
💡 Nếu không có Load Balancer, request 2 sẽ bị lỗi hoặc chờ
============================================================
```

❌ Request 2 bị lỗi → Cần Load Balancer!

---

#### **Bước 3: Đổi sang Load Balancer**

Chọn `5`:

```
👉 Chọn (0-5): 5
Nhập URL mới (hiện tại: http://10.0.67.77:5000): http://10.0.67.77:8080
✅ Đã đổi sang: http://10.0.67.77:8080
```

---

#### **Bước 4: Test lại 2 requests song song (có Load Balancer)**

Chọn `3`:

```
🧪 TEST 2 REQUESTS - SONG SONG
============================================================

[1] 🚀 Đang gửi request...
[1] 📝 Text: Xin chào, đây là câu test thứ nhất...
[2] 🚀 Đang gửi request...
[2] 📝 Text: Câu test thứ hai dài hơn một chút...

[1] ✅ Thành công! (23.2s, 2.1MB)
[2] ✅ Thành công! (23.5s, 2.2MB)

📊 KẾT QUẢ
============================================================
✅ Thành công: 2/2
⏱️  Tổng thời gian: 23.8s
💡 Với Load Balancer, thời gian ~bằng 1 request
============================================================
```

✅ Cả 2 requests thành công, thời gian ~23.8s (thay vì ~47s)!

---

## 🚀 CÁCH 2: TEST VỚI COMMAND-LINE (test_requests.py)

### **Cú pháp:**

```bash
python test_requests.py --num <số_requests> --mode <sequential|parallel> --server <url>
```

### **Ví dụ:**

#### **Test 1 request:**

```bash
python test_requests.py --num 1 --server http://10.0.67.77:5000
```

#### **Test 2 requests song song:**

```bash
python test_requests.py --num 2 --mode parallel --server http://10.0.67.77:5000
```

#### **Test 3 requests song song với Load Balancer:**

```bash
python test_requests.py --num 3 --mode parallel --server http://10.0.67.77:8080
```

#### **Test 5 requests tuần tự:**

```bash
python test_requests.py --num 5 --mode sequential --server http://10.0.67.77:8080
```

---

## 📊 PHÂN TÍCH KẾT QUẢ

### **Trường hợp 1: 1 Server, không Load Balancer**

```bash
# Test 1 request
python test_requests.py --num 1 --server http://10.0.67.77:5000
# Kết quả: ✅ Thành công, ~23s

# Test 2 requests song song
python test_requests.py --num 2 --mode parallel --server http://10.0.67.77:5000
# Kết quả: ❌ 1 thành công, 1 thất bại
```

**Kết luận:** Server chỉ xử lý được 1 request tại 1 thời điểm.

---

### **Trường hợp 2: 3 Servers + Load Balancer**

```bash
# Test 1 request
python test_requests.py --num 1 --server http://10.0.67.77:8080
# Kết quả: ✅ Thành công, ~23s

# Test 2 requests song song
python test_requests.py --num 2 --mode parallel --server http://10.0.67.77:8080
# Kết quả: ✅ 2/2 thành công, ~23s (không phải ~46s!)

# Test 3 requests song song
python test_requests.py --num 3 --mode parallel --server http://10.0.67.77:8080
# Kết quả: ✅ 3/3 thành công, ~23s (không phải ~69s!)
```

**Kết luận:** Load Balancer chia tải hiệu quả, tăng tốc 3x!

---

## 🎯 BẢNG SO SÁNH

| Số requests | 1 Server | 3 Servers + LB | Tăng tốc |
|-------------|----------|----------------|----------|
| 1 request   | ~23s     | ~23s           | 1x       |
| 2 requests  | ~46s     | ~23s           | 2x       |
| 3 requests  | ~69s     | ~23s           | 3x       |
| 6 requests  | ~138s    | ~46s           | 3x       |

---

## 🛠️ TROUBLESHOOTING

### **Lỗi: Connection refused**

```
[1] ❌ Exception: Connection refused
```

**Nguyên nhân:** Server chưa chạy hoặc URL sai.

**Giải pháp:**
```bash
# Kiểm tra server có chạy không
curl http://10.0.67.77:5000/health

# Hoặc
ssh itsw@10.0.67.77
ps aux | grep api_server
```

---

### **Lỗi: HTTP 500**

```
[2] ❌ Lỗi: HTTP 500
```

**Nguyên nhân:** Server bị quá tải (2 requests cùng lúc).

**Giải pháp:** Dùng Load Balancer!

---

### **Lỗi: Timeout**

```
[1] ❌ Exception: Read timed out
```

**Nguyên nhân:** Text quá dài hoặc server quá chậm.

**Giải pháp:** Tăng timeout trong code (dòng 47):
```python
timeout=180,  # Tăng lên 3 phút
```

---

## 📝 TÓM TẮT

### **Để test nhanh:**

```bash
# Cách 1: Menu tương tác (dễ nhất)
python test_simple.py

# Cách 2: Command-line
python test_requests.py --num 2 --mode parallel --server http://10.0.67.77:8080
```

### **Kết quả mong đợi:**

- ✅ **1 server**: Chỉ xử lý được 1 request/lần
- ✅ **3 servers + Load Balancer**: Xử lý được 3 requests/lần, tăng tốc 3x

---

**Chúc bạn test thành công!** 🚀

