import sys
from pathlib import Path

# Thêm đường dẫn src vào sys.path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from f5_tts.api import F5TTS

# ====== Cấu hình ======
ref_audio = "ref3.mp3"  # file audio tham chiếu (giống trong infer.sh)
ref_text = (
    "hiệu quả là có thể khống chế đại tiện của mục tiêu"  # nội dung của ref audio
)
gen_text = (
    "Bạn đang nghe giọng nói được huấn luyện từ dữ liệu tiếng Việt"  # text cần sinh
)

ckpt_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
vocab_file = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
output_path = "output.wav"

print(f"🟢 Đang khởi tạo F5-TTS model...")

# ====== Khởi tạo F5TTS ======
f5tts = F5TTS(
    model="F5TTS_Base",
    ckpt_file=ckpt_file,
    vocab_file=vocab_file,
)

print(f"🟢 Model đã load xong, bắt đầu inference...")

# ====== Inference ======
wav, sr, spec = f5tts.infer(
    ref_file=ref_audio,
    ref_text=ref_text,
    gen_text=gen_text,
    file_wave=output_path,
    speed=1.0,
)

print(f"✅ Done! File đã lưu: {output_path}")
print(f"   Sample rate: {sr} Hz")
print(f"   Audio shape: {wav.shape}")
