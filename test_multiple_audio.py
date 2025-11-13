import sys
from pathlib import Path

# Thêm đường dẫn src vào sys.path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from f5_tts.api import F5TTS

# ====== Cấu hình ======
ref_audio = "ref3.mp3"  # file audio tham chiếu
ref_text = "hiệu quả là có thể khống chế đại tiện của mục tiêu"

ckpt_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
vocab_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"

print(f"🟢 Đang khởi tạo F5-TTS model (CHỈ 1 LẦN)...")

# ====== Khởi tạo F5TTS 1 LẦN DUY NHẤT ======
f5tts = F5TTS(
    model="F5TTS_Base",
    ckpt_file=ckpt_file,
    vocab_file=vocab_file,
)

print(f"✅ Model đã load xong!\n")

# ====== Tạo NHIỀU audio mà KHÔNG cần khởi tạo lại model ======
texts_to_generate = [
    "cậu cao, nghe nói nhà cậu đã vỡ nợ, sắp phá sản rồi à?",
    "nhà tôi đúng là có chút vấn đề, chủ yếu là do hai nguyên nhân.",
    "một mặt là trước đó đã thực hiện một lượt quy trình cho ba môn công pháp cấp cao đặc biệt.",
    "chi phí quả thật hơi cao.",
    "mặt khác là cha tôi đang chuẩn bị đột phá cảnh giới niết bàn.",
    "các loại vật liệu đắt tiền tiêu tốn rất nhiều.",
    "gần đây cấp trên không hiểu vì sao lại đột nhiên ra tay.",
    "bắt đầu điều tra gia đình chúng tôi, chuỗi tài chính tạm thời bị đứt một chút.",
    "nhưng đừng lo, cha tôi đã nhận được sự ủng hộ của cựu thị trưởng rồi.",
    "trong vòng nửa năm sẽ không có chuyện gì lớn xảy ra.",
]

for i, gen_text in enumerate(texts_to_generate, 1):
    output_path = f"output_{i}.wav"

    print(f"🔊 Đang tạo audio {i}/{len(texts_to_generate)}: {gen_text[:50]}...")

    # Gọi infer() nhiều lần mà KHÔNG cần khởi tạo lại model
    wav, sr, spec = f5tts.infer(
        ref_file=ref_audio,
        ref_text=ref_text,
        gen_text=gen_text,
        file_wave=output_path,
        speed=1.0,
    )

    print(f"   ✅ Đã lưu: {output_path}\n")

print(
    f"🎉 Hoàn thành! Đã tạo {len(texts_to_generate)} file audio chỉ với 1 lần khởi tạo model."
)
