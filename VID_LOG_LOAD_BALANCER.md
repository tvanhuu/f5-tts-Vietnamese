# 📊 VÍ DỤ LOG CỦA LOAD BALANCER

## 🎯 Sau khi sửa, log sẽ hiển thị như thế nào

### **Khi chạy Load Balancer:**

```bash
tail -f logs/load_balancer.log
```

### **Output mẫu:**

```
============================================================
🔀 LOAD BALANCER - Forwarding Request
============================================================
📝 Text: Xin chào, đây là câu test thứ nhất...
🎯 Target Server: http://localhost:5000
⏰ Time: 2025-11-14 15:23:45
============================================================

✅ Response from http://localhost:5000: HTTP 200 (23.2s, 2.1MB)

============================================================
🔀 LOAD BALANCER - Forwarding Request
============================================================
📝 Text: Câu test thứ hai dài hơn một chút để kiểm tra...
🎯 Target Server: http://localhost:5001
⏰ Time: 2025-11-14 15:23:46
============================================================

✅ Response from http://localhost:5001: HTTP 200 (23.5s, 2.2MB)

============================================================
🔀 LOAD BALANCER - Forwarding Request
============================================================
📝 Text: Đây là câu test thứ ba, ngắn gọn...
🎯 Target Server: http://localhost:5002
⏰ Time: 2025-11-14 15:23:47
============================================================

✅ Response from http://localhost:5002: HTTP 200 (23.1s, 2.0MB)

============================================================
🔀 LOAD BALANCER - Forwarding Request
============================================================
📝 Text: Câu test thứ tư với nội dung khác nhau...
🎯 Target Server: http://localhost:5000  ← Quay lại server 1
⏰ Time: 2025-11-14 15:24:10
============================================================

✅ Response from http://localhost:5000: HTTP 200 (22.8s, 2.1MB)
```

---

## 🔍 PHÂN TÍCH LOG

### **Thông tin hiển thị:**

1. **📝 Text**: Preview của text cần chuyển thành giọng (50 ký tự đầu)
2. **🎯 Target Server**: Server nào được chọn để xử lý request
3. **⏰ Time**: Thời gian request được gửi
4. **✅/❌ Response**: Kết quả từ server
   - HTTP status code
   - Thời gian xử lý
   - Kích thước file (nếu thành công)

---

## 🎯 CÁCH ĐỌC LOG

### **Ví dụ 1: Phân phối đều**

```
Request 1 → Server 5000
Request 2 → Server 5001
Request 3 → Server 5002
Request 4 → Server 5000  ← Round-robin
Request 5 → Server 5001
Request 6 → Server 5002
```

✅ **Load Balancer hoạt động đúng!**

---

### **Ví dụ 2: Có lỗi**

```
============================================================
🔀 LOAD BALANCER - Forwarding Request
============================================================
📝 Text: Test request...
🎯 Target Server: http://localhost:5001
⏰ Time: 2025-11-14 15:25:00
============================================================

❌ Error forwarding to http://localhost:5001: Connection refused (0.1s)
```

❌ **Server 5001 không hoạt động!**

**Giải pháp:**
```bash
# Kiểm tra server
ssh itsw@10.0.67.77
ps aux | grep api_server

# Restart nếu cần
./stop_all.sh
VENV_PATH=/path/to/venv ./start_with_loadbalancer.sh
```

---

## 📊 THEO DÕI REAL-TIME

### **Xem log liên tục:**

```bash
# Trên server
ssh itsw@10.0.67.77
cd /Users/itsw/Desktop/F5-TTS-Vietnamese_1

# Xem log Load Balancer
tail -f logs/load_balancer.log

# Hoặc xem tất cả logs
tail -f logs/*.log
```

### **Lọc log theo server:**

```bash
# Chỉ xem requests đến server 5000
tail -f logs/load_balancer.log | grep "5000"

# Chỉ xem requests thành công
tail -f logs/load_balancer.log | grep "✅"

# Chỉ xem requests lỗi
tail -f logs/load_balancer.log | grep "❌"
```

---

## 🎯 THỐNG KÊ TỪ LOG

### **Đếm số requests mỗi server:**

```bash
# Đếm requests đến server 5000
grep "Target Server: http://localhost:5000" logs/load_balancer.log | wc -l

# Đếm requests đến server 5001
grep "Target Server: http://localhost:5001" logs/load_balancer.log | wc -l

# Đếm requests đến server 5002
grep "Target Server: http://localhost:5002" logs/load_balancer.log | wc -l
```

### **Đếm requests thành công/thất bại:**

```bash
# Đếm thành công
grep "✅ Response" logs/load_balancer.log | wc -l

# Đếm thất bại
grep "❌" logs/load_balancer.log | wc -l
```

---

## 🔧 TROUBLESHOOTING

### **Vấn đề 1: Không thấy log**

```bash
# Kiểm tra file log có tồn tại không
ls -la logs/load_balancer.log

# Kiểm tra Load Balancer có chạy không
ps aux | grep load_balancer

# Restart
./stop_all.sh
VENV_PATH=/path/to/venv ./start_with_loadbalancer.sh
```

---

### **Vấn đề 2: Log không update**

```bash
# Kiểm tra process
ps aux | grep load_balancer

# Kiểm tra port
lsof -i :8080

# Restart
./stop_all.sh
sleep 2
VENV_PATH=/path/to/venv ./start_with_loadbalancer.sh
```

---

### **Vấn đề 3: Tất cả requests đều đến 1 server**

```
Request 1 → Server 5000
Request 2 → Server 5000  ← Sai! Phải là 5001
Request 3 → Server 5000  ← Sai! Phải là 5002
```

**Nguyên nhân:** Có thể server 5001 và 5002 không chạy.

**Giải pháp:**
```bash
# Kiểm tra tất cả servers
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health

# Restart tất cả
./stop_all.sh
VENV_PATH=/path/to/venv ./start_with_loadbalancer.sh
```

---

## 📝 TÓM TẮT

### **Xem log:**

```bash
tail -f logs/load_balancer.log
```

### **Log sẽ hiển thị:**

- ✅ Request nào đến server nào
- ✅ Thời gian xử lý
- ✅ Kích thước file
- ✅ Lỗi (nếu có)

### **Kiểm tra phân phối:**

```bash
grep "Target Server" logs/load_balancer.log | tail -20
```

Sẽ thấy pattern:
```
5000 → 5001 → 5002 → 5000 → 5001 → 5002 → ...
```

✅ **Round-robin hoạt động đúng!**

---

**Chúc bạn monitoring thành công!** 🚀

