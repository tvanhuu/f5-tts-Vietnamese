#!/usr/bin/env python3
"""
Script benchmark để test hiệu năng TTS API trên máy Mac
"""

import requests
import time
import platform
import subprocess
import json
from statistics import mean, median, stdev


def get_system_info():
    """
    Lấy thông tin hệ thống
    """
    info = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
    }
    
    # Lấy thông tin chip Apple
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                              capture_output=True, text=True)
        info['cpu'] = result.stdout.strip()
    except:
        info['cpu'] = 'Unknown'
    
    # Lấy thông tin RAM
    try:
        result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                              capture_output=True, text=True)
        ram_bytes = int(result.stdout.strip())
        ram_gb = ram_bytes / (1024**3)
        info['ram_gb'] = f"{ram_gb:.1f} GB"
    except:
        info['ram_gb'] = 'Unknown'
    
    return info


def call_tts_api(text, speed=0.75, api_url="http://10.0.67.77:5000/tts"):
    """
    Gọi TTS API và đo thời gian
    """
    headers = {"Content-Type": "application/json"}
    data = {"text": text, "speed": speed}
    
    start_time = time.time()
    response = requests.post(api_url, headers=headers, json=data, timeout=60)
    end_time = time.time()
    
    return {
        'success': response.status_code == 200,
        'status_code': response.status_code,
        'duration': end_time - start_time,
        'response_size': len(response.content) if response.status_code == 200 else 0
    }


def run_benchmark(num_tests=5):
    """
    Chạy benchmark test
    """
    print("=" * 80)
    print("🧪 BENCHMARK TTS API - HIỆU NĂNG MÁY MAC")
    print("=" * 80)
    
    # Hiển thị thông tin hệ thống
    print("\n📊 THÔNG TIN HỆ THỐNG:")
    print("-" * 80)
    sys_info = get_system_info()
    for key, value in sys_info.items():
        print(f"  {key:20s}: {value}")
    
    # Test cases với độ dài khác nhau
    test_cases = [
        {
            'name': 'Câu ngắn (10-20 từ)',
            'text': 'Cậu Cao, nghe nói nhà cậu đã vỡ nợ, sắp phá sản rồi à?'
        },
        {
            'name': 'Câu trung bình (20-30 từ)',
            'text': 'Nhà tôi đúng là có chút vấn đề, chủ yếu là do hai nguyên nhân quan trọng cần phải giải quyết ngay.'
        },
        {
            'name': 'Câu dài (40+ từ)',
            'text': 'Một mặt là trước đó đã thực hiện một lượt quy trình cho ba môn công pháp cấp cao đặc biệt, chi phí quả thật hơi cao, mặt khác là cha tôi đang chuẩn bị đột phá cảnh giới Niết Bàn.'
        }
    ]
    
    all_results = {}
    
    for test_case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"🔬 TEST: {test_case['name']}")
        print(f"📝 Text: {test_case['text'][:60]}...")
        print(f"📏 Độ dài: {len(test_case['text'])} ký tự")
        print("-" * 80)
        
        durations = []
        
        for i in range(num_tests):
            print(f"\n  Lần {i+1}/{num_tests}...", end=" ", flush=True)
            
            try:
                result = call_tts_api(test_case['text'])
                
                if result['success']:
                    durations.append(result['duration'])
                    print(f"✓ {result['duration']:.2f}s ({result['response_size']/1024:.1f} KB)")
                else:
                    print(f"✗ Lỗi {result['status_code']}")
                    
            except requests.exceptions.Timeout:
                print("✗ Timeout (>60s)")
            except requests.exceptions.ConnectionError:
                print("✗ Không kết nối được API")
            except Exception as e:
                print(f"✗ Lỗi: {e}")
        
        # Tính toán thống kê
        if durations:
            stats = {
                'min': min(durations),
                'max': max(durations),
                'mean': mean(durations),
                'median': median(durations),
                'stdev': stdev(durations) if len(durations) > 1 else 0,
                'total_tests': len(durations),
                'text_length': len(test_case['text'])
            }
            
            all_results[test_case['name']] = stats
            
            print(f"\n  📈 KẾT QUẢ:")
            print(f"     • Nhanh nhất:  {stats['min']:.2f}s")
            print(f"     • Chậm nhất:   {stats['max']:.2f}s")
            print(f"     • Trung bình:  {stats['mean']:.2f}s")
            print(f"     • Trung vị:    {stats['median']:.2f}s")
            if stats['stdev'] > 0:
                print(f"     • Độ lệch:     {stats['stdev']:.2f}s")
            print(f"     • Tốc độ:      {stats['text_length']/stats['mean']:.1f} ký tự/giây")
    
    # Tổng kết
    print(f"\n{'=' * 80}")
    print("📊 TỔNG KẾT:")
    print("-" * 80)
    
    if all_results:
        all_durations = []
        for test_name, stats in all_results.items():
            all_durations.append(stats['mean'])
        
        overall_mean = mean(all_durations)
        print(f"  ⏱️  Thời gian trung bình tổng thể: {overall_mean:.2f}s/đoạn")
        print(f"  🚀 Ước tính xử lý 100 đoạn: {overall_mean * 100 / 60:.1f} phút")
        print(f"  💡 Hiệu năng: ", end="")
        
        if overall_mean < 3:
            print("Rất tốt! ⭐⭐⭐")
        elif overall_mean < 5:
            print("Tốt ⭐⭐")
        elif overall_mean < 10:
            print("Trung bình ⭐")
        else:
            print("Cần tối ưu ⚠️")
    
    # Lưu kết quả
    output_file = "benchmark_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'system_info': sys_info,
            'results': all_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n  💾 Đã lưu kết quả chi tiết vào: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    run_benchmark(num_tests=5)

