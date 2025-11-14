#!/bin/bash
# Script test nhanh cho tts_worker.py

echo "============================================================"
echo "🧪 TEST TTS WORKER"
echo "============================================================"
echo ""

# Kiểm tra file tồn tại
if [ ! -f "tts_worker.py" ]; then
    echo "❌ Không tìm thấy tts_worker.py"
    exit 1
fi

if [ ! -f "srt.srt" ]; then
    echo "❌ Không tìm thấy srt.srt"
    exit 1
fi

# Menu
echo "Chọn test case:"
echo "1. Test với 1 worker (chậm nhất, an toàn nhất)"
echo "2. Test với 2 workers (cân bằng)"
echo "3. Test với 3 workers (nhanh nhất)"
echo "4. Test resume (chạy 5 tasks rồi dừng, sau đó resume)"
echo "5. Xem checkpoint hiện tại"
echo "6. Xóa checkpoint (reset)"
echo ""
read -p "Nhập lựa chọn (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Chạy với 1 worker..."
        python3 tts_worker.py --workers 1 --srt srt.srt
        ;;
    2)
        echo ""
        echo "🚀 Chạy với 2 workers..."
        python3 tts_worker.py --workers 2 --srt srt.srt
        ;;
    3)
        echo ""
        echo "🚀 Chạy với 3 workers..."
        python3 tts_worker.py --workers 3 --srt srt.srt
        ;;
    4)
        echo ""
        echo "🧪 Test Resume:"
        echo "Bước 1: Chạy 5 tasks rồi Ctrl+C để dừng"
        echo "Bước 2: Chạy lại để resume"
        echo ""
        read -p "Nhấn Enter để bắt đầu bước 1..."
        
        # Tạo script Python tạm để chạy 5 tasks rồi dừng
        cat > test_resume_temp.py << 'EOF'
import sys
import subprocess
import time
import signal

# Chạy tts_worker.py
proc = subprocess.Popen(
    ["python3", "tts_worker.py", "--workers", "2", "--srt", "srt.srt"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

completed_count = 0
for line in proc.stdout:
    print(line, end='')
    if "✅ Thành công!" in line:
        completed_count += 1
        if completed_count >= 5:
            print("\n🛑 Đã xử lý 5 tasks, dừng lại...")
            proc.send_signal(signal.SIGINT)
            time.sleep(2)
            proc.kill()
            break

proc.wait()
EOF
        
        python3 test_resume_temp.py
        rm test_resume_temp.py
        
        echo ""
        echo "✅ Bước 1 hoàn thành!"
        echo ""
        read -p "Nhấn Enter để chạy bước 2 (Resume)..."
        
        python3 tts_worker.py --workers 2 --srt srt.srt
        ;;
    5)
        echo ""
        if [ -f "output_audio/.checkpoint.json" ]; then
            echo "📋 Checkpoint hiện tại:"
            echo ""
            cat output_audio/.checkpoint.json | python3 -m json.tool
            echo ""
            
            # Thống kê
            completed=$(cat output_audio/.checkpoint.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('completed', [])))")
            failed=$(cat output_audio/.checkpoint.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('failed', [])))")
            in_progress=$(cat output_audio/.checkpoint.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('in_progress', [])))")
            
            echo "📊 Thống kê:"
            echo "  ✅ Completed: $completed"
            echo "  ❌ Failed: $failed"
            echo "  🔄 In progress: $in_progress"
        else
            echo "❌ Chưa có checkpoint"
        fi
        ;;
    6)
        echo ""
        if [ -f "output_audio/.checkpoint.json" ]; then
            read -p "⚠️  Bạn có chắc muốn xóa checkpoint? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                rm output_audio/.checkpoint.json
                echo "✅ Đã xóa checkpoint"
            else
                echo "❌ Hủy bỏ"
            fi
        else
            echo "❌ Không có checkpoint để xóa"
        fi
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "✅ HOÀN THÀNH"
echo "============================================================"

