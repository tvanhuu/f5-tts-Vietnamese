# 🧪 TEST TTS API - Hướng dẫn nhanh

## 🎯 Mục đích

Test xem server có xử lý được **nhiều requests cùng lúc** không.

---

## 🚀 CÁCH NHANH NHẤT (Khuyến nghị)

### **Chạy test với menu tương tác:**

```bash
python test_simple.py
```

### **Menu sẽ hiện ra:**

```
📋 MENU:
  1. Test 1 request
  2. Test 2 requests (tuần tự)
  3. Test 2 requests (song song)  ← Chọn cái này để test!
  4. Test 3 requests (song song)
  5. Thay đổi server URL
  0. Thoát

👉 Chọn (0-5):
```

---

## 📊 KẾT QUẢ MONG ĐỢI

### **Test với 1 server (không Load Balancer):**

```bash
# Trong menu, chọn 5 để đổi URL
Server: http://10.0.67.77:5000

# Chọn 3: Test 2 requests song song
```

**Kết quả:**
```
[1] ✅ Thành công! (23.2s, 2.1MB)
[2] ❌ Lỗi: HTTP 500

📊 KẾT QUẢ
✅ Thành công: 1/2  ← Chỉ 1 request thành công!
```

**→ Server chỉ xử lý được 1 request tại 1 thời điểm** ❌

---

### **Test với Load Balancer:**

```bash
# Trong menu, chọn 5 để đổi URL
Server: http://10.0.67.77:8080

# Chọn 3: Test 2 requests song song
```

**Kết quả:**
```
[1] ✅ Thành công! (23.2s, 2.1MB)
[2] ✅ Thành công! (23.5s, 2.2MB)

📊 KẾT QUẢ
✅ Thành công: 2/2  ← Cả 2 requests đều thành công!
⏱️  Tổng thời gian: 23.8s  ← Chỉ mất ~23s thay vì ~46s!
```

**→ Load Balancer chia tải thành công, tăng tốc 2x!** ✅

---

## 🔧 CÁCH 2: Command-line

### **Test 1 request:**

```bash
python test_requests.py --num 1 --server http://10.0.67.77:5000
```

### **Test 2 requests song song:**

```bash
python test_requests.py --num 2 --mode parallel --server http://10.0.67.77:5000
```

### **Test 3 requests song song (với Load Balancer):**

```bash
python test_requests.py --num 3 --mode parallel --server http://10.0.67.77:8080
```

---

## 📋 BẢNG SO SÁNH

| Trường hợp | Số requests thành công | Thời gian | Tăng tốc |
|------------|------------------------|-----------|----------|
| **1 server, 1 request** | 1/1 | ~23s | 1x |
| **1 server, 2 requests song song** | 1/2 | ~23s | ❌ Lỗi |
| **Load Balancer, 2 requests song song** | 2/2 | ~23s | 2x ✅ |
| **Load Balancer, 3 requests song song** | 3/3 | ~23s | 3x ✅ |

---

## 🎯 KẾT LUẬN

### **Không có Load Balancer:**
- ❌ Chỉ xử lý được 1 request tại 1 thời điểm
- ❌ Requests thứ 2, 3 sẽ bị lỗi hoặc phải chờ

### **Có Load Balancer + 3 servers:**
- ✅ Xử lý được 3 requests cùng lúc
- ✅ Tăng tốc 3x
- ✅ Phân phối tải đều

---

## 🚀 HƯỚNG DẪN CHI TIẾT

Xem file `HUONG_DAN_TEST.md` để biết thêm chi tiết!

---

## 📁 Files

| File | Mô tả |
|------|-------|
| `test_simple.py` | Test với menu tương tác (dễ nhất) ⭐ |
| `test_requests.py` | Test với command-line arguments |
| `HUONG_DAN_TEST.md` | Hướng dẫn chi tiết |

---

**Chúc bạn test thành công!** 🚀

