#!/bin/bash

# Lấy đường dẫn thư mục hiện tại
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

f5-tts_infer-cli \
--model "F5TTS_Base" \
--ref_audio ref3.mp3 \
--ref_text "rất tốt đây là một lỗi quan trọng và khá phổ biến khi load" \
--gen_text "một mặt là trước đó đã thực hiện một lượt quy trình cho ba môn công pháp cấp cao đặc biệt." \
--speed 1.0 \
--vocoder_name vocos \
--vocab_file "$SCRIPT_DIR/F5-TTS-Vietnamese/config.json" \
--ckpt_file "$SCRIPT_DIR/F5-TTS-Vietnamese/model_last.pt" \