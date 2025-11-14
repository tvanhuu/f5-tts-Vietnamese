#!/usr/bin/env python3
"""
Script benchmark để test hiệu năng TTS API với số luồng song song khác nhau
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean


def call_tts_api(text, speed=0.75, api_url="http://10.0.67.77:5000/tts"):
    """
    Gọi TTS API và đo thời gian
    """
    headers = {"Content-Type": "application/json"}
    data = {"text": text, "speed": speed}

    start_time = time.time()
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=120)
        end_time = time.time()

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "duration": end_time - start_time,
            "response_size": (
                len(response.content) if response.status_code == 200 else 0
            ),
        }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "status_code": 0,
            "duration": end_time - start_time,
            "response_size": 0,
            "error": str(e),
        }


def test_sequential(texts, num_requests):
    """
    Test chạy tuần tự (1 luồng)
    """
    print(f"\n🔄 Chạy tuần tự (1 request/lần)...")

    start_time = time.time()
    results = []

    for i, text in enumerate(texts[:num_requests], 1):
        print(f"  [{i}/{num_requests}]", end=" ", flush=True)
        result = call_tts_api(text)
        results.append(result)
        if result["success"]:
            print(f"✓ {result['duration']:.2f}s")
        else:
            print(f"✗ Lỗi")

    total_time = time.time() - start_time

    return {"total_time": total_time, "results": results, "num_workers": 1}


def test_parallel(texts, num_requests, num_workers):
    """
    Test chạy song song với số luồng xác định
    """
    print(f"\n⚡ Chạy song song ({num_workers} requests/lần)...")

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit tất cả tasks
        future_to_text = {
            executor.submit(call_tts_api, text): (i, text)
            for i, text in enumerate(texts[:num_requests], 1)
        }

        # Lấy kết quả khi hoàn thành
        completed = 0
        for future in as_completed(future_to_text):
            i, text = future_to_text[future]
            result = future.result()
            results.append(result)
            completed += 1

            if result["success"]:
                print(
                    f"  [{completed}/{num_requests}] ✓ Request #{i}: {result['duration']:.2f}s"
                )
            else:
                print(f"  [{completed}/{num_requests}] ✗ Request #{i}: Lỗi")

    total_time = time.time() - start_time

    return {"total_time": total_time, "results": results, "num_workers": num_workers}


def analyze_results(test_result):
    """
    Phân tích kết quả test
    """
    successful = [r for r in test_result["results"] if r["success"]]
    failed = len(test_result["results"]) - len(successful)

    if not successful:
        return None

    durations = [r["duration"] for r in successful]

    return {
        "total_time": test_result["total_time"],
        "num_workers": test_result["num_workers"],
        "total_requests": len(test_result["results"]),
        "successful": len(successful),
        "failed": failed,
        "avg_request_time": mean(durations),
        "min_request_time": min(durations),
        "max_request_time": max(durations),
        "throughput": len(successful) / test_result["total_time"],  # requests/second
        "time_per_request": test_result["total_time"]
        / len(successful),  # seconds/request
    }


def run_benchmark():
    """
    Chạy benchmark với các cấu hình khác nhau
    """
    print("=" * 80)
    print("🧪 BENCHMARK TTS API - SO SÁNH SỐ LUỒNG SONG SONG TỐI ƯU")
    print("=" * 80)

    # Chuẩn bị test data
    test_texts = [
        "Cậu Cao, nghe nói nhà cậu đã vỡ nợ, sắp phá sản rồi à?",
        "Nhà tôi đúng là có chút vấn đề, chủ yếu là do hai nguyên nhân.",
        "Một mặt là trước đó đã thực hiện một lượt quy trình cho ba môn công pháp cấp cao đặc biệt.",
        "Chi phí quả thật hơi cao.",
        "Mặt khác là cha tôi đang chuẩn bị đột phá cảnh giới Niết Bàn.",
        "Các loại vật liệu đắt tiền tiêu tốn rất nhiều.",
        "Gần đây cấp trên không hiểu vì sao lại đột nhiên ra tay.",
        "Bắt đầu điều tra gia đình chúng tôi, chuỗi tài chính tạm thời bị đứt một chút.",
        "Nhưng đừng lo, cha tôi đã nhận được sự ủng hộ của cựu thị trưởng rồi.",
        "Trong vòng nửa năm sẽ không có chuyện gì lớn xảy ra.",
    ]

    num_requests = 10  # Số request để test
    worker_configs = [1, 2, 3, 4, 5, 6]  # Các cấu hình số luồng để test

    print(f"\n📊 Cấu hình test:")
    print(f"  • Số requests: {num_requests}")
    print(f"  • Các cấu hình luồng: {worker_configs}")
    print(f"  • API: http://10.0.67.77:5000/tts")

    all_results = []

    # Test từng cấu hình
    for num_workers in worker_configs:
        print(f"\n{'=' * 80}")
        print(f"🔬 TEST: {num_workers} luồng song song")
        print("-" * 80)

        if num_workers == 1:
            test_result = test_sequential(test_texts, num_requests)
        else:
            test_result = test_parallel(test_texts, num_requests, num_workers)

        analysis = analyze_results(test_result)

        if analysis:
            all_results.append(analysis)

            print(f"\n  📈 KẾT QUẢ:")
            print(f"     • Tổng thời gian:        {analysis['total_time']:.2f}s")
            print(
                f"     • Thành công/Tổng:       {analysis['successful']}/{analysis['total_requests']}"
            )
            print(f"     • Thời gian TB/request:  {analysis['time_per_request']:.2f}s")
            print(
                f"     • Throughput:            {analysis['throughput']:.2f} requests/s"
            )
            print(f"     • Request nhanh nhất:    {analysis['min_request_time']:.2f}s")
            print(f"     • Request chậm nhất:     {analysis['max_request_time']:.2f}s")

    # So sánh và tìm cấu hình tối ưu
    print(f"\n{'=' * 80}")
    print("📊 SO SÁNH CÁC CẤU HÌNH:")
    print("=" * 80)

    if not all_results:
        print("❌ Không có kết quả nào thành công!")
        return

    # Sắp xếp theo tổng thời gian (nhanh nhất)
    sorted_by_time = sorted(all_results, key=lambda x: x["total_time"])

    # Sắp xếp theo throughput (cao nhất)
    sorted_by_throughput = sorted(
        all_results, key=lambda x: x["throughput"], reverse=True
    )

    print(
        f"\n{'Luồng':<8} {'Tổng TG':<12} {'TG/Request':<15} {'Throughput':<15} {'Hiệu suất':<12}"
    )
    print("-" * 80)

    baseline = all_results[0]["total_time"]  # Thời gian của cấu hình 1 luồng

    for result in all_results:
        speedup = baseline / result["total_time"]
        efficiency = (speedup / result["num_workers"]) * 100

        # Đánh dấu cấu hình tốt nhất
        marker = "⭐" if result == sorted_by_time[0] else "  "

        print(
            f"{marker} {result['num_workers']:<6} "
            f"{result['total_time']:<10.2f}s "
            f"{result['time_per_request']:<13.2f}s "
            f"{result['throughput']:<13.2f}/s "
            f"{speedup:.2f}x ({efficiency:.0f}%)"
        )

    # Tìm cấu hình tối ưu
    best_config = sorted_by_time[0]
    speedup = baseline / best_config["total_time"]

    print(f"\n{'=' * 80}")
    print("🏆 KẾT LUẬN:")
    print("-" * 80)
    print(f"  ✅ Cấu hình tối ưu: {best_config['num_workers']} luồng song song")
    print(f"  ⏱️  Tổng thời gian: {best_config['total_time']:.2f}s")
    print(f"  🚀 Nhanh hơn tuần tự: {speedup:.2f}x ({(speedup-1)*100:.0f}% faster)")
    print(f"  📊 Throughput: {best_config['throughput']:.2f} requests/s")
    print(f"  💡 Thời gian/request: {best_config['time_per_request']:.2f}s")

    # Ước tính cho file SRT
    print(f"\n  📝 ƯỚC TÍNH CHO FILE SRT (10 đoạn):")
    print(f"     • Với 1 luồng:  {baseline:.0f}s ({baseline/60:.1f} phút)")
    print(
        f"     • Với {best_config['num_workers']} luồng:  {best_config['total_time']:.0f}s ({best_config['total_time']/60:.1f} phút)"
    )
    print(
        f"     • Tiết kiệm:    {baseline - best_config['total_time']:.0f}s ({(baseline - best_config['total_time'])/60:.1f} phút)"
    )

    # Khuyến nghị
    print(f"\n  💡 KHUYẾN NGHỊ:")

    # Tìm điểm diminishing returns
    efficiency_threshold = 70  # Hiệu suất dưới 70% coi là không hiệu quả

    for i, result in enumerate(all_results):
        speedup = baseline / result["total_time"]
        efficiency = (speedup / result["num_workers"]) * 100

        if efficiency < efficiency_threshold and result["num_workers"] > 1:
            print(f"     • Không nên dùng quá {result['num_workers']-1} luồng")
            print(
                f"       (Hiệu suất giảm: {efficiency:.0f}% < {efficiency_threshold}%)"
            )
            break
    else:
        print(
            f"     • Có thể thử tăng số luồng lên {all_results[-1]['num_workers']+1}-{all_results[-1]['num_workers']+2}"
        )
        print(f"       để xem có cải thiện thêm không")

    # Lưu kết quả
    output_file = "benchmark_parallel_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "results": all_results,
                "best_config": best_config,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n  💾 Đã lưu kết quả chi tiết vào: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
