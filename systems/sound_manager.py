import pygame
import os
import glob

class SoundManager:
    """
    Hệ thống quản lý âm thanh (Sound Manager) cho Pygame.
    Tự động load file, cache âm thanh và quản lý volume riêng biệt.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Đường dẫn gốc tới thư mục âm thanh
        # Sử dụng đường dẫn tuyệt đối dựa trên vị trí file này
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sounds_dir = os.path.join(self.base_dir, "Sounds")
        
        self.sounds = {}  # Cache cho Sound objects (SFX)
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.current_music = None
        
        # Khởi tạo mixer nếu chưa có
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.load_all_assets()
        self._initialized = True

    def load_all_assets(self):
        """Tự động quét và load tất cả file trong thư mục Sounds/"""
        extensions = ('.wav', '.mp3', '.ogg')
        
        if not os.path.exists(self.sounds_dir):
            print(f"Warning: Thư mục âm thanh không tồn tại: {self.sounds_dir}")
            return

        # Tìm kiếm đệ quy trong thư mục Sounds/
        search_pattern = os.path.join(self.sounds_dir, "**", "*.*")
        files = glob.glob(search_pattern, recursive=True)
        
        loaded_count = 0
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in extensions:
                # Key là tên file không có phần mở rộng (ví dụ: 'jump' cho 'jump.wav')
                key = os.path.splitext(os.path.basename(file_path))[0]
                
                try:
                    # Load SFX vào cache
                    # Lưu ý: pygame.mixer.Sound phù hợp cho SFX ngắn.
                    # Nhạc nền sẽ dùng pygame.mixer.music (stream từ đĩa).
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[key] = sound
                    loaded_count += 1
                except Exception as e:
                    print(f"Warning: Không thể load âm thanh '{file_path}': {e}")
        
        print(f"[SoundManager] Đã load {loaded_count} file âm thanh từ {self.sounds_dir}")

    def play(self, key):
        """Chơi hiệu ứng âm thanh (SFX) bằng key"""
        if key in self.sounds:
            self.sounds[key].play()
        else:
            # Chỉ in warning, không làm crash game
            print(f"Warning: Không tìm thấy âm thanh key='{key}' trong cache.")

    def play_music(self, key, loops=-1):
        """Chơi nhạc nền (loop). Tự động tìm file phù hợp trong Sounds/"""
        # Vì nhạc nền thường dài, ta không cache toàn bộ vào RAM mà stream từ file
        music_file = None
        extensions = ('.wav', '.mp3', '.ogg')
        
        for ext in extensions:
            potential_path = os.path.join(self.sounds_dir, f"{key}{ext}")
            if os.path.exists(potential_path):
                music_file = potential_path
                break
        
        # Nếu không tìm thấy bằng key trực tiếp, thử tìm trong cache (nếu key là tên file đã quét)
        if not music_file:
            # Tìm trong thư mục con nếu có
            search_pattern = os.path.join(self.sounds_dir, "**", f"{key}.*")
            matches = glob.glob(search_pattern, recursive=True)
            if matches:
                music_file = matches[0]

        if music_file:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = key
            except Exception as e:
                print(f"Warning: Lỗi khi chơi nhạc '{key}': {e}")
        else:
            print(f"Warning: Không tìm thấy file nhạc phù hợp cho key='{key}'")

    def stop_music(self):
        """Dừng nhạc nền"""
        pygame.mixer.music.stop()
        self.current_music = None

    def pause_music(self):
        """Tạm dừng nhạc nền"""
        pygame.mixer.music.pause()

    def resume_music(self):
        """Tiếp tục nhạc nền"""
        pygame.mixer.music.unpause()

    def set_sfx_volume(self, volume):
        """Cập nhật âm lượng SFX (0.0 đến 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, volume):
        """Cập nhật âm lượng Nhạc nền (0.0 đến 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

# Tạo instance duy nhất để sử dụng toàn project
sound_manager = SoundManager()
