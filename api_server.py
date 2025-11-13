"""
Flask API Server cho F5-TTS
Model được khởi tạo 1 lần khi server start, sau đó tái sử dụng cho mọi request
"""
from flask import Flask, request, jsonify, send_file
import sys
from pathlib import Path
import uuid
import os

# Thêm đường dẫn src vào sys.path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from f5_tts.api import F5TTS

app = Flask(__name__)

# ====== KHỞI TẠO MODEL 1 LẦN KHI SERVER START ======
print("🟢 Đang khởi tạo F5-TTS model...")

CKPT_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/model_last.pt"
VOCAB_FILE = "/Users/tvan.huu/Desktop/F5-TTS-Vietnamese/F5-TTS-Vietnamese/config.json"
DEFAULT_REF_AUDIO = "ref3.mp3"
DEFAULT_REF_TEXT = "hiệu quả là có thể khống chế đại tiện của mục tiêu"

# Model global - khởi tạo 1 lần duy nhất
tts_model = F5TTS(
    model="F5TTS_Base",
    ckpt_file=CKPT_FILE,
    vocab_file=VOCAB_FILE,
)

print("✅ Model đã sẵn sàng! Server có thể nhận request.\n")

# Tạo thư mục lưu output
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra server có hoạt động không"""
    return jsonify({
        "status": "ok",
        "model": "F5-TTS Vietnamese",
        "message": "Model đã được load và sẵn sàng"
    })


@app.route('/tts', methods=['POST'])
def text_to_speech():
    """
    API endpoint để chuyển text thành speech
    
    Request body (JSON):
    {
        "text": "Văn bản cần chuyển thành giọng nói",
        "ref_audio": "ref3.mp3" (optional),
        "ref_text": "..." (optional),
        "speed": 1.0 (optional)
    }
    
    Response:
    - File audio .wav
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        ref_audio = data.get('ref_audio', DEFAULT_REF_AUDIO)
        ref_text = data.get('ref_text', DEFAULT_REF_TEXT)
        speed = data.get('speed', 1.0)
        
        # Tạo tên file unique
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        print(f"🔊 Request: {text[:50]}...")
        
        # Sử dụng model đã được khởi tạo sẵn (KHÔNG khởi tạo lại)
        wav, sr, spec = tts_model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            file_wave=str(output_path),
            speed=speed,
        )
        
        print(f"   ✅ Generated: {output_filename}")
        
        # Trả về file audio
        return send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/tts/json', methods=['POST'])
def text_to_speech_json():
    """
    API endpoint trả về thông tin JSON thay vì file
    
    Response:
    {
        "success": true,
        "file_path": "outputs/xxx.wav",
        "sample_rate": 24000,
        "duration": 2.5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        ref_audio = data.get('ref_audio', DEFAULT_REF_AUDIO)
        ref_text = data.get('ref_text', DEFAULT_REF_TEXT)
        speed = data.get('speed', 1.0)
        
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = OUTPUT_DIR / output_filename
        
        # Sử dụng model đã được khởi tạo sẵn
        wav, sr, spec = tts_model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            file_wave=str(output_path),
            speed=speed,
        )
        
        duration = len(wav) / sr
        
        return jsonify({
            "success": True,
            "file_path": str(output_path),
            "sample_rate": sr,
            "duration": duration,
            "text": text
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 F5-TTS API Server")
    print("="*50)
    print("Endpoints:")
    print("  - GET  /health       : Kiểm tra server")
    print("  - POST /tts          : Tạo audio (trả về file)")
    print("  - POST /tts/json     : Tạo audio (trả về JSON)")
    print("="*50 + "\n")
    
    # Chạy server
    app.run(host='0.0.0.0', port=5000, debug=False)

