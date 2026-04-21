# audio.py
# Quản lý nhạc nền và hiệu ứng âm thanh cho game
import pygame
import os
import glob

# Absolute path of the game directory — used for sound discovery.
# No os.chdir here; audio.py is self-contained via absolute paths.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOUND_EFFECTS = {}
SOUND_BY_BASENAME = {}
SOUND_EXTS = (".mp3", ".wav", ".ogg")

# Mapping key -> candidate base filenames (WITHOUT extension).
SOUND_CANDIDATES = {
    "sfx_shot_rifle": ["ban_sung_truong", "sfx_gun_shot"],
    "sfx_shot_smg": ["ban_tieu_lien"],
    "sfx_shot_shotgun": ["ban_shotgun"],
    "sfx_shot_sniper": ["ban_tia"],
    "sfx_shot_rocket": ["ban_b40"],
    "sfx_shot_melee": ["chem"],
    "sfx_reload_rifle": ["thay_dan_sung_truong", "sfx_reload"],
    "sfx_reload_smg": ["thay_dan_tieu_lien", "sfx_reload"],
    "sfx_reload_shotgun": ["thay_dan_shotgun", "sfx_reload"],
    "sfx_reload_sniper": ["thay_dan_tia", "sfx_reload"],
    "sfx_reload_rocket": ["thay_dan_b40", "sfx_reload"],
    "sfx_enemy_hit": ["zombie_trung_dan", "sfx_enemy_hit"],
    "sfx_enemy_death": ["zombie_chet", "sfx_enemy_death"],
    "sfx_player_hit": ["nhan_vat_trung_don", "sfx_player_hit"],
    "sfx_gate_open": ["mo_cong", "sfx_gate_open"],
    "sfx_item_drop": ["roi_vat_pham", "sfx_item_drop"],
    "sfx_quest_complete": ["hoan_thanh_nhiem_vu", "sfx_quest_complete"],
}

def load_sounds():
    sounds_dir = os.path.join(BASE_DIR, "Sounds")
    for path in glob.glob(os.path.join(sounds_dir, "**", "*.*"), recursive=True):
        if not path.lower().endswith(SOUND_EXTS):
            continue
        try:
            SOUND_EFFECTS[path] = pygame.mixer.Sound(path)
            SOUND_BY_BASENAME[os.path.basename(path).lower()] = SOUND_EFFECTS[path]
        except Exception as e:
            print(f"[SOUND LOAD ERROR] {path}: {e}")

def play_bg_music():
    try:
        primary = os.path.join(BASE_DIR, "Sounds", "nhac_nen_chinh.mp3")
        fallback = os.path.join(BASE_DIR, "Sounds", "Game_loop_music.mp3")
        if os.path.exists(primary):
            pygame.mixer.music.load(primary)
        else:
            pygame.mixer.music.load(fallback)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[MUSIC ERROR] {e}")

def play_sound_effect(name):
    key = (name or "").strip()
    if not key:
        return
    bases = SOUND_CANDIDATES.get(key)
    candidates = []
    if bases:
        for base in bases:
            for ext in SOUND_EXTS:
                candidates.append(f"{base}{ext}")
    else:
        lower = key.lower()
        candidates.append(lower)
        root, dot, ext = lower.rpartition(".")
        if dot and ext:
            for e in SOUND_EXTS:
                candidates.append(f"{root}{e}")
        else:
            for e in SOUND_EXTS:
                candidates.append(f"{lower}{e}")
    for fname in candidates:
        snd = SOUND_BY_BASENAME.get(fname.lower())
        if snd:
            snd.play()
            return
