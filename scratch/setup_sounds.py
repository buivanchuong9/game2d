import os
import shutil
import wave
import struct
import math

# Thư mục chứa âm thanh
SOUNDS_DIR = r"c:\Users\daova\Downloads\game2d\Sounds"

# Danh sách đầy đủ các âm thanh demo cần tạo
REQUIRED_SOUNDS = [
    # Vũ khí
    "ban_sung_truong", "ban_tieu_lien", "ban_shotgun", "ban_tia", "ban_b40", "ban_sung_luc", "chem", "thay_dan",
    # Nhân vật
    "nhan_vat_chay", "nhan_vat_chay_nhanh", "nhan_vat_nhay", "nhan_vat_trung_don",
    # Quái vật
    "quai_chet", "quai_trung_dan",
    # Hệ thống & Vật phẩm
    "nhat_xu", "nhat_do", "mo_cong", "hoan_thanh",
    # Nhạc
    "nhac_nen"
]

def generate_dummy_wav(filepath, duration=0.1, freq=440, volume=16383):
    """Tạo một file WAV đơn giản (tiếng beep) làm demo."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            # Sine wave
            value = int(volume * math.sin(2.0 * math.pi * freq * i / sample_rate))
            # Thêm chút noise cho tiếng súng/quái
            if freq < 200:
                import random
                value += random.randint(-2000, 2000)
                
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def setup_demo_sounds():
    print("--- Setting up missing demo sounds (KEEPING existing ones) ---")
    
    # 1. Đảm bảo thư mục tồn tại
    if not os.path.exists(SOUNDS_DIR):
        os.makedirs(SOUNDS_DIR)

    # 2. Tạo các file demo mới
    for key in REQUIRED_SOUNDS:
        # Thử tìm các định dạng phổ biến
        found = False
        for ext in ['.wav', '.mp3', '.ogg']:
            if os.path.exists(os.path.join(SOUNDS_DIR, key + ext)):
                found = True
                break
        
        if found:
            print(f"Skipping: {key} (already exists)")
            continue

        filename = key + ".wav"
        filepath = os.path.join(SOUNDS_DIR, filename)
        
        # Tùy chỉnh đặc tính demo cho từng loại
        duration = 0.1
        freq = 440
        vol = 12000
        
        if "ban_" in key:
            freq = 150
            duration = 0.15
        elif "chem" in key:
            freq = 800
            duration = 0.05
        elif "quai_" in key:
            freq = 200
            duration = 0.2
        elif "nhat_" in key:
            freq = 1000
            duration = 0.05
        elif "nhan_vat_chay" in key:
            freq = 100
            duration = 0.03
            vol = 5000 # Nhỏ hơn cho tiếng bước chân
        elif "nhac_nen" in key:
            duration = 2.0 # Nhạc demo dài hơn chút
            freq = 330
            vol = 8000
            
        generate_dummy_wav(filepath, duration=duration, freq=freq, volume=vol)
        print(f"Created demo sound: {filename}")

    print("--- Finished setting up all demo sounds ---")

if __name__ == "__main__":
    setup_demo_sounds()
