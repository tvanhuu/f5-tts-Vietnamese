"""
TTS Service - Singleton pattern để tái sử dụng model
Khởi tạo model 1 lần duy nhất, sau đó tạo audio nhiều lần
"""

import sys
from pathlib import Path

# Thêm đường dẫn src vào sys.path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from f5_tts.api import F5TTS


class TTSService:
    """
    Singleton service để quản lý F5-TTS model
    Model chỉ được khởi tạo 1 lần duy nhất
    """

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Chỉ khởi tạo model nếu chưa có
        if self._model is None:
            print("🟢 Đang khởi tạo F5-TTS model lần đầu tiên...")
            self._initialize_model()
            print("✅ Model đã sẵn sàng!\n")

    def _initialize_model(self):
        """Khởi tạo model - chỉ chạy 1 lần"""
        # Lấy đường dẫn thư mục hiện tại
        from pathlib import Path

        script_dir = Path(__file__).resolve().parent
        ckpt_file = script_dir / "F5-TTS-Vietnamese" / "model_last.pt"
        vocab_file = script_dir / "F5-TTS-Vietnamese" / "config.json"

        print(f"📂 Model checkpoint: {ckpt_file}")
        print(f"📂 Vocab file: {vocab_file}")

        self._model = F5TTS(
            model="F5TTS_Base",
            ckpt_file=str(ckpt_file),
            vocab_file=str(vocab_file),
        )

    def generate_speech(
        self,
        text: str,
        ref_audio: str = "ref3.mp3",
        ref_text: str = "hiệu quả là có thể khống chế đại tiện của mục tiêu",
        output_path: str = "output.wav",
        speed: float = 1.0,
    ):
        """
        Tạo audio từ text

        Args:
            text: Văn bản cần chuyển thành giọng nói
            ref_audio: File audio tham chiếu
            ref_text: Nội dung của audio tham chiếu
            output_path: Đường dẫn lưu file output
            speed: Tốc độ đọc (1.0 = bình thường)

        Returns:
            tuple: (wav, sample_rate, spectrogram)
        """
        print(f"🔊 Đang tạo audio: {text[:50]}...")

        wav, sr, spec = self._model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            file_wave=output_path,
            speed=speed,
        )

        print(f"   ✅ Đã lưu: {output_path}")
        return wav, sr, spec


# ====== Ví dụ sử dụng ======
if __name__ == "__main__":
    # Khởi tạo service (model chỉ load 1 lần)
    tts = TTSService()

    # Tạo nhiều audio - model KHÔNG bị load lại
    texts = [
        "Xin chào, đây là bài kiểm tra số một",
        "Đây là bài kiểm tra số hai với nội dung khác",
        "Và đây là bài kiểm tra cuối cùng",
    ]

    for i, text in enumerate(texts, 1):
        tts.generate_speech(text=text, output_path=f"output_service_{i}.wav")

    print("\n🎉 Hoàn thành!")

    # Nếu tạo thêm instance mới, model vẫn KHÔNG bị load lại
    print("\n--- Tạo instance mới (model KHÔNG load lại) ---")
    tts2 = TTSService()  # Không in "Đang khởi tạo..." vì đã có rồi

    tts2.generate_speech(
        text="Instance mới nhưng dùng chung model", output_path="output_service_4.wav"
    )
