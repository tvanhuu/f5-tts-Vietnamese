# 📝 HƯỚNG DẪN TEST VỚI FILE SRT

## 🎯 Tính năng mới

Script `test_requests.py` đã được cập nhật để **đọc text từ file SRT** thay vì dùng text mẫu cố định.

---

## 🚀 CÁCH SỬ DỤNG

### **1. Test với text mẫu (như cũ)**

```bash
# Gửi 1 request
python test_requests.py --num 1

# Gửi 3 requests song song
python test_requests.py --num 3 --mode parallel

# Gửi 5 requests tuần tự
python test_requests.py --num 5 --mode sequential
```

---

### **2. Test với file SRT (MỚI)** ⭐

```bash
# Gửi 5 requests từ file SRT
python test_requests.py --num 5 --srt srt.srt

# Gửi 10 requests song song từ SRT
python test_requests.py --num 10 --srt srt.srt --mode parallel

# Gửi 10 requests tuần tự từ SRT
python test_requests.py --num 10 --srt srt.srt --mode sequential

# Test với Load Balancer
python test_requests.py --num 20 --srt srt.srt --server http://10.0.67.77:8080

# Test với single server
python test_requests.py --num 10 --srt srt.srt --server http://10.0.67.77:5000
```

---

## 📊 VÍ DỤ OUTPUT

### **Khi chạy với SRT:**

```bash
$ python test_requests.py --num 5 --srt srt.srt --mode parallel

📄 Đọc file SRT: srt.srt
✅ Đã đọc 150 đoạn text từ SRT

============================================================
🧪 TTS API TEST
============================================================
🌐 Server: http://10.0.67.77:8080
📊 Số requests: 5
🔄 Chế độ: parallel
⚡ Speed: 0.75
📂 Output: test_output
📝 Số đoạn text: 150
============================================================

============================================================
⚡ TEST SONG SONG - 5 requests
============================================================

[Request 1] 🚀 Bắt đầu gửi...
[Request 1] 📝 Text: một mặt là trước đó đã thực hiện một lượt quy...
[Request 2] 🚀 Bắt đầu gửi...
[Request 2] 📝 Text: trình cho ba môn công pháp cấp cao đặc biệt...
...
```

---

## 🔍 CÁCH HOẠT ĐỘNG

### **1. Parse SRT file**

Script sẽ:
1. Đọc file SRT
2. Tách ra các đoạn text (bỏ qua số thứ tự và timestamp)
3. Lưu vào list

**Ví dụ SRT:**
```
1
00:00:00,000 --> 00:00:02,000
một mặt là trước đó đã thực hiện một lượt quy

2
00:00:02,000 --> 00:00:05,000
trình cho ba môn công pháp cấp cao đặc biệt
```

**Kết quả:**
```python
texts = [
    "một mặt là trước đó đã thực hiện một lượt quy",
    "trình cho ba môn công pháp cấp cao đặc biệt",
]
```

---

### **2. Gửi requests**

- Nếu `--num 5` và SRT có 150 đoạn → Gửi 5 requests đầu tiên
- Nếu `--num 200` và SRT có 150 đoạn → Lặp lại từ đầu (vòng tròn)

**Công thức:**
```python
text = texts[i % len(texts)]
```

---

## 📋 CÁC THAM SỐ

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--num` | Số lượng requests | 1 |
| `--mode` | `parallel` hoặc `sequential` | `parallel` |
| `--server` | URL của server/Load Balancer | `http://10.0.67.77:8080` |
| `--speed` | Tốc độ đọc | 0.75 |
| `--srt` | Đường dẫn file SRT | None (dùng text mẫu) |

---

## 🎯 USE CASES

### **Use Case 1: Test Load Balancer với SRT**

```bash
# Gửi 20 requests song song để test Load Balancer
python test_requests.py --num 20 --srt srt.srt --server http://10.0.67.77:8080
```

**Kết quả:**
- Load Balancer sẽ chia đều 20 requests vào 3 servers (5000, 5001, 5002)
- Mỗi server xử lý ~6-7 requests
- Xem log để biết request nào vào server nào

---

### **Use Case 2: Test performance với nhiều requests**

```bash
# Gửi 50 requests song song
python test_requests.py --num 50 --srt srt.srt --mode parallel

# So sánh với tuần tự
python test_requests.py --num 50 --srt srt.srt --mode sequential
```

**Kết quả:**
- Parallel: ~17 phút (50 requests / 3 servers)
- Sequential: ~50 phút (50 requests x 1 phút/request)

---

### **Use Case 3: Test với đoạn text cụ thể**

```bash
# Tạo file SRT nhỏ với 5 đoạn text cần test
# Rồi chạy:
python test_requests.py --num 5 --srt test.srt
```

---

## 🔧 TROUBLESHOOTING

### **Lỗi: File SRT không tồn tại**

```
❌ Lỗi: File SRT không tồn tại: srt.srt
```

**Giải pháp:**
```bash
# Kiểm tra file có tồn tại không
ls -la srt.srt

# Hoặc dùng đường dẫn đầy đủ
python test_requests.py --num 5 --srt /Users/tvan.huu/Desktop/F5-TTS-Vietnamese/srt.srt
```

---

### **Lỗi: Không đọc được text từ SRT**

```
✅ Đã đọc 0 đoạn text từ SRT
```

**Nguyên nhân:** Format SRT không đúng

**Giải pháp:** Kiểm tra format SRT:
```
1
00:00:00,000 --> 00:00:02,000
Text content here

2
00:00:02,000 --> 00:00:05,000
Another text here
```

---

## 📝 TÓM TẮT

### **Đã thêm:**

- ✅ Hàm `parse_srt()` để đọc file SRT
- ✅ Tham số `--srt` để chỉ định file SRT
- ✅ Tự động fallback về text mẫu nếu không có SRT
- ✅ Hiển thị số đoạn text đã đọc

### **Cách dùng:**

```bash
# Với SRT
python test_requests.py --num 10 --srt srt.srt

# Không SRT (dùng text mẫu)
python test_requests.py --num 10
```

---

**Chúc bạn test thành công!** 🚀

