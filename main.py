from core.game import main


if __name__ == "__main__":
    main()
# Resolve working directory FIRST before any imports that load assets
import os as _os
_os.chdir(_os.path.dirname(_os.path.abspath(__file__)))

# NOTE: map_props import is deferred to after pygame.display.set_mode()
# because safe_load calls convert_alpha() which requires an initialized display.

# Màu và hằng số giao diện bổ sung
GRAY = (120, 120, 120)
SOFT = (200, 200, 220)
STROKE = (40, 44, 54)
CARD = (28, 30, 40)
CARD_ALT = (38, 40, 50)
OVERLAY = (10, 8, 12, 180)
PANEL = (24, 26, 34)
FPS = 60
import pygame
import math
import os
import random
import sys
import glob
from dataclasses import dataclass, field
from armory_data import ARMORY, RARITY_COLORS
from scratch.print_map import carve
from systems.sound_manager import sound_manager
# VÍ DỤ SỬ DỤNG SoundManager:
# sound_manager.play("jump")          # Chơi hiệu ứng âm thanh jump.wav/mp3
# sound_manager.play_music("bgm")    # Chơi nhạc nền bgm.wav/mp3 (lặp)
# sound_manager.set_music_volume(0.3) # Chỉnh âm lượng nhạc nền
# sound_manager.stop_music()         # Dừng nhạc nền
from data import ItemPickup, Particle, NPC, Chapter, StoryEnemy, EscortTank, MissionTracker

# Định nghĩa các màu cơ bản
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 128, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)

pygame.init()

# --- Cấu hình màn hình (Bắt buộc trước khi load ảnh có .convert_alpha) ---
SIDEBAR_WIDTH = 256
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
MAP_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT
# Fullscreen + scaled rendering (keeps internal resolution stable)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption("Last Roof: Escape City")
clock = pygame.time.Clock()

from enemy import FlyingEye, Goblin, Mushroom, Skeleton, BigFlyingEye, DashingGoblin, TeleportingMushroom, EvilWizard, OldGuardian
from pathfinding import bfs
from player import Player
from weapon import WeaponManager
from all_graphics import ALL_GRAPHICS
from camera import Camera
from ui import load_ui_font, wrap_text, safe_load, safe_sheet_frame
from entities.pet import Pet, PETS_DATA

# --- Map props loaded HERE after display is initialized ---
from map_props import CHAPTER_TILES, DESERT_TILE, DESERT_TILE_ALT, DESERT_WALL, DESERT_GRASS, DESERT_GRASS_TUFT, DESERT_HUT, DESERT_BIG_GRASS, DESERT_BIG_ROCK, obstacle_prop_for_tile, draw_prop

# SoundManager tự động load assets từ thư mục Sounds/

# Load all graphics with absolute paths via BASE_DIR from ui.py
from ui import BASE_DIR as _ASSET_BASE
ALL_GRAPHICS_SURFACES = {}
for _gfx_path in ALL_GRAPHICS:
    try:
        _abs = os.path.join(_ASSET_BASE, _gfx_path) if not os.path.isabs(_gfx_path) else _gfx_path
        ALL_GRAPHICS_SURFACES[_gfx_path] = pygame.image.load(_abs).convert_alpha()
    except Exception as _e:
        print(f"[GRAPHICS LOAD ERROR] {_gfx_path}: {_e}")

from skill import SkillManager, Skill

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # already chdir'd above

INTERACT_RADIUS = 60
TILE_SIZE = 16
GRID_SIZE = 44


from shop import SHOP_CARD_SURFACES, get_random_shop_card, get_random_pet_card

# Sounds loaded via audio module (centralised, absolute paths)
# load_sounds() # Đã tự động load trong SoundManager


from map import TILE_SIZE, GRID_SIZE
TANK_BASE = safe_load("Sprites/Sprites_Building/Towers bases/Tower 06.png", (52, 52))
TANK_TURRET = safe_load("Sprites/Sprites_Building/RocketLauncher.png", (52, 52))
ROCKET_PICKUP = safe_load("Sprites/Sprites_Weapon/RPG-reisized.png", (34, 34))
SHOTGUN_PICKUP = safe_load("Sprites/Sprites_Weapon/Shotgun-4.png", (42, 24))
AK_PICKUP = safe_load("Sprites/Sprites_Weapon/Assaut-rifle-3-scoped.png", (44, 24))
SMG_PICKUP = safe_load("Sprites/Sprites_Weapon/SMG-4.png", (38, 24))
SNIPER_PICKUP = safe_load("Sprites/Sprites_Weapon/Sniper-rifle-2-scoped.png", (50, 24))
CARD_WEAPON_BASIC = safe_load("Shop_Cards/Card_Weapon_AssaultRifle.png", (72, 96))
CARD_WEAPON_SHOTGUN = safe_load("Shop_Cards/Card_Weapon_Shotgun.png", (72, 96))
CARD_WEAPON_ROCKET = safe_load("Shop_Cards/Card_Building_RocketLauncher.png", (72, 96))
CARD_WEAPON_PISTOL = safe_load("Shop_Cards/Card_Weapon_Pistol.png", (72, 96))
CARD_WEAPON_MINIGUN = safe_load("Shop_Cards/Card_Weapon_Minigun.png", (72, 96))
CARD_WEAPON_FLAMETHROWER = safe_load("Shop_Cards/Card_Weapon_FlameThrower.png", (72, 96))
CARD_WEAPON_GRENADE = safe_load("Shop_Cards/Card_Weapon_GrenadeLauncher.png", (72, 96))
CARD_WEAPON_POISON = safe_load("Shop_Cards/Card_Weapon_PoisonGun.png", (72, 96))
CARD_WEAPON_TAESAR = safe_load("Shop_Cards/Card_Weapon_Taesar_Gun.png", (72, 96))
CARD_BORDER = safe_load("Shop_Cards/Card_Border_1.png", (78, 102))
CARD_PET_BIRD = safe_load("Shop_Cards/Card_Pet_BlueBird.png", (58, 78))
CARD_PET_FOX = safe_load("Shop_Cards/Card_Pet_Fox.png", (58, 78))
CARD_PET_EAGLE = safe_load("Shop_Cards/Card_Pet_Eagle.png", (58, 78))
CARD_PET_GRAY_CAT = safe_load("Shop_Cards/Card_Pet_GrayCat.png", (58, 78))
CARD_PET_ORANGE_CAT = safe_load("Shop_Cards/Card_Pet_OrangeCat.png", (58, 78))
CARD_PET_RACOON = safe_load("Shop_Cards/Card_Pet_Racoon.png", (58, 78))
CARD_BUILD_MORTAR = safe_load("Shop_Cards/Card_Building_SuperMortar.png", (58, 78))
CARD_BUILD_CANNON = safe_load("Shop_Cards/Card_Building_SuperCannon.png", (58, 78))
PET_BIRD = safe_load("Sprites/Sprites_Pet/PET_BlueBird.png", (34, 34))
PET_FOX = safe_load("Sprites/Sprites_Pet/PET_Fox.png", (34, 34))
PET_RACOON = safe_load("Sprites/Sprites_Pet/PET_Racoon.png", (34, 34))
BUILD_CANNON = safe_load("Sprites/Sprites_Building/SuperCannon.png", (52, 52))
BUILD_MORTAR = safe_load("Sprites/Sprites_Building/SuperMortar.png", (52, 52))
BUILD_ROCKET = safe_load("Sprites/Sprites_Building/RocketLauncher.png", (52, 52))
PET_POWER = safe_load("Sprites/Sprites_Effect/Pet_Power.png", (32, 32))
PLAYER_TRAILER = safe_sheet_frame("Sprites/Sprites_Player/mega_scientist_walk.png", (0, 128, 64, 64), (180, 180))
GOBLIN_TRAILER = safe_sheet_frame("Sprites/Sprites_Enemy/Goblin/Run.png", (0, 0, 150, 150), (180, 180))
EYE_TRAILER = safe_sheet_frame("Sprites/Sprites_Enemy/Flying eye/Flight.png", (0, 0, 150, 150), (180, 180))
MUSHROOM_TRAILER = safe_sheet_frame("Sprites/Sprites_Enemy/Mushroom/Run.png", (0, 0, 150, 150), (220, 220))
ROCKET_LAUNCHER_TRAILER = safe_load("Sprites/Sprites_Weapon/RPG-reisized.png", (200, 90))
MORTAR_TRAILER = safe_load("Sprites/Sprites_Building/SuperMortar.png", (180, 180))
HELICOPTER = safe_load("Sprites/Sprites_Building/Helicopter.png", (150, 150))

WEAPON_DROP_POOL = [
    {
        "name": "AK-47",
        "fire_rate": 6.2,
        "reload_time": 1.0,
        "image_path": "Sprites/Sprites_Weapon/Assaut-rifle-3-scoped.png",
        "projectile_speed": 9,
        "damage": 48,
        "projectile_scale": (36, 36),
        "type": "rifle"
    },
    {
        "name": "SMG",
        "fire_rate": 9.0,
        "reload_time": 0.9,
        "image_path": "Sprites/Sprites_Weapon/SMG-4.png",
        "projectile_speed": 10,
        "damage": 34,
        "projectile_scale": (34, 34),
        "type": "smg"
    },
    {
        "name": "Sniper",
        "fire_rate": 1.2,
        "reload_time": 1.8,
        "image_path": "Sprites/Sprites_Weapon/Sniper-rifle-2-scoped.png",
        "projectile_speed": 12,
        "damage": 170,
        "projectile_scale": (42, 42),
        "type": "sniper"
    },
    {
        "name": "Katana",
        "fire_rate": 2.5,
        "reload_time": 0.0,
        "image_path": "Sprites/Sprites_Weapon/Katana.png",
        "projectile_speed": 0,
        "damage": 85,
        "projectile_image": "Sprites/Sprites_Effect/Bullets/KatanaSlash.png",
        "projectile_scale": (160, 160),
        "type": "melee"
    },
    {
        "name": "Plasma Gun",
        "fire_rate": 6.0,
        "reload_time": 1.2,
        "image_path": "Sprites/Sprites_Weapon/PlasmaGun.png",
        "projectile_speed": 15,
        "damage": 95,
        "projectile_scale": (48, 48),
        "type": "plasma"
    },
]

# Extend with big generated armory
for w in ARMORY:
    # Normalize shape for WeaponManager.unlock_weapon
    data = dict(w)
    if data.get("type") == "melee" or data.get("type_hint") == "melee":
        data["type"] = "melee"
    WEAPON_DROP_POOL.append(data)

ITEM_SURFACES = {
    "heal": safe_load("Sprites/Sprites_Weapon/Grenade-2.png", (24, 24)),
    "armor": safe_load("Sprites/Sprites_Effect/Pet_Power.png", (24, 24)),
    "ammo": safe_load("Sprites/Sprites_Weapon/AmoB2.png", (24, 24)),
    "weapon": safe_load("Sprites/Sprites_Weapon/Shotgun-4.png", (34, 24)),
    "rocket_weapon": safe_load("Sprites/Sprites_Weapon/RPG-reisized.png", (38, 38)),
    "material": safe_load("Sprites/Sprites_Effect/Pet_Power.png", (28, 28)), # Shadow fragments
    # Mission items (clear icons)
    "keycard": safe_load("Sprites/Sprites_Environment/items/keycard_24.png", (24, 24)),
    "power": safe_load("Sprites/Sprites_Environment/items/fuse_24.png", (24, 24)),
    "code": safe_load("Sprites/Sprites_Environment/items/codebook_24.png", (24, 24)),
    "antidote": safe_load("Sprites/Sprites_Environment/items/antidote_24.png", (24, 24)),
    "exit_key": safe_load("Sprites/Sprites_Environment/items/exit_key_24.png", (24, 24)),
    "gate": safe_load("Sprites/Sprites_Environment/items/gate_switch_24.png", (24, 24)),
    "signal": safe_load("Sprites/Sprites_Environment/items/beacon_24.png", (24, 24)),
    "flare": safe_load("Sprites/Sprites_Weapon/Grenade-1.png", (24, 24)),
    "money": safe_load("Sprites/Sprites_Environment/items/money_24.png", (24, 24)),
}

# Combo multiplier system
COMBO_TIERS = [(3, "DOUBLE KILL", 1.2), (5, "RAMPAGE!", 1.5), (10, "UNSTOPPABLE", 2.0)]


@dataclass
class ItemPickup:
    grid_pos: tuple[int, int]
    name: str
    description: str
    item_type: str
    amount: int = 0
    color: tuple[int, int, int] = GREEN
    collected: bool = False
    weapon_data: dict | None = None
    sprite_surface: pygame.Surface | None = None
    timer: int = 0  # 0 means infinite
    max_timer: int = 0

@dataclass
class ComboText:
    text: str
    x: float
    y: float
    life: int
    max_life: int
    color: tuple
    size: int


@dataclass
class Particle:
    x: float
    y: float
    dx: float
    dy: float
    life: int
    color: tuple
    size: int

@dataclass
class NPC:
    name: str
    grid_pos: tuple[int, int]
    lines: list[str]
    reward: str | None = None
    color: tuple[int, int, int] = CYAN
    once: bool = True
    interacted: bool = False
    portrait_color: tuple[int, int, int] = CYAN
    sprite_path: str = None
    quest: str | None = None


@dataclass
class Chapter:
    id: str
    title: str
    subtitle: str
    intro_lines: list[str]
    objective_titles: list[str]
    exit_pos: tuple[int, int] | None
    start_pos: tuple[int, int]
    blocked_tiles: set[tuple[int, int]]
    decor_tiles: dict[tuple[int, int], str]
    items: list[ItemPickup]
    npcs: list[NPC]
    enemy_plan: list[tuple[type, tuple[int, int], str]]
    chapter_color: tuple[int, int, int]
    radio_message: str
    quest_line: str = ""
    holdout_seconds: int = 0
    chapter_type: str = "explore"
    spawn_pool: list[type] = field(default_factory=list)
    max_alive_enemies: int = 8
    spawn_interval_ms: int = 5000


class StoryEnemy:
    def __init__(self, enemy, archetype, grid_pos):
        self.enemy = enemy
        self.archetype = archetype
        self.grid_pos = grid_pos
        self.dead_registered = False
        self._last_health = getattr(enemy, "health", 0)
        self._last_hit_sfx_at = 0

    @property
    def is_dead(self):
        return self.enemy.is_dead

    @property
    def pos(self):
        return (self.enemy.x, self.enemy.y)

    def tile(self):
        return (int(self.enemy.x // TILE_SIZE), int(self.enemy.y // TILE_SIZE))


class EscortTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target = (x, y)
        self.speed = 0.6
        self.active = False
        self.angle = 0

    def set_target(self, x, y):
        self.target = (x, y)
        self.active = True

    def update(self):
        if not self.active:
            return
        dx = self.target[0] - self.x
        dy = self.target[1] - self.y
        distance = math.hypot(dx, dy)
        if distance < 50:
            self.active = False
            return
        self.x += dx / distance * self.speed
        self.y += dy / distance * self.speed
        self.angle = math.degrees(math.atan2(dy, dx))

    def draw(self, surface):
        base_rect = TANK_BASE.get_rect(center=(self.x, self.y))
        surface.blit(TANK_BASE, base_rect)
        turret = pygame.transform.rotate(TANK_TURRET, -self.angle)
        turret_rect = turret.get_rect(center=(self.x, self.y))
        surface.blit(turret, turret_rect)


class MissionTracker:
    def __init__(self, chapter):
        self.chapter = chapter
        self.data = {
            "stage": 0,
            "weapon_collected": False,
            "medkit_collected": False,
            "keycard_collected": False,
            "power_restored": False,
            "supply_cache": False,
            "specials_cleared": False,
            "gate_opened": False,
            "signal_started": False,
            "holdout_complete": False,
            "boss_down": False,
            "zombies_killed": 0,
            "special_kills": 0,
            "npc_saved": 0,
        }

    def objectives(self):
        cid = self.chapter.id
        d = self.data
        s = int(d.get("stage", 0) or 0)
        if cid == "roof":
            steps = [
                ("Nhặt vũ khí cơ bản", d["weapon_collected"]),
                ("Hạ 1 zombie", d["zombies_killed"] >= 1),
                ("Tới cổng để xuống tầng 3", d.get("gate_opened", False)),
            ]
            return [steps[min(s, len(steps) - 1)]]
        if cid == "office":
            steps = [
                ("Hạ đủ 10 zombie (0/10)", d["zombies_killed"] >= 10),
                ("Nhặt Keycard", d["keycard_collected"]),
                ("Nhặt cầu chì (Fuse)", d.get("fuse_collected", False)),
                ("Bật điện ở hộp điện", d["power_restored"]),
                ("Tới cổng để xuống tầng 2", d["gate_opened"]),
            ]
            # patch dynamic text for step 0
            if s == 0:
                k = min(int(d.get("zombies_killed", 0) or 0), 10)
                return [(f"Hạ đủ 10 zombie ({k}/10)", d["zombies_killed"] >= 10)]
            return [steps[min(s, len(steps) - 1)]]
        if cid == "medical":
            steps = [
                ("Nhặt vật tư y tế", d["supply_cache"]),
                ("Hạ 3 zombie đặc biệt", d["special_kills"] >= 3),
                ("Nhặt thiết bị mở cổng (Control Fuse)", d.get("control_fuse_collected", False)),
                ("Kích hoạt hộp điện để mở cổng", d["gate_opened"]),
            ]
            return [steps[min(s, len(steps) - 1)]]
        if cid == "basement":
            steps = [
                ("Nhặt sổ tay mã cửa (4821)", d.get("basement_code", False)),
                ("Hạ 2 zombie đặc biệt", d["special_kills"] >= 2),
                ("Bật máy phát (hộp điện)", d["power_restored"]),
                ("Tới cổng để vào phòng thí nghiệm", d["gate_opened"]),
            ]
            return [steps[min(s, len(steps) - 1)]]
        if cid == "lab":
            steps = [
                ("Hạ 1 zombie đặc biệt để rơi mẫu", d["special_kills"] >= 1),
                ("Nhặt mẫu kháng thể", d.get("antidote_collected", False)),
                ("Nhặt thẻ từ an ninh", d["keycard_collected"]),
                ("Mở cửa an ninh (console)", d["gate_opened"]),
            ]
            return [steps[min(s, len(steps) - 1)]]
        if cid == "escape":
            steps = [
                ("Hạ boss Old Guardian", d["boss_down"]),
                ("Chờ trực thăng đến", d.get("helicopter_arrived", False)),
                ("Tới điểm trực thăng để thoát", d.get("extracted", False)),
            ]
            return [steps[min(s, len(steps) - 1)]]
        return [
            # ground
            ("Mở cổng ra sân", d["gate_opened"]),
        ]

    def complete(self):
        cid = self.chapter.id
        d = self.data
        s = int(d.get("stage", 0) or 0)
        if cid == "roof":
            # Chapter 1 should never get stuck: as soon as you pick weapon + kill 1, gate can open.
            return bool(d.get("weapon_collected", False)) and int(d.get("zombies_killed", 0) or 0) >= 1
        if cid == "office":
            return s >= 4 and bool(d.get("gate_opened", False))
        if cid == "medical":
            return s >= 3 and bool(d.get("gate_opened", False))
        if cid == "basement":
            return s >= 3 and bool(d.get("gate_opened", False))
        if cid == "lab":
            return s >= 3 and bool(d.get("gate_opened", False))
        if cid == "escape":
            return bool(d.get("extracted", False))
        # ground
        return bool(d.get("holdout_complete", False))


from camera import Camera
from npc_data import get_random_npcs_for_chunk, reset_spawned_chunks

class Game:
    def __init__(self):
        self.font = load_ui_font(22)
        self.font_big = load_ui_font(40, bold=True)
        self.font_title = load_ui_font(64, bold=True)
        self.font_small = load_ui_font(18)
        
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, SIDEBAR_WIDTH)
        self.player = Player(400, 400)
        self.weapon_manager = WeaponManager()
        def find_nearest_enemy(self, radius=300):
            px, py = self.player.x, self.player.y
            nearest = None
            min_dist = radius

            for e in self.story_enemies:
                ex, ey = e.pos
                dist = math.hypot(ex - px, ey - py)
                if dist < min_dist:
                    min_dist = dist
                    nearest = e

            return nearest
        # Wire weapon SFX events (shot/reload)
        def _weapon_event(evt, weapon):
            wname = (getattr(weapon, "name", "") or "").lower()
            is_melee = bool(getattr(weapon, "melee", False))

            # classify weapon
            if is_melee or "katana" in wname or "knife" in wname:
                wtype = "melee"
            elif "shotgun" in wname:
                wtype = "shotgun"
            elif "pistol" in wname:
                wtype = "sung_luc"
            elif "sniper" in wname:
                wtype = "tia"
            elif "smg" in wname:
                wtype = "tieu_lien"
            elif "rocket" in wname or "rpg" in wname or "b40" in wname:
                wtype = "b40"
            else:
                wtype = "sung_truong"

            if evt == "shot":
                sound_manager.play(f"ban_{wtype}" if wtype != "melee" else "chem")
            elif evt in {"reload_start", "reload_complete"}:
                sound_manager.play("thay_dan")
        self.weapon_manager.on_event = _weapon_event
        self.story_flags = set()
        self.exit_path = []
        self.last_spawn_at = 0
        self.shot_counter = 0
        self.frenzy_window_until = 0
        self.combo_counter = 0
        self.combo_texts = []
        self.frenzy_active = False
        self.frenzy_timer = 0
        self.kill_count = 0
        self.saved_npcs = 0
        self.money = 0
        # Finite wave per chapter (no infinite spawning)
        self.enemy_target_per_chapter = [10, 20, 30, 40, 50, 60, 70]
        self.enemies_remaining_to_spawn = 0
        self.enemies_initial_count = 0
        # Dialogue UI (Genshin-like)
        self.dialog_started_at = 0
        self.dialog_page_index = 0
        self.dialog_chars_shown = 0
        self.dialog_speed_cps = 70  # chars per second
        self.end_reason = ""
        self._last_player_hp = self.player.health
        self._last_player_hit_sfx_at = 0
        
        # --- Kỹ năng ---
        self.skill_manager = SkillManager()
        # Sử dụng hệ thống cắt sheet mới để lấy hiệu ứng cụ thể từ các tấm ảnh tổng hợp
        self.skill_manager.add_skill(Skill(
            "Fireball", 1500, "Sprites/Sprites_Effect/Bullets/Fireball.png",
            effect_image_paths="Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif",
            rows=4, cols=4, effect_scale=(64, 64), damage=50
        ))
        self.skill_manager.add_skill(Skill(
            "Frost Nova", 3000, "Sprites/Sprites_Effect/Bullets/FrostNova.png",
            effect_image_paths="Sprites/Sprites_Effect/Bullets/Introl Blue Effect Bullet Impact Explosion 32x32.gif",
            rows=4, cols=4, effect_scale=(128, 128), damage=80
        ))
        self.skill_manager.add_skill(Skill(
            "Poison Cloud", 2500, "Sprites/Sprites_Effect/Bullets/25.png",
            effect_image_paths="Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif",
            rows=4, cols=4, effect_scale=(96, 96), damage=40
        ))
        
        # --- Pets & Loadout ---
        self.all_pets = {}
        for pdata in PETS_DATA:
            pet = Pet(pdata["name"], pdata["path"], pdata["attr"], pdata["desc"])
            self.all_pets[pdata["id"]] = pet
        
        self.unlocked_pets = ["blue_bird"] # Only start with Blue Bird
        self.current_pet_id = "blue_bird"
        self.current_pet_instance = self.all_pets["blue_bird"]
        self.apply_pet_effects()
        
        # --- Infinite Map ---
        self.chunks = {} # (cx, cy) -> list of objects
        self.visited_chunks = set()
        
        self.mouse_down = False
        self.state = "menu"
        self.show_help = False
        self.show_shop = False
        self.show_map = False
        self.map_assets = [None] + self.discover_map_backgrounds()
        self.selected_map_index = 0
        self.selected_map_name = "Default Tilemap"
        self.map_background_path = None
        self.map_background_surface = None
        self.map_world_surface = None
        self.map_surface_cache = {}
        self.set_map_background_by_index(0)
        self.exit_path = []
        self.exit_path_timer = 0
        self.hint_modes = ["BFS", "DFS", "SAFE", "A*"]
        self.hint_mode_index = 0
        
        self.popup = ""
        self.popup_timer = 0
        self.dialog_npc = None
        self.dialog_speaker = ""
        self.dialog_color = CYAN
        self.dialog_lines = []
        self.dialog_queue = []
        
        self.kill_count = 0
        self.saved_npcs = 0
        self.next_chapter_ready = False
        self.exit_unlocked = False
        self.yard_spawned = False
        self.yard_enemy_plan = []
        self.yard_gate_tile = (26, 22)
        self.chapter_index = 0
        self.chapters = self.build_chapters()
        self.chapter = None
        self.mission = None
        self.story_enemies = []
        self.current_blocked = set()
        self.stats_start = pygame.time.get_ticks()
        
        # World Bounds (Fixed map)
        self.world_w = GRID_SIZE * TILE_SIZE
        self.world_h = GRID_SIZE * TILE_SIZE
        
        # Particles
        self.particles = []
        
        # UI & Animation
        self.shop_anim_timer = 0
        self.trailer_started_at = 0
        self.chapter_card_timer = 0
        self.last_objective_text = ""
        self.objective_flash_until = 0
        self.show_shop = False
        
        # Phát nhạc chờ sảnh khi khởi động
        sound_manager.play_music("nhac_cho_sanh")
        self.set_chapter(0)

    def discover_map_backgrounds(self):
        map_dir = os.path.join(BASE_DIR, "Sprites", "Sprites_Environment", "maps")
        patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp")
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(map_dir, pattern)))
        return sorted(set(files), key=lambda p: os.path.basename(p).lower())

    def auto_crop_black_border(self, image: pygame.Surface) -> pygame.Surface:
        """Crop uniform black borders from map images while keeping gameplay stable."""
        w, h = image.get_size()
        if w < 8 or h < 8:
            return image

        # Downscale for fast border detection on very large maps.
        max_scan_edge = 512
        scale = min(1.0, float(max_scan_edge) / float(max(w, h)))
        scan_w = max(1, int(w * scale))
        scan_h = max(1, int(h * scale))
        scan = pygame.transform.smoothscale(image, (scan_w, scan_h)) if scale < 1.0 else image

        threshold = 10
        min_x, min_y = scan_w, scan_h
        max_x, max_y = -1, -1

        for y in range(scan_h):
            for x in range(scan_w):
                px = scan.get_at((x, y))
                if len(px) >= 4 and px[3] <= threshold:
                    continue
                if px[0] > threshold or px[1] > threshold or px[2] > threshold:
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y

        # If nothing detectable, keep original for safety.
        if max_x < 0 or max_y < 0:
            return image

        # Map scan bbox back to original image coordinates.
        x1 = int(min_x * w / scan_w)
        y1 = int(min_y * h / scan_h)
        x2 = int((max_x + 1) * w / scan_w)
        y2 = int((max_y + 1) * h / scan_h)

        # Small padding avoids clipping map edges.
        pad = max(1, int(min(w, h) * 0.005))
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        if x1 == 0 and y1 == 0 and x2 == w and y2 == h:
            return image
        if x2 - x1 < 32 or y2 - y1 < 32:
            return image

        return image.subsurface(pygame.Rect(x1, y1, x2 - x1, y2 - y1)).copy()

    def set_map_background_by_index(self, index):
        if not self.map_assets:
            self.selected_map_index = 0
            self.selected_map_name = "Default Tilemap"
            self.map_background_path = None
            self.map_background_surface = None
            self.map_world_surface = None
            return

        self.selected_map_index = index % len(self.map_assets)
        selected = self.map_assets[self.selected_map_index]
        if selected is None:
            self.selected_map_name = "Default Tilemap"
            self.map_background_path = None
            self.map_background_surface = None
            self.map_world_surface = None
            return

        self.map_background_path = selected
        raw_name = os.path.splitext(os.path.basename(selected))[0]
        self.selected_map_name = raw_name.replace("_", " ")
        if selected in self.map_surface_cache:
            self.map_world_surface, self.map_background_surface = self.map_surface_cache[selected]
            return
        try:
            image = pygame.image.load(selected).convert()
            cropped = self.auto_crop_black_border(image)
            self.map_world_surface = pygame.transform.smoothscale(cropped, (GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE))
            self.map_background_surface = pygame.transform.smoothscale(cropped, (MAP_WIDTH, MAP_HEIGHT))
            self.map_surface_cache[selected] = (self.map_world_surface, self.map_background_surface)
        except Exception as exc:
            print(f"[MAP LOAD ERROR] {selected}: {exc}")
            self.map_background_surface = None
            self.map_world_surface = None

    def build_chapters(self):
        def ring_walls():
            blocked = set()
            for x in range(GRID_SIZE):
                blocked.add((x, 0))
                blocked.add((x, GRID_SIZE - 1))
            for y in range(GRID_SIZE):
                blocked.add((0, y))
                blocked.add((GRID_SIZE - 1, y))
            return blocked

        def add_rect_walls(blocked: set[tuple[int, int]], x1: int, y1: int, x2: int, y2: int, doors: list[tuple[int, int]] | None = None):
            """Add rectangle perimeter walls (inclusive)."""
            for x in range(x1, x2 + 1):
                blocked.add((x, y1))
                blocked.add((x, y2))
            for y in range(y1, y2 + 1):
                blocked.add((x1, y))
                blocked.add((x2, y))
            if doors:
                for d in doors:
                    blocked.discard(d)

        def corridor(blocked: set[tuple[int, int]], x1: int, y1: int, x2: int, y2: int, width: int = 3):
            """Carve a corridor by removing walls in a band (useful after placing big rectangles)."""
            if x1 == x2:
                x = x1
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    for dx in range(-(width // 2), width // 2 + 1):
                        blocked.discard((x + dx, y))
            elif y1 == y2:
                y = y1
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    for dy in range(-(width // 2), width // 2 + 1):
                        blocked.discard((x, y + dy))

        def add_block_rect(blocked: set[tuple[int, int]], x1: int, y1: int, x2: int, y2: int):
            """Fill a rectangle area as blocked obstacles."""
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    blocked.add((x, y))

        def carve(blocked: set[tuple[int, int]], x1: int, y1: int, x2: int, y2: int):
            """Clear a rectangle area (walkable)."""
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    blocked.discard((x, y))

        roof_blocked = ring_walls()
        # Rooftop: Clear, open space with centralized obstacle islands
        add_block_rect(roof_blocked, 12, 10, 16, 14)  # Vent cluster
        add_block_rect(roof_blocked, 24, 6, 28, 10)   # AC cluster
        add_block_rect(roof_blocked, 30, 26, 34, 30)  # Water tank zone
        add_block_rect(roof_blocked, 14, 28, 18, 32)  # Debris zone
        
        # Primary 3-tile wide walkways ensuring path to stairwell exit
        carve(roof_blocked, 3, 3, 41, 41)             # Mass clear internal area
        # Re-add obstacles more selectively to keep paths very wide
        add_block_rect(roof_blocked, 12, 12, 14, 14)  
        add_block_rect(roof_blocked, 24, 8, 26, 10)
        add_block_rect(roof_blocked, 32, 28, 34, 30)
        
        # Explicitly carve the exit and start paths (3x3 min)
        carve(roof_blocked, 3, 4, 6, 7)              # Start area
        carve(roof_blocked, 37, 33, 40, 36)           # Exit area
        roof_decor = {
            # Rooftop context props
            (6, 6): "roof_stairwell",
            (10, 8): "roof_vent",
            (12, 8): "roof_vent",
            (20, 6): "roof_ac",
            (30, 8): "roof_sat_dish",
            (34, 30): "roof_water_tank",
            # existing decor
            (5, 5): "grass",
            (32, 6): "hut",
            (25, 33): "rock",
        }
        roof_items = [
            ItemPickup((6, 7), "Shotgun", "Một khẩu shotgun còn hoạt động.", "weapon", color=ORANGE),
            ItemPickup((10, 31), "Bandage", "Băng gạc từ túi cứu hộ sân thượng.", "heal", amount=25),
        ]
        roof_npcs = [
            NPC("Phi công", (38, 5), ["Tôi chỉ liên lạc được qua bộ đàm.", "Xuống các tầng dưới, mở cổng sân và gọi tín hiệu."], reward="radio", portrait_color=YELLOW, sprite_path="Sprites/Sprites_NPC/pilot.png",
                quest="Nhặt súng + hạ 1 zombie -> cổng xuống tầng sẽ mở"),
        ]
        roof_enemies = [
            (Goblin, (18, 7), "basic"),
            (FlyingEye, (31, 18), "fast"),
            (Goblin, (35, 31), "basic"),
            (Goblin, (12, 20), "basic"),
            (FlyingEye, (24, 34), "fast"),
        ]

        office_blocked = ring_walls()
        # Office: readable "plus" corridors + furniture islands (no maze walls)
        carve(office_blocked, 2, 2, GRID_SIZE - 3, GRID_SIZE - 3)
        office_blocked |= ring_walls()
        # Main cross corridors
        carve(office_blocked, 4, 20, 39, 26)   # horizontal corridor (wide)
        carve(office_blocked, 18, 4, 26, 39)   # vertical corridor (wide)
        # Furniture islands (blocked)
        add_block_rect(office_blocked, 6, 6, 14, 12)
        add_block_rect(office_blocked, 28, 6, 38, 12)
        add_block_rect(office_blocked, 6, 30, 14, 36)
        add_block_rect(office_blocked, 28, 30, 38, 36)
        add_block_rect(office_blocked, 10, 14, 14, 18)
        add_block_rect(office_blocked, 30, 14, 34, 18)
        # Ensure clear approach to exits/objectives
        carve(office_blocked, 3, 32, 10, 38)  # start lane
        carve(office_blocked, 34, 32, 41, 38) # exit lane
        office_decor = {
            # Office context props: desks, tables, cabinets, glass partitions
            (8, 7): "office_desk",
            (14, 8): "office_desk",
            (28, 8): "office_table",
            (34, 12): "office_cabinet",
            (24, 26): "office_glass",
            (30, 26): "office_glass",
        }
        office_items = [
            ItemPickup((35, 28), "Fuse", "Cầu chì phụ cho điện hành lang.", "power", color=YELLOW),
            ItemPickup((14, 20), "Katana", "Thanh kiếm Nhật gia: sắc lẹm và tốc độ cao.", "weapon", weapon_data={
                "name": "Katana", "fire_rate": 2.5, "reload_time": 0.0,
                "image_path": "Sprites/Sprites_Weapon/Katana.png",
                "projectile_speed": 0, "damage": 110, "projectile_scale": (96, 96), "type": "melee",
                "projectile_image": [
                    {"atlas": "Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif", "tile": (32, 32)},
                    {"atlas": "Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif", "tile": (32, 32)},
                ],
            }),
            ItemPickup((24, 5), "Ammo", "Đạn dự trữ từ phòng nhân sự.", "ammo", amount=18, color=WHITE),
        ]
        office_npcs = [
            NPC("Bảo vệ Nam", (21, 17), ["Tôi giữ được phòng camera nhưng cửa đang kẹt.", "Hạ zombie đặc biệt để lấy thẻ từ, rồi khôi phục điện để mở lối xuống."], reward="map", portrait_color=BLUE, sprite_path="Sprites/Sprites_NPC/guard.png",
                quest="Checkpoint: Hạ đủ 10 zombie -> rơi Keycard. Sau đó tìm cầu chì và bật hộp điện."),
        ]
        office_enemies = [
            (Goblin, (9, 17), "basic"),
            (EvilWizard, (24, 16), "ranged"),
            (DashingGoblin, (33, 6), "fast"),
            (EvilWizard, (35, 31), "ranged"),
            (Skeleton, (9, 29), "special"),
            (Goblin, (26, 31), "basic"),
            (DashingGoblin, (19, 6), "fast"),
        ]

        med_blocked = ring_walls()
        # Medical: long corridor + wards on sides, fewer tight corners
        carve(med_blocked, 2, 2, GRID_SIZE - 3, GRID_SIZE - 3)
        med_blocked |= ring_walls()
        # Main medical hallway
        carve(med_blocked, 4, 17, 42, 25)
        # Ward islands
        add_block_rect(med_blocked, 6, 6, 16, 14)
        add_block_rect(med_blocked, 22, 6, 38, 14)
        add_block_rect(med_blocked, 6, 28, 16, 38)
        add_block_rect(med_blocked, 22, 28, 38, 38)
        # service core
        add_block_rect(med_blocked, 18, 8, 20, 16)
        add_block_rect(med_blocked, 18, 28, 20, 36)
        # đường đi từ đầu
        carve(med_blocked, 4, 30, 12, 42)
        # 🔥 EXIT: mở rộng to hẳn để không kẹt
        carve(med_blocked, 30, 28, 43, 43)
        # 🔥 FIX CUỐI: đảm bảo không bị block lại
        med_blocked.discard((37, 33))
        med_blocked.discard((36, 33))
        med_blocked.discard((38, 33))
        med_blocked.discard((37, 32))
        med_blocked.discard((37, 34))
        med_decor = {
            # Medical context props
            (8, 10): "medical_bed",
            (12, 10): "medical_bed",
            (28, 8): "medical_cabinet",
            (30, 8): "medical_cabinet",
            (18, 26): "medical_trolley",
        }
        med_items = [
            ItemPickup((6, 6), "Medkit", "Một hộp cứu thương lớn trong phòng cấp cứu.", "heal", amount=50),
            ItemPickup((19, 20), "Armor Vest", "Áo giáp nhẹ giúp giảm sát thương.", "armor", amount=25, color=CYAN),
            ItemPickup((10, 26), "Rocket Launcher", "Vũ khí nổ mạnh để quét đám đông zombie.", "rocket_weapon", color=ORANGE),
            ItemPickup((37, 33), "Control Fuse", "Thiết bị mở cổng tầng 1.", "exit", color=YELLOW),
            ItemPickup((27, 8), "Rifle Ammo", "Đạn hiếm cho súng trường.", "ammo", amount=28, color=WHITE),
        ]
        med_npcs = [
            NPC("Y tá Linh", (18, 7), ["Tôi vẫn còn giữ được kho thuốc.", "Hạ 3 zombie đặc biệt và mở lối xuống tầng 1, tôi sẽ giúp cậu."], reward="medkit", portrait_color=GREEN, sprite_path="Sprites/Sprites_NPC/medic.png",
                quest="Checkpoint: Hạ 3 zombie đặc biệt -> mở đường xuống tầng 1."),
        ]
        med_enemies = [
            (Mushroom, (9, 21), "tank"),
            (TeleportingMushroom, (28, 18), "special"),
            (Skeleton, (36, 11), "special"),
            (Goblin, (21, 31), "basic"),
            (FlyingEye, (6, 33), "fast"),
            (Mushroom, (17, 16), "tank"),
            (EvilWizard, (32, 28), "ranged"),
            (Goblin, (30, 7), "basic"),
        ]

        ground_blocked = ring_walls()
        # Ground: left = lobby/inside, right-bottom = yard; wide lanes
        carve(ground_blocked, 2, 2, GRID_SIZE - 3, GRID_SIZE - 3)
        ground_blocked |= ring_walls()
        # Lobby furniture blocks (inside)
        add_block_rect(ground_blocked, 6, 8, 16, 10)
        add_block_rect(ground_blocked, 6, 14, 16, 16)
        add_block_rect(ground_blocked, 18, 8, 22, 16)
        carve(ground_blocked, 4, 4, 24, 20)
        # Yard obstacles (cars/crates)
        add_block_rect(ground_blocked, 30, 28, 36, 30)
        add_block_rect(ground_blocked, 28, 34, 34, 36)
        carve(ground_blocked, 24, 20, 41, 41)
        # Gate lane from inside to yard
        carve(ground_blocked, 22, 20, 30, 26)
        ground_items = [
            ItemPickup((7, 7), "Gate Switch", "Công tắc mở cổng sân.", "gate", color=ORANGE),
            ItemPickup((34, 29), "Signal Beacon", "Thiết bị phát tín hiệu cho trực thăng.", "signal", color=YELLOW),
            ItemPickup((38, 36), "Rescue Flare", "Phao sang dung de xac nhan vi tri ha canh.", "flare", color=RED),
        ]
        ground_npcs = [
            NPC("Kỹ thuật viên Huy", (17, 18), ["Tôi giữ được bộ phát ở sân.", "Mở cổng chính, ra sân và bật beacon. Quái ngoài sân chỉ phát hiện cậu sau khi cổng mở."], reward="shortcut", portrait_color=ORANGE, sprite_path="Sprites/Sprites_NPC/engineer.png",
                quest="Checkpoint: Mở cổng chính -> quái ngoài sân xuất hiện. Bật beacon -> trụ vững."),
        ]
        ground_enemies = [
            (Goblin, (18, 6), "basic"),
            (EvilWizard, (35, 9), "ranged"),
            (Mushroom, (28, 18), "tank"),
            (Skeleton, (6, 28), "special"),
            (EvilWizard, (37, 24), "ranged"),
            (BigFlyingEye, (33, 35), {"type": "boss", "health": 100}),
            (Goblin, (14, 27), "basic"),
            (DashingGoblin, (30, 31), "fast"),
        ]

        basement_blocked = ring_walls()
        # Outer concrete perimeter
        add_rect_walls(basement_blocked, 3, 3, 41, 41, doors=[(4, 35), (41, 35)])  # Slightly larger perimeter
        
        # 1. Main 3-tile wide horizontal corridor (Spawn to Exit)
        carve(basement_blocked, 4, 34, 41, 36)
        
        # 2. Large Central T-Junction (Vertical Hallway)
        carve(basement_blocked, 19, 4, 23, 35)
        
        # 3. Generator Room (Top Right) - 36x8 Item is here
        carve(basement_blocked, 28, 6, 39, 16)
        corridor(basement_blocked, 33, 16, 33, 35, width=3) # Connector to main hall
        
        # 4. Storage Wing (Top Left) - 12x10 Item is here
        carve(basement_blocked, 5, 6, 17, 18)
        corridor(basement_blocked, 11, 18, 11, 35, width=3) # Connector to main hall
        
        # 5. Engineering Niche (NPC Room) - 10x26 NPC is here
        carve(basement_blocked, 5, 23, 15, 30)
        corridor(basement_blocked, 11, 30, 11, 35, width=3) # Connector to main hall

        # Ensure spawn point and exit are completely clear
        carve(basement_blocked, 3, 33, 6, 37)
        carve(basement_blocked, 39, 33, 42, 37)
        basement_decor = {
            (36, 8): "basement_panel",
            (34, 12): "basement_generator",
            (12, 30): "basement_crates",
            (30, 18): "basement_pipes",
        }

        lab_blocked = ring_walls()
        # 1. Outer Perimeter
        add_rect_walls(lab_blocked, 2, 2, 42, 42, doors=[(3, 6), (39, 35)])
        
        # 2. Main U-Shaped Hallway (Expanded to 3-5 tiles width)
        carve(lab_blocked, 3, 3, 7, 39)           # Left vertical corridor (contains spawn)
        carve(lab_blocked, 3, 34, 38, 38)        # Bottom horizontal corridor
        carve(lab_blocked, 34, 3, 38, 38)        # Right vertical corridor (contains exit)
        
        # 3. Dedicated Lab Wings (Shifted inward to avoid narrow gaps)
        # Cold Storage (Top Center)
        add_rect_walls(lab_blocked, 10, 5, 30, 15, doors=[(20, 15), (20, 5)])
        # Research Wing (Bottom Left)
        add_rect_walls(lab_blocked, 10, 20, 18, 32, doors=[(18, 26), (14, 20)])
        # Security/Control (Bottom Right)
        add_rect_walls(lab_blocked, 22, 20, 31, 32, doors=[(22, 26), (26, 20)])

        # 4. Connecting Corridors
        corridor(lab_blocked, 7, 26, 10, 26, width=3)   # To Research Wing
        corridor(lab_blocked, 30, 26, 34, 26, width=3)  # To Security
        corridor(lab_blocked, 20, 15, 20, 20, width=5)  # Center Plaza

        # Ensure Spawn (3, 6) and Exit (39, 35) are fully cleared
        carve(lab_blocked, 2, 4, 6, 8)
        carve(lab_blocked, 38, 33, 40, 37)

        lab_decor = {
            (25, 8): "lab_freezer",
            (15, 8): "lab_freezer",
            (12, 26): "lab_bench",
            (28, 26): "lab_console",
            (20, 25): "lab_tubes",
        }

        return [
            Chapter(
                "roof",
                "Chương 1: Tầng thượng",
                "Tỉnh dậy giữa tận thế",
                ["Một vụ nổ rung chuyển tòa nhà.", "Bạn tỉnh dậy trên tầng thượng, bộ đàm chỉ còn tiếng nhiễu.", "Một trực thăng cứu hộ đang dò tín hiệu từ dưới sân."],
                ["Nhặt súng", "Lấy băng gạc", "Hạ zombie đầu tiên", "Mở lối xuống tầng 3"],
                (38, 34),
                (4, 5),
                roof_blocked,
                roof_decor,
                roof_items,
                roof_npcs,
                roof_enemies,
                ORANGE,
                "Phi công: Nếu còn nghe thấy tôi, hãy xuống các tầng dưới và mở cổng sân.",
                quest_line="Thoát khỏi sân thượng: nhặt súng, hạ 1 zombie, mở cổng xuống tầng 3.",
                spawn_pool=[],
                max_alive_enemies=5,
                spawn_interval_ms=999999,
            ),
            Chapter(
                "office",
                "Chương 2: Tầng 3",
                "Khu văn phòng cũ",
                ["Điện hành lang chập chờn, văn phòng biến thành mê cung.", "Zombie bắt đầu di chuyển nhanh hơn trong không gian hẹp."],
                ["Lấy thẻ từ", "Khôi phục điện", "Nói chuyện với bảo vệ", "Tới thang xuống tầng 2"],
                (37, 35),
                (3, 34),
                office_blocked,
                office_decor,
                office_items,
                office_npcs,
                office_enemies,
                BLUE,
                "Bảo vệ Nam: Tôi thấy cầu thang kỹ thuật ở góc đông nam. Nhưng phải có điện.",
                quest_line="Tầng 3: hạ đủ 10 zombie lấy thẻ từ, khôi phục điện, mở lối xuống tầng 2.",
                spawn_pool=[Goblin, DashingGoblin, FlyingEye],
                max_alive_enemies=11,
                spawn_interval_ms=3200,
            ),
            Chapter(
                "medical",
                "Chương 3: Tầng 2",
                "Khu y tế và kho chứa",
                ["Mùi hóa chất và máu trộn lẫn trong hành lang.", "Đây là nơi còn nhiều tiếp tế nhất, cũng là nơi nguy hiểm nhất."],
                ["Lấy kho thuốc", "Diệt 3 zombie đặc biệt", "Giúp y tá", "Mở đường xuống tầng 1"],
                (39, 35),
                (4, 34),
                med_blocked,
                med_decor,
                med_items,
                med_npcs,
                med_enemies,
                GREEN,
                "Y tá Linh: Cổng tầng 1 chỉ mở nếu cấp điện đúng tuyến kỹ thuật.",
                quest_line="Tầng 2: thu thập vật tư, hạ 3 zombie đặc biệt, mở đường xuống tầng 1.",
                spawn_pool=[Goblin, Mushroom, TeleportingMushroom, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=3000,
            ),
            # --------- NEW CHAPTER: Basement ----------
            Chapter(
                "basement",
                "Chương 4: Tầng hầm",
                "Máy phát dự phòng và cửa sắt",
                [
                    "Không khí ẩm và mùi dầu máy xộc thẳng vào mũi.",
                    "Tiếng kim loại kéo lên lạnh sống lưng — bên dưới có thứ gì đó đang di chuyển.",
                ],
                ["Tìm mã cửa", "Hạ zombie đặc biệt", "Khởi động máy phát", "Mở cửa đến phòng thí nghiệm"],
                (40, 35),
                (4, 35),
                basement_blocked,
                basement_decor,
                [
                    ItemPickup((8, 34), "Sổ tay kỹ thuật", "Trong sổ có mã cửa phòng máy: 4821.", "code", color=WHITE),
                    ItemPickup((36, 8), "Đạn dự trữ", "Hộp đạn còn mới trong tủ kỹ thuật.", "ammo", amount=24, color=WHITE),
                    ItemPickup((12, 10), "Áo giáp", "Áo giáp cũ nhưng vẫn dùng được.", "armor", amount=20, color=CYAN),
                ],
                [
                    NPC("Thợ máy Dũng", (10, 26), ["Máy phát ở phòng máy bị khóa mã.", "Tìm sổ tay kỹ thuật, bật điện lên thì cửa sắt sẽ mở."], reward="shortcut", portrait_color=ORANGE, sprite_path="Sprites/Sprites_NPC/engineer.png"),
                ],
                [
                    (Skeleton, (22, 30), "special"),
                    (TeleportingMushroom, (30, 12), "special"),
                    (Mushroom, (16, 16), "tank"),
                    (EvilWizard, (36, 30), "ranged"),
                ],
                (160, 160, 200),
                "Radio: Tầng hầm rất nguy hiểm. Bật được điện là sẽ mở được cửa sắt dẫn đến phòng thí nghiệm.",
                spawn_pool=[Goblin, Skeleton, TeleportingMushroom],
                max_alive_enemies=13,
                spawn_interval_ms=2600,
            ),
            # --------- NEW CHAPTER: Lab ----------
            Chapter(
                "lab",
                "Chương 5: Phòng thí nghiệm",
                "Nguồn gốc đại dịch",
                [
                    "Ánh đèn nhấp nhoáng trên các tủ lạnh mẫu.",
                    "Có thể ở đây có thứ gì đó giúp bạn sống sót lâu hơn.",
                ],
                ["Lấy mẫu kháng thể", "Cứu bác sĩ", "Mở lối ra sảnh chính"],
                (39, 35),
                (3, 6),
                lab_blocked,
                lab_decor,
                [
                    ItemPickup((34, 10), "Mẫu kháng thể", "Một ống mẫu được niêm phong. Có thể dùng để pha chế.", "antidote", color=GREEN),
                    ItemPickup((8, 34), "Medkit", "Hộp cứu thương còn đầy.", "heal", amount=50),
                    ItemPickup((18, 30), "Thẻ từ an ninh", "Mở cửa ra hành lang chính.", "keycard", color=BLUE),
                ],
                [
                    NPC("Bác sĩ Linh", (12, 8), ["Cậu tìm thấy ống mẫu rồi sao?", "Hãy mở cửa an ninh, chúng ta cần ra khỏi đây ngay!"], reward="medkit", portrait_color=CYAN, sprite_path="Sprites/Sprites_NPC/doctor.png"),
                ],
                [
                    (EvilWizard, (26, 8), "ranged"),
                    (Skeleton, (32, 24), "special"),
                    (Mushroom, (22, 34), "tank"),
                    (DashingGoblin, (37, 18), "fast"),
                ],
                (120, 220, 200),
                "Bác sĩ: Nếu lấy được mẫu kháng thể, có thể kéo dài thời gian sống sót. Nhưng hãy ra khỏi phòng thí nghiệm!",
                spawn_pool=[Goblin, DashingGoblin, FlyingEye, Skeleton],
                max_alive_enemies=14,
                spawn_interval_ms=2400,
            ),
            Chapter(
                "ground",
                "Chương 6: Tầng 1 - Sảnh chính",
                "Điểm nghẽn cuối cùng bên trong tòa nhà",
                ["Bạn đã xuống tới tầng trệt. Còi báo động vang dội khắp sảnh.", "Zombie đang tràn vào qua các cửa kính vỡ.", "Phải mở được cổng chính để ra sân sau."],
                ["Mở cổng chính", "Hạ 2 zombie đặc biệt", "Tìm lối ra sân"],
                (38, 36),
                (5, 5),
                ground_blocked,
                {(6, 6): "hut", (24, 20): "rock", (10, 30): "grass"},
                ground_items,
                ground_npcs,
                ground_enemies,
                RED,
                "Kỹ thuật viên Huy: Cổng chính đang kẹt. Tôi sẽ mở từ xa, hãy giữ chân chúng!",
                spawn_pool=[Goblin, DashingGoblin, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=2800,
            ),
            Chapter(
                "escape",
                "Chương 7: Sân bay - Thoát hiểm",
                "Trực thăng đang đợi",
                ["Bầu trời rực lửa, trực thăng cứu hộ đã ở phía trước.", "Hãy bật đèn hiệu beacon và trụ vững cho đến khi chúng có thể hạ cánh."],
                ["Bật đèn hiệu Beacon", "Trụ vững trong 25 giây", "Hạ boss Old Guardian", "Lên trực thăng"],
                (40, 37),
                (10, 10),
                ring_walls(),
                {(15, 15): "rock", (25, 25): "grass", (12, 30): "hut", (30, 12): "rock", (38, 36): "heli_pad"},
                [ItemPickup((34, 29), "Rescue Flare", "Pháo sáng xác nhận vị trí.", "flare", color=RED)],
                [],
                [
                    (BigFlyingEye, (33, 35), {"type": "boss", "health": 150}),
                    (OldGuardian, (25, 25), {"type": "boss", "health": 1200}),
                    (EvilWizard, (35, 10), "ranged"),
                    (EvilWizard, (10, 35), "ranged"),
                ],
                YELLOW,
                "Phi công: Tôi thấy beacon rồi! Đang hạ độ cao, hãy quét sạch khu vực!",
                holdout_seconds=30,
                chapter_type="holdout",
                spawn_pool=[Goblin, DashingGoblin, Skeleton, EvilWizard, Mushroom],
                max_alive_enemies=18,
                spawn_interval_ms=1800,
            ),
        ]

    def trailer_scenes(self):
        return [
            {
                "title": "Thành phố đã sụp đổ",
                "subtitle": "Virus làm biến cả khu trung tâm thành ổ zombie chỉ sau một đêm.",
                "accent": RED,
                "art": [("player", 160, 360), ("eye", 590, 160), ("goblin", 770, 360)],
            },
            {
                "title": "Tỉnh dậy trên tầng thượng",
                "subtitle": "Bạn bị mắc kẹt giữa khói lửa, chỉ còn tiếng bộ đàm cứu hộ vọng lại.",
                "accent": ORANGE,
                "art": [("player", 220, 340), ("hut", 670, 340), ("eye", 760, 180)],
            },
            {
                "title": "Xuống từng tầng, mở đường sống",
                "subtitle": "Tìm súng, vật tư, chìa khóa và khôi phục điện để mở lối thoát.",
                "accent": BLUE,
                "art": [("player", 170, 350), ("rocket", 540, 350), ("mortar", 760, 320)],
            },
            {
                "title": "Trụ vững tới chuyến bay cuối",
                "subtitle": "Ra sân, bật đèn hiệu và chống lại đợt zombie cuối cùng để thoát khỏi thành phố.",
                "accent": YELLOW,
                "art": [("player", 160, 360), ("mushroom", 620, 330), ("rocket", 800, 240)],
            },
        ]

    def set_chapter(self, index):
        self.chapter_index = index
        self.chapter = self.chapters[index]
        # Chỉ phát nhạc chương nếu đang trong trạng thái chơi (không phải ở Menu)
        if self.state != "menu":
            sound_manager.play_music(f"nhac_nen_{self.chapter.id}")
        self.mission = MissionTracker(self.chapter)
        self.story_enemies = []
        self.current_blocked = set(self.chapter.blocked_tiles)
        # Gate is physically closed until objectives complete
        if self.chapter.exit_pos and not self.exit_unlocked:
            self.current_blocked.add(self.chapter.exit_pos)
        # Yard gate is physically closed until switched (ground chapter only)
        if self.chapter.id == "ground":
            self.current_blocked.add(self.yard_gate_tile)
        self.player.x = self.chapter.start_pos[0] * TILE_SIZE + TILE_SIZE // 2
        self.player.y = self.chapter.start_pos[1] * TILE_SIZE + TILE_SIZE // 2
        self.chapter_card_timer = pygame.time.get_ticks() + 2800
        self.popup = self.chapter.radio_message
        self.popup_timer = pygame.time.get_ticks() + 4200
        self.dialog_npc = None
        self.dialog_speaker = ""
        self.dialog_color = CYAN
        self.dialog_lines = []
        self.dialog_queue = []
        self.show_map = False
        self.exit_path = []
        self.next_chapter_ready = False
        self.exit_unlocked = False
        self.yard_spawned = False
        self.yard_enemy_plan = []
        self.yard_gate_tile = (26, 22)
        self.last_objective_text = self.objective_label() if self.chapter else ""
        self.objective_flash_until = pygame.time.get_ticks() + 1800
        self.beacon_started_at = 0
        self.holdout_until = 0
        self.mouse_down = False
        self.shot_counter = 0
        self.frenzy_until = 0
        self.frenzy_window_until = 0
        self.last_spawn_at = pygame.time.get_ticks()
        self.tank = EscortTank(self.player.x - 70, self.player.y + 50)

        def is_yard_tile(tile: tuple[int, int]) -> bool:
            # Right/bottom quadrant: treated as outside yard in ground chapter
            x, y = tile
            return x >= 26 and y >= 22

        enemy_plan = list(self.chapter.enemy_plan)
        if self.chapter.id == "ground":
            # Do not spawn outside enemies until the main gate opens
            inside = []
            outside = []
            for e in enemy_plan:
                _, grid_pos, _ = e
                (outside if is_yard_tile(grid_pos) else inside).append(e)
            enemy_plan = inside
            self.yard_enemy_plan = outside

        for enemy_cls, grid_pos, archetype in enemy_plan:
            ex = grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
            ey = grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
            if isinstance(archetype, dict) and archetype.get("type") == "boss":
                enemy = enemy_cls(ex, ey)
                enemy.health = archetype.get("health", 100)
                enemy.max_health = archetype.get("health", 100)
                enemy.obstacle_map = self.build_obstacle_grid()
                self.story_enemies.append(StoryEnemy(enemy, "boss", grid_pos))
            else:
                enemy = enemy_cls(ex, ey)
                enemy.obstacle_map = self.build_obstacle_grid()
                self.story_enemies.append(StoryEnemy(enemy, archetype, grid_pos))

        # Finite spawn budget for this chapter (bắn hết là hết)
        target = self.enemy_target_per_chapter[min(index, len(self.enemy_target_per_chapter) - 1)]
        self.enemies_initial_count = len([e for e in self.story_enemies if not e.enemy.is_dead])
        self.enemies_remaining_to_spawn = max(0, target - self.enemies_initial_count)
        self.last_spawn_at = pygame.time.get_ticks()

        self.power_boxes = []
        self.gates = []
        if self.chapter.id == "roof":
            self.power_boxes = [(36, 33)]
        elif self.chapter.id == "office":
            self.power_boxes = [(34, 28)]
            self.gates = [(37, 35)]
        elif self.chapter.id == "medical":
            self.power_boxes = [(37, 33)]
            self.gates = [(39, 35)]
        elif self.chapter.id == "basement":
            self.power_boxes = [(38, 9)]   # generator panel
            self.gates = [(40, 35)]        # steel door to lab
        elif self.chapter.id == "lab":
            self.power_boxes = [(18, 30)]  # security console
            self.gates = [(39, 35)]        # exit to ground lobby
        elif self.chapter.id == "ground":
            self.gates = [(7, 7)]
            self.power_boxes = [(34, 29)]
            self.heli_zone = (40, 37)
            self.tank = EscortTank(self.player.x - 70, self.player.y + 40)

        self.queue_story_dialog("Radio", self.chapter.radio_message, YELLOW)
        self.queue_story_dialog("Survivor", self.chapter.intro_lines[0], self.chapter.chapter_color)

    def build_obstacle_grid(self):
        grid = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for x, y in self.current_blocked:
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                grid[y][x] = True
        return grid

    def queue_story_dialog(self, speaker, text, color=CYAN):
        self.dialog_queue.append((speaker, [text], color))
        if not self.dialog_npc:
            self.advance_dialog_queue()

    def queue_story_lines(self, speaker, lines, color=CYAN):
        self.dialog_queue.append((speaker, lines, color))
        if not self.dialog_npc:
            self.advance_dialog_queue()

    def advance_dialog_queue(self):
        if self.dialog_npc or not self.dialog_queue:
            return
        speaker, lines, color = self.dialog_queue.pop(0)
        self.dialog_npc = speaker
        self.dialog_speaker = speaker
        self.dialog_color = color
        self.dialog_lines = lines
        self.dialog_started_at = pygame.time.get_ticks()
        self.dialog_page_index = 0
        self.dialog_chars_shown = 0

    def current_tile(self):
        return (int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE))

    def item_pickup_rect(self, item, inflate=8):
        rect = pygame.Rect(item.grid_pos[0] * TILE_SIZE, item.grid_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if inflate:
            rect = rect.inflate(inflate, inflate)
        return rect

    def player_can_pick_item(self, item, inflate=8):
        return self.player.get_rect().colliderect(self.item_pickup_rect(item, inflate=inflate))

    def item_at_player(self):
        for item in self.chapter.items:
            # Money is auto-picked up; never require E
            if not item.collected:
                ix = item.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
                iy = item.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
                if math.hypot(ix - self.player.x, iy - self.player.y) <= INTERACT_RADIUS:
                    return item
        return None

    def npc_near_player(self):
        for npc in self.chapter.npcs:
            nx = npc.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
            ny = npc.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
            if math.hypot(nx - self.player.x, ny - self.player.y) <= INTERACT_RADIUS:
                return npc
        return None

    def interact(self):
        # 1. NPCs (Highest Priority)
        npc = self.npc_near_player()
        if npc:
            self.open_dialog(npc)
            return

        # 2. Items
        item = self.item_at_player()
        if item:
            self.collect_item(item)
            return

        # 3. Power Boxes / Interactive Tiles
        for bx, by in getattr(self, "power_boxes", []):
            pix_x = bx * TILE_SIZE + TILE_SIZE // 2
            pix_y = by * TILE_SIZE + TILE_SIZE // 2
            if math.hypot(pix_x - self.player.x, pix_y - self.player.y) <= INTERACT_RADIUS:
                self.activate_box((bx, by))
                return

    def unlock_weapon(self, weapon_data, equip_now=True):
        added = self.weapon_manager.add_weapon(
            weapon_data["name"],
            weapon_data["fire_rate"],
            weapon_data["reload_time"],
            weapon_data["image_path"],
            projectile_speed=weapon_data.get("projectile_speed", 5),
            damage=weapon_data.get("damage", 3000),
            projectile_radius=weapon_data.get("projectile_radius", 0),
            projectile_image=weapon_data.get("projectile_image", "Sprites/Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_00.png"),
            projectile_scale=weapon_data.get("projectile_scale", (48, 48)),
            equip_on_add=equip_now,
            melee=(weapon_data.get("type", "") == "melee")
        )
        if not added and equip_now:
            self.weapon_manager.select_weapon(weapon_data["name"])
        return added

    def spawn_weapon_drop(self, x, y):
        if random.random() > 0.23:
            return

        uncollected_drops = [item for item in self.chapter.items if item.item_type == "weapon_drop" and not item.collected]
        if len(uncollected_drops) >= 4:
            return

        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if not (1 <= tile_x < GRID_SIZE - 1 and 1 <= tile_y < GRID_SIZE - 1):
            return
        if (tile_x, tile_y) in self.current_blocked:
            return

        for item in self.chapter.items:
            if not item.collected and item.grid_pos == (tile_x, tile_y):
                return

        # Weighted rarity selection (only affects generated armory entries that have 'rarity')
        roll = random.random()
        want = "common" if roll < 0.78 else "rare" if roll < 0.96 else "epic"
        candidates = [w for w in WEAPON_DROP_POOL if w.get("rarity") == want]
        if not candidates:
            candidates = WEAPON_DROP_POOL
        weapon_data = dict(random.choice(candidates))
        # Find the sprite surface for this weapon (load on demand if not preloaded)
        wp_sprite = ALL_GRAPHICS_SURFACES.get(weapon_data["image_path"])
        if not wp_sprite and os.path.exists(weapon_data["image_path"]):
            try:
                wp_sprite = pygame.image.load(weapon_data["image_path"]).convert_alpha()
                ALL_GRAPHICS_SURFACES[weapon_data["image_path"]] = wp_sprite
            except Exception:
                wp_sprite = None
        if wp_sprite:
            wp_sprite = pygame.transform.scale(wp_sprite, (32, 24))

        self.chapter.items.append(
            ItemPickup(
                (tile_x, tile_y),
                weapon_data["name"],
                f"Zombie đã rơi {weapon_data['name']}. Bấm E để nhặt.",
                "weapon_drop",
                color=RARITY_COLORS.get(weapon_data.get("rarity", "common"), ORANGE),
                weapon_data=weapon_data,
                sprite_surface=wp_sprite
            )
        )

    def spawn_mission_item_at(self, tile: tuple[int, int], item_type: str, name: str, description: str, color=YELLOW, amount=0):
        """Spawn a mission item on a walkable tile if free."""
        tx, ty = tile
        if not (1 <= tx < GRID_SIZE - 1 and 1 <= ty < GRID_SIZE - 1):
            return False
        if (tx, ty) in self.current_blocked:
            return False
        for it in self.chapter.items:
            if not it.collected and it.grid_pos == (tx, ty):
                return False
        self.chapter.items.append(ItemPickup((tx, ty), name, description, item_type, amount=amount, color=color))
        sound_manager.play("nhat_do")
        return True

    def spawn_mission_item_near(self, tile: tuple[int, int], item_type: str, name: str, description: str, color=YELLOW, radius: int = 2):
        """Try to spawn near a tile; returns True on success."""
        tx, ty = tile
        # search diamond-ish rings around the point
        for r in range(0, max(0, radius) + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    if self.spawn_mission_item_at((tx + dx, ty + dy), item_type, name, description, color=color):
                        return True
        return False

    def spawn_money_drop_near(self, tile: tuple[int, int], amount: int = 1, radius: int = 2):
        """Spawn money near a tile; avoids blocked tiles so dropped coins are always reachable."""
        tx, ty = tile
        for r in range(0, max(0, radius) + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    if self.spawn_mission_item_at(
                        (tx + dx, ty + dy),
                        "money",
                        "Tien",
                        "1 tien roi tu zombie.",
                        color=YELLOW,
                        amount=max(1, int(amount or 1)),
                    ):
                        return True
        return False

    def collect_item(self, item):
        item.collected = True
        sound_manager.play("nhat_do")
        self.popup = item.description
        self.popup_timer = pygame.time.get_ticks() + 2600
        if item.item_type == "weapon":
            self.mission.data["weapon_collected"] = True
            if self.chapter.id == "roof":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
            self.unlock_weapon(
                {
                    "name": "Shotgun",
                    "fire_rate": 1.8,
                    "reload_time": 1.4,
                    "image_path": "Sprites/Sprites_Weapon/Shotgun-4.png",
                    "projectile_speed": 7,
                    "damage": 95,
                    "projectile_scale": (42, 28),
                },
                equip_now=True,
            )
            self.popup = "Đã nhặt Shotgun. Đã chuyển sang súng mới."
            self.queue_story_lines("Nhân vật chính", ["Được rồi, có thêm hỏa lực rồi.", "Giết 1 zombie nữa là xong màn khởi động."], ORANGE)
        elif item.item_type == "heal":
            self.player.heal(item.amount)
            self.mission.data["medkit_collected"] = True
            if self.chapter.id == "medical":
                self.mission.data["supply_cache"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
                self.queue_story_lines("Y tá Linh Tây", ["Lấy thêm băng gạc và thuốc tăng lực nếu thấy.", "Tầng dưới nguy hiểm hơn nhiều."], GREEN)
        elif item.item_type == "ammo":
            self.popup = f"Nhặt {item.amount} viên đạn dự trữ."
            # Feed reserve ammo into current weapon if applicable
            w = self.weapon_manager.current_weapon
            if w and not getattr(w, "melee", False):
                w.reserve_ammo += item.amount
        elif item.item_type == "armor":
            self.player.add_armor(item.amount)
            self.mission.data["supply_cache"] = True
            if self.chapter.id == "medical":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
            self.queue_story_dialog("Hero", "Áo giáp này sẽ giúp mình sống dai hơn.", CYAN)
        elif item.item_type == "rocket_weapon":
            self.unlock_weapon(
                {
                    "name": "Rocket Launcher",
                    "fire_rate": 1.1,
                    "reload_time": 2,
                    "image_path": "Sprites/Sprites_Weapon/RPG-reisized.png",
                    "projectile_speed": 4,
                    "damage": 180,
                    "projectile_radius": 80,
                    "projectile_image": "Sprites/Sprites_Weapon/RPG.png",
                    "projectile_scale": (34, 18),
                },
                equip_now=True,
            )
            self.popup = "Đã mở khóa Rocket Launcher và chuyển sang vũ khí mới."
            self.queue_story_lines("Y tá Linh", ["Phía dưới đang có đám đông rất lớn.", "Lấy vũ khí nổ này, nó sẽ giúp cậu mở đường."], GREEN)
        elif item.item_type == "weapon_drop":
            weapon_data = item.weapon_data or dict(random.choice(WEAPON_DROP_POOL))
            was_new = self.unlock_weapon(weapon_data, equip_now=True)
            if was_new:
                self.popup = f"Da nhat {weapon_data['name']}. Đã trang bị ngay."
            else:
                self.popup = f"Bạn đã có {weapon_data['name']}. Đã chuyển sang vũ khí này."
        elif item.item_type == "keycard":
            self.mission.data["keycard_collected"] = True
            self.queue_story_lines("Bảo vệ Nam", ["Tốt, đó là thẻ từ của phòng an ninh.", "Mang nó tới hộp điện bên phải."], BLUE)
            if self.chapter.id in {"office", "lab"}:
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2 if self.chapter.id == "office" else 2)
        elif item.item_type == "code":
            # Used in basement
            self.mission.data["basement_code"] = True
            self.popup = "Đã lấy được mã cửa: 4821. Hãy tới phòng máy và khởi động máy phát."
            self.queue_story_dialog("Hero", "Mã cửa phòng máy... mình cần tìm bảng điều khiển điện.", ORANGE)
            if self.chapter.id == "basement":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
        elif item.item_type == "antidote":
            # Used in lab
            self.mission.data["antidote_collected"] = True
            self.popup = "Đã lấy mẫu kháng thể. Có thể dùng để kéo dài sức bền."
            self.queue_story_lines("Bác sĩ Hoa", ["Tốt! Đây là mẫu quan trọng.", "Giờ mở cửa an ninh và thoát ra sảnh chính!"], CYAN)
            if self.chapter.id == "lab":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
        elif item.item_type == "power":
            self.popup = "Đã lấy cầu chì. Tới hộp điện để khôi phục nguồn."
            self.queue_story_dialog("Radio", "Điện phụ đang ở trạng thái offline. Hãy lắp cầu chì ngay.", YELLOW)
            if self.chapter.id == "office":
                self.mission.data["fuse_collected"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
        elif item.item_type == "exit":
            self.mission.data["supply_cache"] = True
            self.popup = "Thiết bị điều khiển cổng đã có trong tay."
            self.queue_story_dialog("Hero", "Mở được cổng tầng 1 rồi. Phải tiếp tục di chuyển.", ORANGE)
            if self.chapter.id == "medical":
                self.mission.data["control_fuse_collected"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
        elif item.item_type == "gate":
            self.mission.data["gate_opened"] = True
            self.popup = "Cổng sân đã mở. Đi tới beacon."
            if self.chapter.id == "ground":
                self.remove_gate_collision(self.yard_gate_tile)
                self.spawn_particles(self.yard_gate_tile[0] * TILE_SIZE + 8, self.yard_gate_tile[1] * TILE_SIZE + 8, YELLOW, count=18)
                sound_manager.play("mo_cong")
            else:
                self.remove_gate_collision(item.grid_pos)
            self.queue_story_lines("Kỹ thuật viên Huy", ["Cổng sân đã mở.", "Tôi sẽ giữ hệ thống điện ổn định, cậu ra beacon đi."], ORANGE)
        elif item.item_type == "signal":
            self.mission.data["signal_started"] = True
            self.beacon_started_at = pygame.time.get_ticks()
            self.holdout_until = self.beacon_started_at + self.chapter.holdout_seconds * 1000
            self.popup = "Tín hiệu cứu hộ đã phát. Trụ vững tới khi trực thăng tới."
            self.queue_story_lines("Phi công", ["Đã nhận được tín hiệu.", "Giữ vị trí, tôi sẽ hạ cánh trong ít phút nữa."], YELLOW)
        elif item.item_type == "flare":
            self.popup = "Phao sang da san sang cho diem ha canh."
        elif item.item_type == "money":
            amount = max(1, int(item.amount or 1))
            if hasattr(self.player, "money_mult"):
                amount = int(amount * self.player.money_mult)
            self.money += amount
            self.popup = f"+{amount} tien"
            self.popup_timer = pygame.time.get_ticks() + 1200

    def remove_gate_collision(self, gate_tile):
        if gate_tile in self.current_blocked:
            self.current_blocked.remove(gate_tile)
        for dx in range(-1, 2):
            pos = (gate_tile[0] + dx, gate_tile[1])
            if pos in self.current_blocked:
                self.current_blocked.remove(pos)
        for story_enemy in self.story_enemies:
            story_enemy.enemy.obstacle_map = self.build_obstacle_grid()

    def activate_box(self, tile):
        cid = self.chapter.id
        if cid == "roof":
            self.mission.data["power_restored"] = True
            self.popup = "Cua ky thuat da mo. Di xuong tang 3."
            self.mission.data["gate_opened"] = True
            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
        elif cid == "office":
            # Require linear stage: have keycard + fuse first
            if self.mission.data.get("keycard_collected") and self.mission.data.get("fuse_collected"):
                self.mission.data["power_restored"] = True
                self.mission.data["gate_opened"] = True
                self.popup = "Điện đã trở lại. Thang kỹ thuật tầng 2 đã mở."
                self.remove_gate_collision((37, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 4)
            else:
                self.popup = "Cần Keycard + Fuse trước khi kích hoạt lại hành lang."
        elif cid == "medical":
            # Require picking up Control Fuse first
            if self.mission.data.get("control_fuse_collected"):
                self.mission.data["gate_opened"] = True
                self.popup = "Lối xuống tầng 1 đã được mở."
                self.remove_gate_collision((39, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Cần nhặt thiết bị mở cổng (Control Fuse) trước."
        elif cid == "basement":
            if self.mission.data.get("basement_code", False) and self.mission.data.get("special_kills", 0) >= 2:
                self.mission.data["power_restored"] = True
                self.mission.data["gate_opened"] = True
                self.popup = "May phat da khoi dong. Cua sat den phong thi nghiem da mo."
                self.remove_gate_collision((40, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Cần mã cửa + hạ đủ 2 zombie đặc biệt trước."
        elif cid == "lab":
            if self.mission.data.get("antidote_collected", False) and self.mission.data.get("keycard_collected", False):
                self.mission.data["gate_opened"] = True
                self.popup = "Cửa an ninh mở. Đường ra sảnh chính đã thông."
                self.remove_gate_collision((39, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Cần thẻ từ và mẫu kháng thể trước khi mở cửa an ninh."
        elif cid == "ground":
            self.mission.data["signal_started"] = True
            self.beacon_started_at = pygame.time.get_ticks()
            self.holdout_until = self.beacon_started_at + self.chapter.holdout_seconds * 1000
            self.popup = "Beacon đã bật. Giữ vị trí."
        self.popup_timer = pygame.time.get_ticks() + 2800

    def open_dialog(self, npc):
        self.dialog_npc = npc
        self.dialog_speaker = npc.name
        self.dialog_color = npc.portrait_color
        self.dialog_lines = (["Quest: " + npc.quest] if npc.quest else []) + list(npc.lines)
        if not npc.interacted:
            npc.interacted = True
            self.saved_npcs += 1
            self.mission.data["npc_saved"] += 1
            if npc.reward == "map":
                self.popup = "Bạn nhận được sơ đồ an ninh tầng hiện tại."
            elif npc.reward == "medkit":
                self.player.heal(20)
                self.popup = "Y tá Linh hồi máu cho bạn."
            elif npc.reward == "shortcut":
                self.popup = "Kỹ thuật viên đánh dấu đường tắt ra sân."
            elif npc.reward == "radio":
                self.popup = "Bộ đàm bắt được kênh cứu hộ ổn định hơn."
            self.popup_timer = pygame.time.get_ticks() + 2600

    def update(self):
        if self.state == "menu":
            return
        if self.state == "pause":
            return
        if self.state == "playing":
            if self.show_shop:
                return
            # Pause gameplay while story dialogue is open (Genshin feel)
            if self.dialog_npc:
                return

            keys = pygame.key.get_pressed()
            self.player.update(keys, self.current_blocked, None, None, TILE_SIZE)
            if self.current_pet_instance:
                self.current_pet_instance.update(self.player.x, self.player.y, self.player.direction, 16.6) # approx 60fps dt
            self.player.x = max(TILE_SIZE, min(self.player.x, self.world_w - TILE_SIZE))
            self.player.y = max(TILE_SIZE, min(self.player.y, self.world_h - TILE_SIZE))

            # Regen logic from pet
            if getattr(self.player, "regen", 0) > 0:
                self.player.health = min(self.player.max_health, self.player.health + self.player.regen)

            # Auto-pickup money on contact
            for it in self.chapter.items:
                if it.collected:
                    continue
                if it.item_type != "money":
                    continue
                # Auto-pickup radius (pixel based for smoother feel)
                ix = it.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
                iy = it.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
                dist = math.hypot(ix - self.player.x, iy - self.player.y)
                if dist <= INTERACT_RADIUS * 0.7:
                    self.collect_item(it)
            
            self.camera.update(self.player.x, self.player.y, self.world_w, self.world_h)
            
            self.update_enemies()
            self.spawn_dynamic_enemies()
            self._trigger_clear_dialog_if_ready()
            
            if self.chapter.id == "ground" and self.mission.data["gate_opened"]:
                self.tank.set_target(self.player.x - 40, self.player.y + 35)
            self.tank.update()
            
            mx, my = pygame.mouse.get_pos()
            world_mx, world_my = self.camera.screen_to_world(mx, my)
            
            shot_fired = self.weapon_manager.update(
                self.player.x,
                self.player.y,
                world_mx,
                world_my,
                self.mouse_down and mx < SCREEN_WIDTH - SIDEBAR_WIDTH,
                [entry.enemy for entry in self.story_enemies],
                self.current_blocked,
                fire_rate_mult=getattr(self.player, "fire_rate_mult", 1.0),
                damage_mult=getattr(self.player, "damage_mult", 1.0)
            )

            # Update exit path every 60 frames (1s) to save performance
            self.exit_path_timer -= 1
            if self.exit_path_timer <= 0:
                self.update_exit_path()
                self.exit_path_timer = 60
            
            self.skill_manager.update([entry.enemy for entry in self.story_enemies], self.current_blocked)
            self.update_particles()
            self.handle_progression()
            self.check_auto_transition()

            # Player hit SFX and Combo Reset
            now = pygame.time.get_ticks()
            if self.player.health < self._last_player_hp:
                if now - self._last_player_hit_sfx_at > 120:
                    self._last_player_hit_sfx_at = now
                    sound_manager.play("nhan_vat_trung_don")
                # Reset combo on hit
                if self.combo_counter > 0:
                    self.combo_counter = 0
                    self.frenzy_active = False
                    self.player.frenzy_active = False
                    self.player.damage_mult = 1.0
                    self.spawn_particles(self.player.x, self.player.y, RED, count=20)
                    # Play a "combo break" sound effect if it was high
                    if self.combo_counter >= 5:
                        sound_manager.play("quai_trung_dan") 
            self._last_player_hp = self.player.health
            
            # Sync Frenzy state to player
            self.player.frenzy_active = self.frenzy_active
            
            if self.chapter.id == "escape" and hasattr(self, 'rescue_arrived') and self.rescue_arrived:
                # Kiem tra xem nguoi choi da den Helipad chua
                dist_to_extract = math.hypot(self.player.x - 38*TILE_SIZE, self.player.y - 36*TILE_SIZE)
                if dist_to_extract < 64:
                    self.state = "win"
                    sound_manager.play_music("nhac_chien_thang")

            if self.player.health <= 0:
                self.end_reason = "Bạn đã bị zombie áp đảo trước khi thoát được khỏi thành phố."
                self.state = "lose"
                sound_manager.play_music("nhac_that_bai")

    def update_frenzy(self, shot_fired):
        now = pygame.time.get_ticks()
        # Combo window check
        if now > self.frenzy_window_until and self.combo_counter > 0:
            self.combo_counter = 0
            self.frenzy_active = False
            self.player.frenzy_active = False
            self.player.damage_mult = 1.0

        # Update combo texts
        for ct in self.combo_texts[:]:
            ct.life -= 1
            ct.y -= 0.8 # float up
            if ct.life <= 0:
                self.combo_texts.remove(ct)
        
        # Update Item timers (fade out)
        for it in self.chapter.items[:]:
            if it.timer > 0:
                it.timer -= 1
                if it.timer <= 0:
                    it.collected = True # Mark as collected to remove it from world

    def spawn_dynamic_enemies(self):
        now = pygame.time.get_ticks()
        if self.enemies_remaining_to_spawn <= 0:
            return
        alive = [entry for entry in self.story_enemies if not entry.enemy.is_dead]
        if len(alive) >= self.chapter.max_alive_enemies:
            return
        if now - self.last_spawn_at < self.chapter.spawn_interval_ms:
            return
        if not self.chapter.spawn_pool:
            return

        spawn_candidates = [(2, 2), (41, 2), (2, 41), (41, 41), (4, 20), (39, 20), (20, 4), (20, 39)]
        player_tile = self.current_tile()
        valid = []
        for tile in spawn_candidates:
            if tile in self.current_blocked:
                continue
            if abs(tile[0] - player_tile[0]) + abs(tile[1] - player_tile[1]) < 12:
                continue
            valid.append(tile)
        if not valid:
            return

        enemy_cls = random.choice(self.chapter.spawn_pool)
        tile = random.choice(valid)
        ex = tile[0] * TILE_SIZE + TILE_SIZE // 2
        ey = tile[1] * TILE_SIZE + TILE_SIZE // 2
        enemy = enemy_cls(ex, ey)
        enemy.obstacle_map = self.build_obstacle_grid()
        archetype = "basic"
        if enemy_cls in (DashingGoblin, FlyingEye):
            archetype = "fast"
        elif enemy_cls in (Skeleton, TeleportingMushroom):
            archetype = "special"
        elif enemy_cls is Mushroom:
            archetype = "tank"
        self.story_enemies.append(StoryEnemy(enemy, archetype, tile))
        self.last_spawn_at = now
        self.enemies_remaining_to_spawn = max(0, self.enemies_remaining_to_spawn - 1)

    def update_enemies(self):
        for entry in self.story_enemies:
            enemy = entry.enemy
            # Enemy hit SFX (detect health drop since last loop)
            now = pygame.time.get_ticks()
            cur_hp = getattr(enemy, "health", 0)
            if (not enemy.is_dead) and cur_hp < entry._last_health and now - entry._last_hit_sfx_at > 90:
                entry._last_hit_sfx_at = now
                sound_manager.play("quai_trung_dan")
            entry._last_health = cur_hp

            enemy.obstacle_map = self.build_obstacle_grid()
            enemy.update(self.player)
            enemy.x = max(TILE_SIZE, min(enemy.x, self.world_w - TILE_SIZE))
            enemy.y = max(TILE_SIZE, min(enemy.y, self.world_h - TILE_SIZE))
            if enemy.is_dead and not entry.dead_registered:
                self.handle_enemy_death(entry)
                # Mission drops to make objectives obvious
                if self.chapter.id == "office" and not self.mission.data.get("keycard_collected", False):
                    # Guaranteed: kill 10 zombies -> keycard drops (not RNG)
                    if self.mission.data.get("zombies_killed", 0) >= 10 and "office_keycard_drop" not in self.story_flags:
                        # Only mark dropped when we successfully place it
                        if self.spawn_mission_item_near(etile, "keycard", "Keycard", "Thẻ từ an ninh roi ra sau khi ha 10 zombie.", color=BLUE, radius=3):
                            self.story_flags.add("office_keycard_drop")
                            self.popup = "Da ha du 10 zombie: Keycard da roi!"
                            self.popup_timer = pygame.time.get_ticks() + 2200
                            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
                if self.chapter.id == "medical":
                    # Stage 1 requires 3 special kills
                    if self.mission.data.get("special_kills", 0) >= 3:
                        self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
                if self.chapter.id == "lab" and not self.mission.data.get("antidote_collected", False):
                    # First special kill drops antidote vial
                    if entry.archetype == "special":
                        if self.spawn_mission_item_near(etile, "antidote", "Mẫu kháng thể", "Ống mẫu rơi từ kẻ tấn công.", color=GREEN, radius=3):
                            self.popup = "Co ong mau khang the roi ra!"
                            self.popup_timer = pygame.time.get_ticks() + 2200
                            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
                if self.chapter.id == "basement":
                    if self.mission.data.get("special_kills", 0) >= 2:
                        self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
                self.spawn_weapon_drop(enemy.x, enemy.y)
        self.story_enemies = [
            entry for entry in self.story_enemies
            if not (entry.enemy.is_dead and entry.enemy.death_animation_completed)
        ]

    def handle_enemy_death(self, entry):
        entry.dead_registered = True
        sound_manager.play("quai_chet")
        self.kill_count += 1
        self.mission.data["zombies_killed"] += 1
        
        enemy = entry.enemy
        now = pygame.time.get_ticks()
        etile = entry.tile()

        # Combo Logic
        self.combo_counter += 1
        self.frenzy_window_until = now + 3000 # 3s window

        # Combo Milestones Sounds
        if self.combo_counter in [5, 15, 25]:
            sound_manager.play("nhat_do")
            self.combo_shake_until = now + 250
            self.popup = f"COMBO {self.combo_counter} BREAKING!"
            self.popup_timer = now + 1500
        elif self.combo_counter in [10, 20, 30]:
            sound_manager.play("hoan_thanh")
            self.combo_shake_until = now + 500
            self.popup = f"ULTRA COMBO {self.combo_counter}!"
            self.popup_timer = now + 2000

        # Frenzy Mode
        if self.combo_counter >= 3:
            self.frenzy_active = True
            # Apply damage buff
            self.player.damage_mult = 1.2
            
        # Combo Visual
        tier_text = ""
        reward_mult = 1.0
        for threshold, label, mult in COMBO_TIERS:
            if self.combo_counter >= threshold:
                tier_text = label
                reward_mult = mult
        
        display_text = f"{self.combo_counter} COMBO"
        if tier_text and self.combo_counter in [3, 5, 10]:
            display_text = f"{tier_text}!"

        self.combo_texts.append(ComboText(
            display_text,
            enemy.x, enemy.y - 40,
            life=60, max_life=60,
            color=YELLOW if self.combo_counter < 5 else ORANGE if self.combo_counter < 10 else RED,
            size=20 + min(self.combo_counter * 2, 20)
        ))

        # Loot Drop
        roll = random.random()
        if entry.archetype in {"special", "tank", "boss"}:
            # Guaranteed drop for specials
            if type(enemy).__name__ == "ShadowWraith":
                self.spawn_loot_at(etile, "material", "Mảnh bóng tối", "Nguyên liệu quý từ ShadowWraith.", color=PURPLE)
            else:
                # Other specials drop something nice
                self.spawn_loot_at(etile, "weapon_drop", "Vũ khí", "Rơi từ quái mạnh.", color=ORANGE)
            self.mission.data["special_kills"] += 1
            if entry.archetype == "boss":
                self.mission.data["boss_down"] = True
        else:
            if roll < 0.30: # 30% Money
                amount = int(random.randint(1, 3) * reward_mult)
                self.spawn_loot_at(etile, "money", "Tiền", f"+{amount} tiền rơi ra.", amount=amount, color=YELLOW)
            elif roll < 0.40: # 10% Ammo
                amount = random.randint(5, 12)
                self.spawn_loot_at(etile, "ammo", "Đạn", f"Nhặt {amount} viên đạn.", amount=amount, color=CYAN)
            elif roll < 0.45: # 5% Medkit
                self.spawn_loot_at(etile, "heal", "Medkit nhỏ", "Hồi 20 HP.", amount=20, color=GREEN)

        # Stage progression hooks
        if self.chapter.id == "roof" and self.mission.data.get("weapon_collected") and self.mission.data["zombies_killed"] >= 1:
            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)

    def spawn_loot_at(self, tile, item_type, name, description, amount=0, color=WHITE):
        """Spawn a temporary loot item that fades away."""
        # Ensure tile is valid
        tx, ty = tile
        if not (1 <= tx < GRID_SIZE - 1 and 1 <= ty < GRID_SIZE - 1): return
        if (tx, ty) in self.current_blocked: return
        
        item = ItemPickup(
            (tx, ty), name, description, item_type, 
            amount=amount, color=color, 
            timer=360, max_timer=360 # 6 seconds at 60fps
        )
        self.chapter.items.append(item)

    def _trigger_clear_dialog_if_ready(self):
        # When all enemies are dead and no more are allowed to spawn, play story chat
        if self.dialog_npc:
            return
        if self.enemies_remaining_to_spawn > 0:
            return
        alive = [entry for entry in self.story_enemies if not entry.enemy.is_dead]
        if alive:
            return
        flag = f"clear_dialog_{self.chapter.id}"
        if flag in self.story_flags:
            return
        self.story_flags.add(flag)

        cid = self.chapter.id
        # Small cinematic exchanges per chapter (Genshin-ish)
        if cid == "roof":
            self.queue_story_lines("Hero", ["Hết rồi... tạm an toàn.", "Mình phải kiếm đường xuống dưới."], ORANGE)
            self.queue_story_lines("Radio", ["Tín hiệu yếu. Cố giữ bình tĩnh.", "Đi theo đèn chỉ dẫn, tránh xa bóng tối."], YELLOW)
        elif cid == "office":
            self.queue_story_lines("Bảo vệ Linh", ["Khu này sạch. Cậu làm tốt lắm.", "Nhớ nhặt Keycard, nó mở cửa an ninh."], BLUE)
            self.queue_story_lines("Hero", ["Rõ. Mình sẽ tìm trong xác bọn đặc biệt."], ORANGE)
        elif cid == "medical":
            self.queue_story_lines("Y tá Linh Tây", ["Cậu vẫn ổn chứ?", "Lấy đồ y tế rồi đi nhanh, chúng sẽ quay lại."], GREEN)
            self.queue_story_lines("Hero", ["Ừ. Mình đi đây."], ORANGE)
        elif cid == "basement":
            self.queue_story_lines("Radio", ["Dưới tầng hầm có máy phát.", "Khởi động được nó thì đường thoát sẽ mở."], YELLOW)
            self.queue_story_lines("Hero", ["Nghe như kế hoạch duy nhất."], ORANGE)
        elif cid == "lab":
            self.queue_story_lines("Nhà nghiên cứu An", ["Tốt! Khu lab đã yên.", "Mẫu kháng thể phải được mang ra ngoài ngay."], CYAN)
            self.queue_story_lines("Hero", ["Mở cổng. Mình ra sảnh."], ORANGE)
        elif cid == "ground":
            self.queue_story_lines("Phi công", ["Khu vực tạm sạch!", "Bật beacon lên, tôi sẽ hạ độ cao."], YELLOW)
            self.queue_story_lines("Hero", ["Đã rõ. Mình giữ vị trí."], ORANGE)
        else:
            self.queue_story_lines("Hero", ["Khu này sạch... đi tiếp thôi."], ORANGE)

    def handle_progression(self):
        if self.chapter.id == "roof" and self.mission.data["zombies_killed"] >= 1 and "roof_first_kill" not in self.story_flags:
            self.story_flags.add("roof_first_kill")
            self.queue_story_lines("Nhân vật chính", ["Con đầu tiên đã gục.", "Mình phải lấy đồ rồi mở lối xuống ngay."], ORANGE)
        if self.chapter.id == "roof" and self.mission.data["weapon_collected"] and self.mission.data["zombies_killed"] >= 1:
            # Chapter 1: open gate immediately after the simple starter objectives
            self.mission.data["medkit_collected"] = True
            self.mission.data["power_restored"] = True
            self.mission.data["gate_opened"] = True
            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
        if self.chapter.id == "office" and self.mission.data["power_restored"] and "office_power" not in self.story_flags:
            self.story_flags.add("office_power")
            self.queue_story_lines("Bảo vệ Linh", ["Điện đã lên. Camera cho thấy cầu thang kỹ thuật đã mở.", "Đi nhanh lên, chúng đang áp sát từ hành lang sau."], BLUE)

        # Failsafe: if player reached 10 kills but keycard never spawned (blocked tile etc)
        if self.chapter.id == "office" and not self.mission.data.get("keycard_collected", False):
            if int(self.mission.data.get("zombies_killed", 0) or 0) >= 10:
                has_keycard_on_ground = any((not it.collected) and it.item_type == "keycard" for it in self.chapter.items)
                if not has_keycard_on_ground:
                    ptile = self.current_tile()
                    if self.spawn_mission_item_near(ptile, "keycard", "Keycard", "Thẻ từ an ninh (failsafe).", color=BLUE, radius=2):
                        self.popup = "Keycard đã xuất hiện gần bạn!"
                        self.popup_timer = pygame.time.get_ticks() + 2200
                        self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)

        # Failsafe: lab antidote can never get lost due to blocked tiles
        if self.chapter.id == "lab" and not self.mission.data.get("antidote_collected", False):
            has_on_ground = any((not it.collected) and it.item_type == "antidote" for it in self.chapter.items)
            if self.mission.data.get("special_kills", 0) >= 1 and not has_on_ground:
                ptile = self.current_tile()
                if self.spawn_mission_item_near(ptile, "antidote", "Mẫu kháng thể", "Mẫu kháng thể (failsafe).", color=GREEN, radius=2):
                    self.popup = "Mẫu kháng thể đã xuất hiện gần bạn!"
                    self.popup_timer = pygame.time.get_ticks() + 2200
                    self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
        if self.chapter.id == "medical" and self.mission.data["special_kills"] >= 2 and "medical_warning" not in self.story_flags:
            self.story_flags.add("medical_warning")
            self.queue_story_lines("Y tá Linh", ["Có loại đột biến đang đi trong kho.", "Đừng đối mặt quá lâu, nó rất trâu."], GREEN)
        if self.chapter.id == "medical" and self.mission.data["special_kills"] >= 3:
            self.mission.data["specials_cleared"] = True
        if self.chapter.id == "ground" and self.mission.data["signal_started"] and pygame.time.get_ticks() >= self.holdout_until:
            self.mission.data["holdout_complete"] = True
        if self.chapter.id == "ground" and self.mission.data["signal_started"] and "ground_hold" not in self.story_flags:
            self.story_flags.add("ground_hold")
            self.queue_story_lines("Phi công", ["Tôi đang hạ độ cao.", "Đừng để boss đột biến áp sát beacon."], YELLOW)
            
        if self.chapter.id == "escape" and self.mission.data["boss_down"]:
            if not getattr(self, "countdown_started", False):
                self.countdown_started = True
                self.holdout_until = pygame.time.get_ticks() + 30 * 1000  # 30 giây
                self.queue_story_lines("Phi công", ["Đã xác nhận mục tiêu nguy hiểm bị hạ.", "Đang bay tới vị trí. Giữ vững trong 30 giây!"], YELLOW)

            if getattr(self, "countdown_started", False) and pygame.time.get_ticks() >= self.holdout_until and not getattr(self, "rescue_arrived", False):
                self.rescue_arrived = True
                self.mission.data["helicopter_arrived"] = True
                self.queue_story_lines("Phi công", ["Trực thăng đã hạ cánh! Lên nhanh nào!"], YELLOW)

        # Auto unlock exit gate when objectives done
        if self.mission.complete() and not self.exit_unlocked:
            self.exit_unlocked = True
        if self.chapter.exit_pos in self.current_blocked:
            self.current_blocked.remove(self.chapter.exit_pos)
            if self.chapter.exit_pos:
                self.remove_gate_collision(self.chapter.exit_pos)
            sound_manager.play("hoan_thanh")
            self.popup = "Cổng đã mở. Chạy tới cổng để đi tiếp."
            self.popup_timer = pygame.time.get_ticks() + 3200

        # Ground floor: once main gate opened -> spawn outside yard enemies
        if self.chapter.id == "ground" and self.mission.data.get("gate_opened", False) and not self.yard_spawned:
            self.yard_spawned = True
            for enemy_cls, grid_pos, archetype in self.yard_enemy_plan:
                ex = grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
                ey = grid_pos[1] * TILE_SIZE + TILE_SIZE // 2
                enemy = enemy_cls(ex, ey)
                enemy.obstacle_map = self.build_obstacle_grid()
                arch = "boss" if isinstance(archetype, dict) and archetype.get("type") == "boss" else archetype
                self.story_enemies.append(StoryEnemy(enemy, arch, grid_pos))
            self.popup = "Tiếng cổng sắt vang lên... Quái ngoài sân đã phát hiện bạn!"
            self.popup_timer = pygame.time.get_ticks() + 3600

    def check_auto_transition(self):
        """Walk-through gate to go next chapter (no button press).
        
        Triggers continuously every frame when the player overlaps the
        open exit gate within a 1.5x tile radius (pixel-based hitbox).
        Consistent across all chapters.
        """
        if not self.exit_unlocked:
            return
        if not self.chapter.exit_pos:
            return

        ex, ey = self.chapter.exit_pos
        # Exit gate centre in world-pixel coordinates
        gate_cx = ex * TILE_SIZE + TILE_SIZE // 2
        gate_cy = ey * TILE_SIZE + TILE_SIZE // 2

        # 1.5× tile hitbox radius for generous, frustration-free detection
        DOOR_RADIUS = TILE_SIZE * 1.5

        dist = math.hypot(self.player.x - gate_cx, self.player.y - gate_cy)
        if dist <= DOOR_RADIUS:
            if self.chapter_index < len(self.chapters) - 1:
                # Phát âm thanh qua màn
                sound_manager.play("qua_man")
                self.set_chapter(self.chapter_index + 1)
                self.state = "playing"
            else:
                # Final chapter — trigger win state
                self.state = "win"
                self.end_reason = "Bạn đã thoát thành công khỏi tòa nhà!"

    def spawn_particles(self, x, y, color, count=5):
        for _ in range(count):
            self.particles.append(Particle(
                x, y,
                random.uniform(-3, 3), random.uniform(-3, 3),
                random.randint(15, 30),
                color,
                random.randint(2, 4)
            ))

    def update_particles(self):
        for p in self.particles:
            p.x += p.dx
            p.y += p.dy
            p.life -= 1
        self.particles = [p for p in self.particles if p.life > 0]

    def draw_shadow(self, surface, x, y, width=44, height=18):
        # Ve bong do don gian
        shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, width, height))
        surface.blit(shadow_surf, (x - width // 2, y - height // 2))

    def build_obstacle_grid(self):
        """Trả về tập hợp các ô bị chặn trong bán kính gần người chơi để AI tìm đường hiệu quả."""
        px, py = int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE)
        radius = 40 
        local_blocked = set()
        for bx, by in self.current_blocked:
            if abs(bx - px) <= radius and abs(by - py) <= radius:
                local_blocked.add((bx, by))
        return local_blocked

    def build_danger_map(self):
        danger_map = {}
        for entry in self.story_enemies:
            if entry.enemy.is_dead:
                continue
            ex, ey = entry.tile()
            for x in range(max(0, ex - 4), min(GRID_SIZE, ex + 5)):
                for y in range(max(0, ey - 4), min(GRID_SIZE, ey + 5)):
                    dist = abs(ex - x) + abs(ey - y)
                    danger_map[(x, y)] = danger_map.get((x, y), 0) + max(0, 6 - dist)
        return danger_map

    def objective_tile(self):
        chapter_id = self.chapter.id
        s = int(self.mission.data.get("stage", 0) or 0)
        if chapter_id == "roof":
            if s <= 0 and not self.mission.data["weapon_collected"]:
                return (6, 7)
            if s <= 1:
                return (18, 7)
            return self.chapter.exit_pos
        if chapter_id == "office":
            if s <= 0:
                return (22, 22)
            if s == 1:
                # keycard drop zone is dynamic; hint toward center
                return (22, 22)
            if s == 2:
                return (35, 28)  # fuse item
            if s == 3:
                return (34, 28)  # power box
            return self.chapter.exit_pos
        if chapter_id == "medical":
            if s == 0:
                return (6, 6)
            if s == 1:
                return (19, 20)
            if s == 2:
                return (37, 33)  # control fuse item tile
            if s == 3:
                return (37, 33)  # power box tile in set_chapter
            return self.chapter.exit_pos
        if chapter_id == "basement":
            if s == 0:
                return (8, 34)
            if s == 1:
                return (22, 30)
            if s == 2:
                return (38, 9)
            return self.chapter.exit_pos
        if chapter_id == "lab":
            if s == 0:
                return (32, 24)
            if s == 1:
                return (32, 24)
            if s == 2:
                return (18, 30)  # keycard item
            if s == 3:
                return (18, 30)  # security console
            return self.chapter.exit_pos
        if not self.mission.data["gate_opened"]:
            return (7, 7)
        if not self.mission.data["signal_started"]:
            return (34, 29)
        return self.chapter.exit_pos

    def objective_label(self):
        cid = self.chapter.id
        s = int(self.mission.data.get("stage", 0) or 0)
        if cid == "roof":
            if s == 0:
                return "Nhặt vũ khí"
            if s == 1:
                return "Hạ 1 zombie"
            return "Tới cổng để xuống tầng 3"
        if cid == "office":
            if s == 0:
                k = min(int(self.mission.data.get("zombies_killed", 0) or 0), 10)
                return f"Hạ đủ 10 zombie ({k}/10)"
            if s == 1:
                return "Nhặt Keycard"
            if s == 2:
                return "Nhặt cầu chì (Fuse)"
            if s == 3:
                return "Bật điện ở hộp điện"
            return "Tới cổng để xuống tầng 2"
        if cid == "medical":
            if s == 0:
                return "Nhặt vật tư y tế"
            if s == 1:
                return "Hạ 3 zombie đặc biệt"
            if s == 2:
                return "Nhặt Control Fuse"
            return "Kích hoạt hộp điện để mở cổng"
        if cid == "basement":
            if s == 0:
                return "Nhặt sổ tay mã cửa (4821)"
            if s == 1:
                return "Hạ 2 zombie đặc biệt"
            if s == 2:
                return "Bật máy phát (hộp điện)"
            return "Tới cổng để vào phòng thí nghiệm"
        if cid == "lab":
            if s == 0:
                return "Hạ 1 zombie đặc biệt để rơi mẫu"
            if s == 1:
                return "Nhặt mẫu kháng thể"
            if s == 2:
                return "Nhặt thẻ từ an ninh"
            return "Mở cửa an ninh (console)"
        if not self.mission.data["gate_opened"]:
            return "Mo cong chính"
        if not self.mission.data["signal_started"]:
            return "Kích hoạt beacon"
        return "Ra điểm trực thăng"

    def update_exit_path(self):
        """Update the BFS path to the current objective or exit portal."""
        current_objective = self.objective_label()
        if current_objective != self.last_objective_text:
            self.last_objective_text = current_objective
            self.objective_flash_until = pygame.time.get_ticks() + 1800
        
        start = self.current_tile()
        goal = self.objective_tile()
        blocked = self.current_blocked
        
        if start and goal:
            mode = self.hint_modes[self.hint_mode_index]
            if mode == "DFS":
                from pathfinding import dfs
                self.exit_path = dfs(start, goal, GRID_SIZE, GRID_SIZE, blocked)
            else:
                self.exit_path = bfs(start, goal, GRID_SIZE, GRID_SIZE, blocked)

    def draw_path_overlay(self, surface):
        """Draw the BFS path for the player."""
        if not self.exit_path or len(self.exit_path) < 2: 
            return
            
        # Bright Cyan/Green that glows in the dark
        color = (0, 255, 255) 
        points = []
        for x, y in self.exit_path:
            sx, sy = self.camera.world_to_screen(x * TILE_SIZE + 8, y * TILE_SIZE + 8)
            points.append((sx, sy))
            
        if len(points) > 1:
            # Draw a thicker glowing line
            pygame.draw.lines(surface, color, False, points, 4)
            # Draw start and end markers
            for i, p in enumerate(points):
                if i % 4 == 0:
                    pygame.draw.circle(surface, color, p, 3)

    def draw(self):
        screen.fill(BLACK)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "intro":
            self.draw_intro()
        elif self.state == "playing":
            self.draw_world()
            self.draw_sidebar()
            self.draw_overlays()
        elif self.state == "pause":
            self.draw_world()
            self.draw_sidebar()
            self.draw_pause()
        elif self.state in {"win", "lose"}:
            self.draw_end_screen()
        pygame.display.flip()

    def draw_world(self):
        # We don't use a separate world_surface for infinite map because it's too large
        self.render_world(screen)
        # Vẽ hiệu ứng kỹ năng
        self.skill_manager.draw(screen, self.camera)

        # Darkness overlay (power-out ambience)
        self.draw_darkness(screen)

        # DRAW PATH ON TOP OF DARKNESS so it glows
        self.draw_path_overlay(screen)

        # HUD mission always visible
        self.draw_mission_hud(screen)

    def draw_mission_hud(self, surface):
        """Always-visible mission HUD (no need to talk to NPC)."""
        if self.state != "playing" or not self.chapter or not self.mission:
            return
        if self.dialog_npc:
            return
        rect = pygame.Rect(14, 14, 320, 92)

        # Semi-transparent panel so it doesn't block the map
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 14, 20, 140), panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (*self.chapter.chapter_color, 180), panel.get_rect(), 2, border_radius=14)
        pygame.draw.rect(panel, (*self.chapter.chapter_color, 220), (0, 0, rect.width, 4), border_top_left_radius=14, border_top_right_radius=14)

        # Title + current objective (subtle)
        panel.blit(self.font_small.render("Quest", True, (220, 220, 230)), (12, 10))
        obj = self.objective_label()
        panel.blit(self.font_small.render(obj, True, (190, 190, 205)), (12, 28))

        # Checkpoints
        yy = 50
        for text, done in self.mission.objectives()[:3]:
            mark = "✓" if done else "•"
            col = (120, 230, 150) if done else (160, 165, 180)
            panel.blit(self.font_small.render(f"{mark} {text}", True, col), (12, yy))
            yy += 18

        surface.blit(panel, (rect.x, rect.y))

    def draw_darkness(self, surface):
        """Simulate blackout: dark screen + light around player."""
        cid = self.chapter.id if self.chapter else ""
        if cid in {"roof", "escape"}:
            return
        # If power restored, keep only a very subtle vignette
        power_on = bool(self.mission and self.mission.data.get("power_restored", False))
        base_alpha = 80 if power_on else 190
        # Flicker when power is off
        if not power_on:
            t = pygame.time.get_ticks()
            if (t // 220) % 7 == 0:
                base_alpha = 230
            elif (t // 180) % 9 == 0:
                base_alpha = 160

        darkness = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, base_alpha))

        # Light around player: "cut out" with gradient circles
        psx, psy = self.camera.world_to_screen(self.player.x, self.player.y)
        radius = 170 if power_on else 140
        for i in range(8):
            r = int(radius * (1 - i / 8))
            a = int(180 * (i / 8))
            pygame.draw.circle(darkness, (0, 0, 0, a), (int(psx), int(psy)), r)

        surface.blit(darkness, (0, 0))

    def render_world(self, surface):
        # Get visible tile range from camera
        min_tx, max_tx, min_ty, max_ty = self.camera.get_visible_tile_range(TILE_SIZE)
        custom_map_active = self.map_world_surface is not None
        
        # 1. Background Backdrop
        self.draw_chapter_backdrop(surface)
        
        # 2. Tiles
        current_tiles = CHAPTER_TILES.get(self.chapter.id)
        if not current_tiles:
            base_1, base_2, wall_tile = DESERT_TILE, DESERT_TILE_ALT, DESERT_WALL
        else:
            base_1, base_2, wall_tile = current_tiles["floor1"], current_tiles["floor2"], current_tiles["wall"]

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
                if custom_map_active:
                    src_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    surface.blit(self.map_world_surface, (sx, sy), src_rect)
                else:
                    base_tile = base_2 if (tx * 3 + ty * 5) % 11 == 0 else base_1
                    surface.blit(base_tile, (sx, sy))

                if (tx, ty) in self.current_blocked:
                    # Draw solid wall tile first (clean readable walls)
                    surface.blit(wall_tile, (sx, sy))
                    # Optional sparse contextual props on some blocked tiles (reduce clutter)
                    prop_key = obstacle_prop_for_tile(self.chapter.id, tx, ty)
                    if prop_key and ((tx * 5 + ty * 7) % 11 == 0):
                        draw_prop(surface, prop_key, sx, sy)
                else:
                    # Outdoor-only ambient decals (avoid weird grass inside buildings)
                    if self.chapter.id in {"roof", "ground", "escape"}:
                        if (tx + ty) % 9 == 0:
                            surface.blit(DESERT_GRASS, (sx, sy))
                        elif (tx * 7 + ty * 3) % 19 == 0:
                            surface.blit(DESERT_GRASS_TUFT, (sx, sy))
                
                # Ve vat trang tri Chapter
                prop = self.chapter.decor_tiles.get((tx, ty))
                if prop:
                    if prop == "heli_pad" and hasattr(self, 'rescue_arrived') and self.rescue_arrived:
                        # Draw Heli-pad and Rescue Helidrop
                        pygame.draw.rect(surface, YELLOW, (sx-32, sy-32, 96, 96), 3)
                        screen.blit(HELICOPTER, (sx-75, sy-75))
                    elif prop == "hut":
                        surface.blit(DESERT_HUT, (sx, sy - 32))
                    elif prop == "rock":
                        surface.blit(DESERT_BIG_ROCK, (sx, sy))
                    elif prop == "grass":
                        surface.blit(DESERT_BIG_GRASS, (sx, sy))
                    else:
                        draw_prop(surface, prop, sx, sy)
                    
        # Gate at chapter exit (shows locked/unlocked state)
        if self.chapter.exit_pos:
            ex, ey = self.chapter.exit_pos
            if self.camera.is_visible(ex * TILE_SIZE, ey * TILE_SIZE):
                gsx, gsy = self.camera.world_to_screen(ex * TILE_SIZE, ey * TILE_SIZE)
                draw_prop(surface, "gate_open" if self.exit_unlocked else "gate_closed", gsx, gsy)

        for item in self.chapter.items:
            if item.collected: continue
            if self.camera.is_visible(item.grid_pos[0]*TILE_SIZE, item.grid_pos[1]*TILE_SIZE):
                sx, sy = self.camera.world_to_screen(item.grid_pos[0]*TILE_SIZE, item.grid_pos[1]*TILE_SIZE)
                
                # Fade logic
                alpha = 255
                if item.timer > 0:
                    alpha = int(255 * (item.timer / item.max_timer))
                
                # Bobbing animation for loot
                bob = int(math.sin(pygame.time.get_ticks() * 0.01 + item.grid_pos[0] * 10) * 4)
                sy += bob

                mission_types = {"keycard", "power", "code", "antidote", "exit", "exit_key", "gate", "signal"}
                is_mission = item.item_type in mission_types
                if is_mission or item.item_type == "weapon_drop" or item.item_type == "material":
                    pulse = 10 + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 6)
                    # Unique color for Shadow Fragments
                    ring_col = (180, 0, 255) if item.item_type == "material" else (255, 220, 80) if is_mission else item.color
                    # Handle alpha for circles
                    if alpha < 255:
                        s = pygame.Surface((pulse*2+4, pulse*2+4), pygame.SRCALPHA)
                        pygame.draw.circle(s, (*ring_col, alpha), (pulse+2, pulse+2), pulse, 2)
                        surface.blit(s, (sx + 8 - (pulse+2), sy + 8 - (pulse+2)))
                    else:
                        pygame.draw.circle(surface, ring_col, (sx + 8, sy + 8), pulse, 2)
                    
                    # Name label
                    label_col = (200, 100, 255) if item.item_type == "material" else YELLOW if is_mission else item.color
                    label = self.font_small.render(item.name, True, label_col)
                    if alpha < 255: label.set_alpha(alpha)
                    surface.blit(label, (sx - 4, sy - 14))
                
                sprite = item.sprite_surface
                if not sprite:
                    sprite = ITEM_SURFACES.get(item.item_type)
                
                if sprite:
                    if item.item_type == "material":
                        # Tint material purple
                        sprite = sprite.copy()
                        sprite.fill((200, 100, 255), special_flags=pygame.BLEND_RGB_MULT)
                    
                    if alpha < 255:
                        sprite = sprite.copy()
                        sprite.set_alpha(alpha)
                    surface.blit(sprite, (sx, sy))
                else:
                    if alpha < 255:
                        s = pygame.Surface((16, 16), pygame.SRCALPHA)
                        pygame.draw.circle(s, (*item.color, alpha), (8, 8), 6)
                        surface.blit(s, (sx, sy))
                    else:
                        pygame.draw.circle(surface, item.color, (sx+8, sy+8), 6)
                    
        for npc in self.chapter.npcs:
            if self.camera.is_visible(npc.grid_pos[0]*TILE_SIZE, npc.grid_pos[1]*TILE_SIZE):
                sx, sy = self.camera.world_to_screen(npc.grid_pos[0]*TILE_SIZE + 8, npc.grid_pos[1]*TILE_SIZE + 8)
                color = GRAY if npc.interacted else npc.color
                
                # Use sprite if available
                if npc.sprite_path and npc.sprite_path in ALL_GRAPHICS_SURFACES:
                    sprite = ALL_GRAPHICS_SURFACES[npc.sprite_path]
                    surface.blit(sprite, sprite.get_rect(center=(sx, sy)))
                elif npc.sprite_path and os.path.exists(npc.sprite_path):
                    # Load dynamically if not in ALL_GRAPHICS
                    sprite = pygame.image.load(npc.sprite_path).convert_alpha()
                    ALL_GRAPHICS_SURFACES[npc.sprite_path] = sprite
                    surface.blit(sprite, sprite.get_rect(center=(sx, sy)))
                else:
                    pygame.draw.circle(surface, color, (sx, sy), 7)
                    pygame.draw.circle(surface, WHITE, (sx, sy), 7, 1)

        for entry in self.story_enemies:
            if self.camera.is_visible(entry.enemy.x, entry.enemy.y):
                sx, sy = self.camera.world_to_screen(entry.enemy.x, entry.enemy.y)
                self.draw_shadow(surface, sx, sy + 20)
                sprite = entry.enemy.frames[entry.enemy.current_action][entry.enemy.current_frame]
                if not entry.enemy.look_right:
                    sprite = pygame.transform.flip(sprite, True, False)
                rect = sprite.get_rect(center=(sx, sy))
                surface.blit(sprite, rect.topleft)

        self.draw_pet_companion(surface)
        psx, psy = self.camera.world_to_screen(self.player.x, self.player.y)
        self.draw_shadow(surface, psx, psy + 24, width=48)
        self.weapon_manager.draw(surface, self.camera)
        
        sprite = self.player.frames[self.player.direction][self.player.current_frame]
        rect = sprite.get_rect(center=(psx, psy))
        surface.blit(sprite, rect.topleft)

        # Ammo text above player
        w = self.weapon_manager.current_weapon
        if w and not getattr(w, "melee", False):
            ammo_text = f"{getattr(w, 'ammo_in_mag', 0)}/{getattr(w, 'reserve_ammo', 0)}"
            label = self.font_small.render(ammo_text, True, YELLOW)
            surface.blit(label, (psx - label.get_width() // 2, psy - 64))
        
        # Draw Particles
        for p in self.particles:
            sx, sy = self.camera.world_to_screen(p.x, p.y)
            pygame.draw.circle(surface, p.color, (sx, sy), p.size)
        
        # 5. Objective Marker
        goal = self.objective_tile()
        if goal:
            gsx, gsy = self.camera.world_to_screen(goal[0]*TILE_SIZE + 8, goal[1]*TILE_SIZE + 8)
            pulse = 10 + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 8)
            pygame.draw.circle(surface, YELLOW, (gsx, gsy), pulse, 2)
            pygame.draw.circle(surface, WHITE, (gsx, gsy), 4)
            
        # Draw Combo Texts
        for ct in self.combo_texts:
            sx, sy = self.camera.world_to_screen(ct.x, ct.y)
            alpha = int(255 * (ct.life / ct.max_life))
            font = self.font if ct.size <= 24 else self.font_big
            lines = ct.text.split("\n")
            for i, line in enumerate(lines):
                txt_surf = font.render(line, True, ct.color)
                txt_surf.set_alpha(alpha)
                surface.blit(txt_surf, (sx - txt_surf.get_width() // 2, sy - txt_surf.get_height() // 2 + i * 25))
            
        self.draw_world_fx(surface)

    def draw_world_props(self, surface):
        pass

    def draw_pet_companion(self, surface):
        if self.current_pet_instance:
            self.current_pet_instance.draw(surface, self.camera)

    def apply_pet_effects(self):
        """Apply current pet's attributes to player and game stats."""
        # Reset defaults (assuming base values)
        self.player.speed = 5
        self.player.max_health = 300
        # self.player.health = min(self.player.health, self.player.max_health)
        
        if not self.current_pet_instance:
            return
            
        attr = self.current_pet_instance.attributes
        
        # Apply Speed
        if "speed_mult" in attr:
            self.player.speed *= attr["speed_mult"]
            
        # Apply Health
        if "max_health_add" in attr:
            self.player.max_health += attr["max_health_add"]
            self.player.health = min(self.player.health + attr["max_health_add"], self.player.max_health)
            
        # Armor add (initial)
        if "armor_add" in attr and getattr(self, "stats_start", 0) > pygame.time.get_ticks() - 1000:
            self.player.armor = max(self.player.armor, attr["armor_add"])

        # Other effects like damage_mult, fire_rate_mult, etc.
        # These need to be handled where damage/fire rate is calculated.
        # We can store them in player or weapon manager.
        self.player.damage_mult = attr.get("damage_mult", 1.0)
        self.player.fire_rate_mult = attr.get("fire_rate_mult", 1.0)
        self.player.money_mult = attr.get("money_mult", 1.0)
        self.player.regen = attr.get("regen", 0.0)

    def draw_chapter_backdrop(self, surface):
        if self.force_black_map_background:
            pygame.draw.rect(surface, BLACK, (0, 0, MAP_WIDTH, MAP_HEIGHT))
            return
        top = self.chapter.chapter_color
        for y in range(0, SCREEN_HEIGHT, 8):
            blend = y / SCREEN_HEIGHT
            c = [max(10, int(top[i] * 0.12 * (1-blend) + 15 * blend)) for i in range(3)]
            pygame.draw.rect(surface, tuple(c), (0, y, MAP_WIDTH, 8))

    def generate_chunk_walls(self, cx, cy):
        import random
        # Seed cố định dựa trên tọa độ chunk để map luôn nhất quán
        rng = random.Random(cx * 1000003 + cy * 999983 + 42)
        walls = set()
        # 40% khả năng có một bức tường rào trong chunk này
        if rng.random() < 0.4:
            is_horiz = rng.random() < 0.5
            start_x = cx * 20
            start_y = cy * 20
            # Vị trí khe hở (gap) để người chơi có thể đi qua
            gap_pos = rng.randint(2, 17)
            
            for i in range(20):
                # Để lại khe hở 2 ô
                if i in (gap_pos, gap_pos + 1): 
                    continue
                if is_horiz:
                    walls.add((start_x + i, start_y + 10))
                else:
                    walls.add((start_x + 10, start_y + i))
        return walls

    def draw_world_fx(self, surface):
        # Particles or weather effects
        now = pygame.time.get_ticks()
        for i in range(12):
            px = (now * (0.05 + i*0.01) + i * 200) % MAP_WIDTH
            py = (i * 100 + math.sin(now*0.002 + i)*30) % SCREEN_HEIGHT
            pygame.draw.circle(surface, (255, 255, 255, 20), (int(px), int(py)), 2)

    def draw_sidebar(self):
        panel_rect = pygame.Rect(MAP_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        for i in range(panel_rect.height):
            blend = i / panel_rect.height
            color = (
                int(18 + blend * 8),
                int(22 + blend * 10),
                int(30 + blend * 14),
            )
            pygame.draw.line(screen, color, (panel_rect.x, i), (panel_rect.right, i))
        pygame.draw.line(screen, self.chapter.chapter_color, (MAP_WIDTH + 1, 0), (MAP_WIDTH + 1, SCREEN_HEIGHT), 3)

        header_rect = pygame.Rect(MAP_WIDTH + 14, 14, SIDEBAR_WIDTH - 28, 84)
        self.draw_card(header_rect, self.chapter.chapter_color, title="Sân Thượng Cuối", subtitle=self.chapter.title)

        stat_rect = pygame.Rect(MAP_WIDTH + 14, 108, SIDEBAR_WIDTH - 28, 98)
        self.draw_card(stat_rect, RED)
        self.draw_bar(stat_rect.x + 16, stat_rect.y + 18, stat_rect.width - 32, 16, self.player.health, self.player.max_health, RED, "HP")
        self.draw_bar(stat_rect.x + 16, stat_rect.y + 48, stat_rect.width - 32, 16, self.player.armor, 100, CYAN, "ARM")
        weapon_card_pos = (stat_rect.right - 84, stat_rect.y - 6)
        weapon_card = self.current_weapon_card()
        screen.blit(CARD_BORDER, weapon_card_pos)
        screen.blit(weapon_card, (weapon_card_pos[0] + 3, weapon_card_pos[1] + 3))
        screen.blit(self.font_small.render(self.weapon_manager.current_weapon.name, True, WHITE), (stat_rect.x + 16, stat_rect.y + 72))

        objective_rect = pygame.Rect(MAP_WIDTH + 14, 216, SIDEBAR_WIDTH - 28, 86)
        self.draw_card(objective_rect, YELLOW, title=f"Gợi ý: {self.hint_modes[self.hint_mode_index]}", subtitle=self.objective_label())

        quest_rect = pygame.Rect(MAP_WIDTH + 14, 312, SIDEBAR_WIDTH - 28, 120)
        quest_title = "Quest"
        quest_sub = self.chapter.quest_line if getattr(self.chapter, "quest_line", "") else self.objective_label()
        self.draw_card(quest_rect, self.chapter.chapter_color, title=quest_title, subtitle=quest_sub)
        # Checkpoints
        yy = quest_rect.y + 56
        if self.mission:
            for text, done in self.mission.objectives()[:4]:
                mark = "[x]" if done else "[ ]"
                color = GREEN if done else SOFT
                line = self.font_small.render(f"{mark} {text}", True, color)
                screen.blit(line, (quest_rect.x + 14, yy))
                yy += 18

        minimap_frame = pygame.Rect(MAP_WIDTH + 14, 442, SIDEBAR_WIDTH - 28, 214)
        self.draw_card(minimap_frame, self.chapter.chapter_color, title="Minimap", subtitle="Mục tiêu và đường đi")
        minimap_rect = pygame.Rect(minimap_frame.x + 12, minimap_frame.y + 44, minimap_frame.width - 24, 152)
        self.draw_minimap(minimap_rect)

        info_rect = pygame.Rect(MAP_WIDTH + 14, 666, SIDEBAR_WIDTH - 28, 86)
        self.draw_card(info_rect, CYAN, title="Thông tin", subtitle=f"Zombie: {self.kill_count}  |  NPC: {self.saved_npcs}")
        y = info_rect.y + 48
        stats = [
            "Chuột trái bắn  |  E nhặt",
            "Q đổi súng  |  Tự động qua cổng",
            f"Thuật toán: {self.hint_modes[self.hint_mode_index]}",
        ]
        for line in stats:
            screen.blit(self.font_small.render(line, True, SOFT), (info_rect.x + 14, y))
            y += 18

        asset_rect = pygame.Rect(MAP_WIDTH + 14, 752, SIDEBAR_WIDTH - 28, 40)
        self.draw_card(asset_rect, ORANGE, title="Loadout & Hỗ trợ", subtitle="Card asset đang dùng")
        # (Cards hidden to make room for quest tracker)

    def draw_minimap(self, rect):
        pygame.draw.rect(screen, (8, 10, 14), rect, border_radius=10)
        pygame.draw.rect(screen, STROKE, rect, 1, border_radius=10)
        sx = rect.width / GRID_SIZE
        sy = rect.height / GRID_SIZE
        for x, y in self.current_blocked:
            pygame.draw.rect(screen, GRAY, (rect.x + x * sx, rect.y + y * sy, max(1, sx), max(1, sy)))
        for item in self.chapter.items:
            if not item.collected:
                pygame.draw.rect(screen, item.color, (rect.x + item.grid_pos[0] * sx, rect.y + item.grid_pos[1] * sy, max(2, sx), max(2, sy)))
        for npc in self.chapter.npcs:
            pygame.draw.circle(screen, npc.color, (int(rect.x + npc.grid_pos[0] * sx), int(rect.y + npc.grid_pos[1] * sy)), 2)
        for entry in self.story_enemies:
            if not entry.enemy.is_dead:
                ex, ey = entry.tile()
                pygame.draw.circle(screen, RED, (int(rect.x + ex * sx), int(rect.y + ey * sy)), 2)
        if self.exit_path:
            for tile in self.exit_path:
                pygame.draw.rect(screen, YELLOW, (rect.x + tile[0] * sx, rect.y + tile[1] * sy, max(1, sx), max(1, sy)), 1)
        px, py = self.current_tile()
        pygame.draw.circle(screen, WHITE, (int(rect.x + px * sx), int(rect.y + py * sy)), 3)

    def draw_bar(self, x, y, width, height, value, max_value, color, label):
        pygame.draw.rect(screen, (8, 10, 14), (x, y, width, height), border_radius=8)
        fill = 0 if max_value == 0 else int(width * max(0, value) / max_value)
        pygame.draw.rect(screen, color, (x, y, fill, height), border_radius=8)
        pygame.draw.rect(screen, STROKE, (x, y, width, height), 1, border_radius=8)
        screen.blit(self.font_small.render(f"{label} {int(value)}/{int(max_value)}", True, WHITE), (x + 8, y + 1))

    def current_weapon_card(self):
        name = self.weapon_manager.current_weapon.name.lower()
        if "shotgun" in name:
            return CARD_WEAPON_SHOTGUN
        if "rocket" in name:
            return CARD_WEAPON_ROCKET
        return CARD_WEAPON_BASIC

    def draw_card(self, rect, accent, title=None, subtitle=None):
        shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        pygame.draw.rect(shadow, (0, 0, 0, 55), shadow.get_rect(), border_radius=18)
        screen.blit(shadow, (rect.x + 3, rect.y + 5))
        pygame.draw.rect(screen, CARD, rect, border_radius=18)
        pygame.draw.rect(screen, STROKE, rect, 1, border_radius=18)
        pygame.draw.rect(screen, accent, (rect.x, rect.y, rect.width, 5), border_top_left_radius=18, border_top_right_radius=18)
        if title:
            screen.blit(self.font.render(title, True, WHITE), (rect.x + 14, rect.y + 12))
        if subtitle:
            wrapped = wrap_text(subtitle, self.font_small, rect.width - 28)
            yy = rect.y + 34
            for line in wrapped[:2]:
                screen.blit(self.font_small.render(line, True, SOFT), (rect.x + 14, yy))
                yy += 16

    def draw_overlays(self):
        if pygame.time.get_ticks() < self.objective_flash_until and not self.dialog_npc and not self.next_chapter_ready:
            flash_rect = pygame.Rect(24, 22, 320, 54)
            self.draw_card(flash_rect, YELLOW)
            title = "Màn khởi động" if self.chapter.id == "roof" else "Mục tiêu hiện tại"
            screen.blit(self.font_small.render(title, True, SOFT), (flash_rect.x + 14, flash_rect.y + 10))
            for i, line in enumerate(wrap_text(self.objective_label(), self.font, flash_rect.width - 28)[:2]):
                screen.blit(self.font.render(line, True, WHITE), (flash_rect.x + 14, flash_rect.y + 24 + i * 18))
        if self.chapter.id == "escape" and getattr(self, "countdown_started", False) and not getattr(self, "rescue_arrived", False):
            time_left = max(0, (self.holdout_until - pygame.time.get_ticks()) // 1000)
            mins = time_left // 60
            secs = time_left % 60
            timer_str = f"Trực thăng đến sau: {mins:02d}:{secs:02d}"
            timer_rect = pygame.Rect(MAP_WIDTH // 2 - 140, 24, 280, 50)
            self.draw_card(timer_rect, YELLOW)
            screen.blit(self.font_big.render(timer_str, True, YELLOW), (timer_rect.x + 16, timer_rect.y + 12))
        if pygame.time.get_ticks() < self.chapter_card_timer:
            card_rect = pygame.Rect(116, 72, 500, 132)
            self.draw_card(card_rect, self.chapter.chapter_color)
            screen.blit(self.font_big.render(self.chapter.title, True, self.chapter.chapter_color), (146, 104))
            screen.blit(self.font.render(self.chapter.subtitle, True, WHITE), (146, 144))
        if self.popup and pygame.time.get_ticks() < self.popup_timer:
            popup_rect = pygame.Rect(24, MAP_HEIGHT - 92, 560, 64)
            self.draw_card(popup_rect, self.chapter.chapter_color)
            yy = popup_rect.y + 12
            for line in wrap_text(self.popup, self.font, popup_rect.width - 28)[:2]:
                screen.blit(self.font.render(line, True, WHITE), (popup_rect.x + 14, yy))
                yy += 22
        nearby_npc = self.npc_near_player()
        nearby_item = self.item_at_player()
        
        # Priority: NPC > Item > Power Box
        if nearby_npc and not self.dialog_npc:
            hint_rect = pygame.Rect(24, MAP_HEIGHT - 118, 300, 32)
            pygame.draw.rect(screen, CARD_ALT, hint_rect, border_radius=10)
            pygame.draw.rect(screen, CYAN, hint_rect, 1, border_radius=10)
            screen.blit(self.font.render(f"Nhấn E để nói chuyện với {nearby_npc.name}", True, WHITE), (hint_rect.x + 10, hint_rect.y + 8))
        elif nearby_item and not self.dialog_npc:
            hint_rect = pygame.Rect(24, MAP_HEIGHT - 118, 300, 32)
            pygame.draw.rect(screen, CARD_ALT, hint_rect, border_radius=10)
            pygame.draw.rect(screen, ORANGE, hint_rect, 1, border_radius=10)
            screen.blit(self.font.render(f"Nhấn E để nhặt {nearby_item.name}", True, WHITE), (hint_rect.x + 10, hint_rect.y + 8))
        elif not self.dialog_npc:
            # Check for power boxes
            for bx, by in getattr(self, "power_boxes", []):
                pix_x = bx * TILE_SIZE + TILE_SIZE // 2
                pix_y = by * TILE_SIZE + TILE_SIZE // 2
                if math.hypot(pix_x - self.player.x, pix_y - self.player.y) <= INTERACT_RADIUS:
                    hint_rect = pygame.Rect(24, MAP_HEIGHT - 118, 300, 32)
                    pygame.draw.rect(screen, CARD_ALT, hint_rect, border_radius=10)
                    pygame.draw.rect(screen, YELLOW, hint_rect, 1, border_radius=10)
                    screen.blit(self.font.render("Nhấn E để kích hoạt thiết bị", True, WHITE), (hint_rect.x + 10, hint_rect.y + 8))
                    break
        if self.next_chapter_ready and not self.dialog_npc:
            ready_rect = pygame.Rect(138, 18, 448, 82)
            self.draw_card(ready_rect, YELLOW)
            if self.chapter.id == "roof":
                title = "Xong màn khởi động"
                text = "Nhấn ENTER để bắt đầu Chương 2"
            else:
                title = "Qua màn"
                text = "Nhấn ENTER để sang màn tiếp theo" if self.chapter_index < len(self.chapters) - 1 else "Nhấn ENTER để kết thúc và lên trực thăng"
            screen.blit(self.font_big.render(title, True, YELLOW), (ready_rect.x + 16, ready_rect.y + 8))
            for i, line in enumerate(wrap_text(text, self.font, ready_rect.width - 28)[:2]):
                screen.blit(self.font.render(line, True, WHITE), (ready_rect.x + 18, ready_rect.y + 40 + i * 18))
        if self.dialog_npc:
            self.draw_dialog()
        if self.show_map:
            self.draw_full_map()
        
        self.draw_combo_ui(screen)

    def draw_combo_ui(self, surface):
        """Draw high-fidelity persistent Combo Meter on the left."""
        if self.combo_counter < 2:
            return
            
        x, y = 30, 220
        now = pygame.time.get_ticks()
        
        # Shake effect on milestone
        shake_x = 0
        if now < getattr(self, "combo_shake_until", 0):
            shake_x = random.randint(-8, 8)
            
        # Background Pulse Glow / Fire Effect
        glow_alpha = 120 + int(math.sin(now * 0.01) * 40)
        if self.combo_counter >= 15:
            glow_col = (255, 60, 0, glow_alpha)
        elif self.combo_counter >= 5:
            glow_col = (255, 150, 0, glow_alpha)
        else:
            glow_col = (200, 200, 220, glow_alpha)
        
        glow_width = 160 + min(self.combo_counter * 4, 100)
        glow_surf = pygame.Surface((glow_width, 110), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, glow_col, (0, 0, glow_width, 110))
        
        # Add dynamic "sparks" for high combo
        if self.combo_counter >= 10:
            for _ in range(int(self.combo_counter / 5)):
                sx_pos = random.randint(0, glow_width)
                sy_pos = random.randint(0, 110)
                pygame.draw.circle(glow_surf, (255, 220, 100, 150), (sx_pos, sy_pos), random.randint(2, 6))
                
        surface.blit(glow_surf, (x - 40 + shake_x, y - 30))
        
        # Combo Count Text (X15)
        combo_str = f"X{self.combo_counter}"
        font = self.font_title if self.combo_counter >= 10 else self.font_big
        
        # Premium Stroke / Shadow
        stroke_col = (30, 5, 0)
        for dx, dy in [(-3,-3), (3,-3), (-3,3), (3,3), (0, 4)]:
            surface.blit(font.render(combo_str, True, stroke_col), (x + dx + shake_x, y + dy))
            
        # Pulsing Main Text Color
        if self.combo_counter >= 20:
            # Fire cycle
            t = (now // 100) % 3
            main_col = [RED, ORANGE, YELLOW][t]
        elif self.combo_counter >= 10:
            main_col = ORANGE
        else:
            main_col = WHITE
            
        txt_surf = font.render(combo_str, True, main_col)
        surface.blit(txt_surf, (x + shake_x, y))
        
        # Progress Bar (Timer)
        time_left = max(0, self.frenzy_window_until - now)
        bar_w = 140
        fill_w = int(bar_w * (time_left / 3000))
        
        # Bar Container
        pygame.draw.rect(surface, (10, 10, 15, 200), (x, y + 85, bar_w, 12), border_radius=6)
        pygame.draw.rect(surface, (60, 60, 70), (x, y + 85, bar_w, 12), 2, border_radius=6)
        
        # Animated Fill
        if fill_w > 0:
            fill_col = RED if time_left < 1000 else ORANGE if self.combo_counter >= 10 else BLUE
            pygame.draw.rect(surface, fill_col, (x + 2, y + 87, fill_w - 4, 8), border_radius=4)
            # Add a "shine" to the bar
            if fill_w > 10:
                pygame.draw.rect(surface, (255, 255, 255, 100), (x + 2, y + 87, fill_w - 4, 3), border_radius=2)
            
        # Label
        label_txt = "FRENZY STATUS" if self.combo_counter >= 3 else "COMBO WINDOW"
        label_col = RED if self.combo_counter >= 10 else YELLOW if self.combo_counter >= 3 else SOFT
        surface.blit(self.font_small.render(label_txt, True, label_col), (x + 2, y + 100))

    def draw_dialog(self):
        # Genshin-like cinematic dialog box
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 12, 110))
        screen.blit(overlay, (0, 0))

        dialog_rect = pygame.Rect(48, SCREEN_HEIGHT - 210, SCREEN_WIDTH - 96, 168)
        panel = pygame.Surface((dialog_rect.width, dialog_rect.height), pygame.SRCALPHA)
        panel.fill((22, 22, 28, 210))
        screen.blit(panel, dialog_rect.topleft)
        pygame.draw.rect(screen, (255, 255, 255, 60), dialog_rect, 2, border_radius=18)

        # Portrait + speaker
        portrait_center = (dialog_rect.x + 70, dialog_rect.y + 64)
        pygame.draw.circle(screen, self.dialog_color, portrait_center, 30)
        pygame.draw.circle(screen, WHITE, portrait_center, 30, 2)
        screen.blit(self.font_big.render(self.dialog_speaker, True, self.dialog_color), (dialog_rect.x + 115, dialog_rect.y + 18))

        # Typewriter text
        pages = []
        for raw in (self.dialog_lines or [""]):
            pages.extend(wrap_text(raw, self.font, dialog_rect.width - 150))
        if not pages:
            pages = [""]
        page = pages[max(0, min(self.dialog_page_index, len(pages) - 1))]

        now = pygame.time.get_ticks()
        elapsed = max(0, now - getattr(self, "dialog_started_at", now))
        max_chars = int((elapsed / 1000.0) * float(getattr(self, "dialog_speed_cps", 70)))
        shown = page[:max_chars]
        screen.blit(self.font.render(shown, True, WHITE), (dialog_rect.x + 115, dialog_rect.y + 70))

        # Hint
        hint = "SPACE/ENTER để tiếp tục"
        screen.blit(self.font_small.render(hint, True, (220, 220, 230)), (dialog_rect.right - 260, dialog_rect.bottom - 32))

    def draw_full_map(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        screen.blit(overlay, (0, 0))
        rect = pygame.Rect(120, 60, 520, 520)
        pygame.draw.rect(screen, PANEL, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        scale = rect.width / GRID_SIZE
        for x, y in self.current_blocked:
            pygame.draw.rect(screen, GRAY, (rect.x + x * scale, rect.y + y * scale, scale, scale))
        for item in self.chapter.items:
            if not item.collected:
                pygame.draw.rect(screen, item.color, (rect.x + item.grid_pos[0] * scale, rect.y + item.grid_pos[1] * scale, scale, scale))
        for npc in self.chapter.npcs:
            pygame.draw.circle(screen, CYAN, (int(rect.x + npc.grid_pos[0] * scale), int(rect.y + npc.grid_pos[1] * scale)), 4)
        for tile in self.exit_path:
            pygame.draw.rect(screen, YELLOW, (rect.x + tile[0] * scale, rect.y + tile[1] * scale, scale, scale), 1)
        px, py = self.current_tile()
        pygame.draw.circle(screen, WHITE, (int(rect.x + px * scale), int(rect.y + py * scale)), 5)
        screen.blit(self.font_big.render("Bản Đồ Chiến Thuật", True, WHITE), (rect.x + 18, rect.y - 34))

    def draw_menu(self):
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(screen, (28, 30, 40), (0, y), (SCREEN_WIDTH, y), 1)
        shadow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shadow.fill((10, 8, 12, 180))
        screen.blit(shadow, (0, 0))
        screen.blit(self.font_title.render("LAST ROOF", True, WHITE), (120, 110))
        screen.blit(self.font_big.render("Escape City", True, ORANGE), (124, 164))
        menu_lines = [
            "ENTER  Xem trailer và bắt đầu",
            "H      Hướng dẫn chơi",
            "<- ->  Chọn map",
            "ESC    Thoát",
        ]
        y = 280
        for line in menu_lines:
            screen.blit(self.font_big.render(line, True, WHITE), (126, y))
            y += 44
        teaser = [
            "Sinh tồn 2D theo chương, có NPC và hệ gợi ý đường đi.",
            "Bấm TAB trong game để đổi BFS / DFS / SAFE / A*.",
            "Tiếng Việt có dấu: ă â ê ô ơ ư đ.",
        ]
        y = 500
        for line in teaser:
            screen.blit(self.font.render(line, True, WHITE), (126, y))
            y += 28

        map_rect = pygame.Rect(520, 390, 560, 330)
        pygame.draw.rect(screen, PANEL, map_rect)
        pygame.draw.rect(screen, ORANGE, map_rect, 2)
        screen.blit(self.font_big.render("Map Selector", True, ORANGE), (map_rect.x + 18, map_rect.y + 16))
        screen.blit(self.font_small.render(f"Map đang chọn: {self.selected_map_name}", True, WHITE), (map_rect.x + 18, map_rect.y + 66))
        screen.blit(self.font_small.render("Phím mũi tên trái/phải để đổi map", True, SOFT), (map_rect.x + 18, map_rect.y + 88))

        list_top = map_rect.y + 118
        total = len(self.map_assets)
        start = max(0, min(self.selected_map_index - 2, max(0, total - 5)))
        for idx in range(start, min(total, start + 5)):
            path = self.map_assets[idx]
            name = "Default Tilemap" if path is None else os.path.splitext(os.path.basename(path))[0]
            color = YELLOW if idx == self.selected_map_index else WHITE
            prefix = ">" if idx == self.selected_map_index else " "
            screen.blit(self.font_small.render(f"{prefix} {name}", True, color), (map_rect.x + 18, list_top))
            list_top += 28

        if self.map_background_surface is not None:
            preview = pygame.transform.smoothscale(self.map_background_surface, (240, 140))
            preview_rect = pygame.Rect(map_rect.right - 258, map_rect.y + 160, 240, 140)
            screen.blit(preview, preview_rect.topleft)
            pygame.draw.rect(screen, WHITE, preview_rect, 1)
        if self.show_help:
            help_rect = pygame.Rect(520, 100, 330, 280)
            pygame.draw.rect(screen, PANEL, help_rect)
            pygame.draw.rect(screen, CYAN, help_rect, 2)
            lines = [
                "WASD: Di chuyển",
                "E: Tương tác / nhặt đồ",
                "Q / Lăn chuột: Đổi súng",
                "1-2-3: Chọn nhanh súng",
                "B: Mở shop vật phẩm",
                "TAB: Đổi thuật toán tìm đường",
                "M: Mở minimap lớn",
                "ESC: Tạm dừng",
                "Mục tiêu mỗi chương ở bảng bên phải",
            ]
            yy = help_rect.y + 26
            for line in lines:
                screen.blit(self.font.render(line, True, WHITE), (help_rect.x + 18, yy))
                yy += 32

    def draw_intro(self):
        scenes = self.trailer_scenes()
        elapsed = pygame.time.get_ticks() - self.trailer_started_at
        scene_duration = 3000
        scene_index = min(len(scenes) - 1, elapsed // scene_duration)
        scene = scenes[scene_index]

        self.draw_trailer_scene(scene, elapsed % scene_duration)

        progress_width = 360
        pygame.draw.rect(screen, (32, 36, 46), (90, 612, progress_width, 8), border_radius=4)
        fill = int(progress_width * min(1, elapsed / (scene_duration * len(scenes))))
        pygame.draw.rect(screen, scene["accent"], (90, 612, fill, 8), border_radius=4)
        screen.blit(self.font.render("ENTER de bo qua trailer", True, WHITE), (90, 580))
        screen.blit(self.font.render(f"Canh {scene_index + 1}/{len(scenes)}", True, WHITE), (470, 606))

        if elapsed >= scene_duration * len(scenes):
            self.state = "playing"

    def draw_trailer_scene(self, scene, local_elapsed):
        screen.fill((8, 10, 14))
        for y in range(SCREEN_HEIGHT):
            blend = y / SCREEN_HEIGHT
            color = (
                int(10 + scene["accent"][0] * 0.08 + 10 * blend),
                int(10 + scene["accent"][1] * 0.05 + 14 * blend),
                int(16 + scene["accent"][2] * 0.06 + 20 * blend),
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        offset = int((1 - min(1, local_elapsed / 900)) * 80)
        title_shadow = self.font_title.render(scene["title"], True, BLACK)
        screen.blit(title_shadow, (92, 82))
        screen.blit(self.font_title.render(scene["title"], True, WHITE), (88, 78))
        screen.blit(self.font_big.render(scene["subtitle"], True, WHITE), (92, 152))

        for idx, art in enumerate(scene["art"]):
            key, x, y = art
            bob = int(math.sin((pygame.time.get_ticks() * 0.004) + idx) * 8)
            self.draw_trailer_art(key, x, y + bob + offset)

        panel = pygame.Surface((520, 150), pygame.SRCALPHA)
        panel.fill((10, 12, 18, 170))
        screen.blit(panel, (74, 420))
        pygame.draw.rect(screen, scene["accent"], (74, 420, 520, 150), 2, border_radius=12)
        lines = self.chapter.intro_lines
        yy = 448
        for line in lines[:2]:
            screen.blit(self.font.render(line, True, WHITE), (96, yy))
            yy += 34

    def draw_trailer_art(self, key, x, y):
        """Draw specific art assets for the trailer sequence."""
        if key == "player":
            screen.blit(PLAYER_TRAILER, PLAYER_TRAILER.get_rect(center=(x, y)))
        elif key == "goblin":
            screen.blit(GOBLIN_TRAILER, GOBLIN_TRAILER.get_rect(center=(x, y)))
        elif key == "eye":
            screen.blit(EYE_TRAILER, EYE_TRAILER.get_rect(center=(x, y)))
        elif key == "mushroom":
            screen.blit(MUSHROOM_TRAILER, MUSHROOM_TRAILER.get_rect(center=(x, y)))
        elif key == "rocket":
            rocket = pygame.transform.rotate(ROCKET_LAUNCHER_TRAILER, -18)
            screen.blit(rocket, rocket.get_rect(center=(x, y)))
        elif key == "mortar":
            screen.blit(MORTAR_TRAILER, MORTAR_TRAILER.get_rect(center=(x, y)))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 12, 190))
        screen.blit(overlay, (0, 0))

        # Panel
        w, h = 520, 420
        panel = pygame.Rect((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h)
        self.draw_card(panel, YELLOW, title="TẠM DỪNG", subtitle="Chọn hành động")

        def draw_btn(rect: pygame.Rect, label: str, accent: tuple[int, int, int]):
            pygame.draw.rect(screen, CARD_ALT, rect, border_radius=14)
            pygame.draw.rect(screen, accent, rect, 2, border_radius=14)
            pygame.draw.rect(screen, accent, (rect.x, rect.y, rect.width, 4), border_top_left_radius=14, border_top_right_radius=14)
            txt = self.font_big.render(label, True, WHITE)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # Buttons
        bx = panel.x + 60
        by = panel.y + 120
        bw = panel.width - 120
        bh = 74
        gap = 22
        btn_continue = pygame.Rect(bx, by, bw, bh)
        btn_menu = pygame.Rect(bx, by + (bh + gap), bw, bh)
        btn_quit = pygame.Rect(bx, by + 2 * (bh + gap), bw, bh)
        draw_btn(btn_continue, "TIẾP TỤC", GREEN)
        draw_btn(btn_menu, "VỀ MENU", CYAN)
        draw_btn(btn_quit, "THOÁT GAME", RED)

        hint = "ESC: tiếp tục | Click nút để chọn"
        screen.blit(self.font_small.render(hint, True, SOFT), (panel.x + 60, panel.bottom - 54))

        # Store for click handling
        self.pause_buttons = {
            "continue": btn_continue,
            "menu": btn_menu,
            "quit": btn_quit,
        }

    def draw_end_screen(self):
        screen.fill((10, 10, 14))
        title = "THOÁT THÀNH CÔNG" if self.state == "win" else "THẤT BẠI"
        color = GREEN if self.state == "win" else RED
        screen.blit(self.font_title.render(title, True, color), (110, 110))
        screen.blit(self.font.render(self.end_reason, True, WHITE), (110, 190))
        screen.blit(self.font_big.render("Nhấn ENTER để chơi lại", True, YELLOW), (110, SCREEN_HEIGHT - 100))

    def draw_npc_portrait(self, x, y, color):
        """Draw a custom-made NPC portrait using shapes."""
        rect = pygame.Rect(x, y, 64, 64)
        pygame.draw.rect(screen, (30, 30, 45), rect, border_radius=8)
        pygame.draw.rect(screen, color, rect, 2, border_radius=8)
        # Face
        pygame.draw.circle(screen, (240, 200, 160), (x+32, y+35), 20)
        # Hair/Hat based on color
        pygame.draw.rect(screen, color, (x+12, y+10, 40, 15), border_top_left_radius=10, border_top_right_radius=10)
        # Eyes
        pygame.draw.circle(screen, BLACK, (x+25, y+32), 2)
        pygame.draw.circle(screen, BLACK, (x+39, y+32), 2)
        # Mouth
        pygame.draw.arc(screen, BLACK, (x+22, y+38, 20, 10), 3.14, 0, 2)

    def draw_sidebar(self):
        panel_rect = pygame.Rect(MAP_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        for i in range(panel_rect.height):
            blend = i / panel_rect.height
            color = (int(18 + blend * 8), int(22 + blend * 10), int(30 + blend * 14))
            pygame.draw.line(screen, color, (panel_rect.x, i), (panel_rect.right, i))
        pygame.draw.line(screen, self.chapter.chapter_color, (MAP_WIDTH + 1, 0), (MAP_WIDTH + 1, SCREEN_HEIGHT), 3)

        # Header
        header_rect = pygame.Rect(MAP_WIDTH + 14, 14, SIDEBAR_WIDTH - 28, 84)
        self.draw_card(header_rect, self.chapter.chapter_color, title="LAST ROOF", subtitle=self.chapter.title)

        # Stats
        stat_rect = pygame.Rect(MAP_WIDTH + 14, 108, SIDEBAR_WIDTH - 28, 140)
        self.draw_card(stat_rect, RED)
        self.draw_bar(stat_rect.x + 16, stat_rect.y + 18, stat_rect.width - 32, 16, self.player.health, self.player.max_health, RED, "HP")
        self.draw_bar(stat_rect.x + 16, stat_rect.y + 48, stat_rect.width - 32, 16, self.player.armor, 100, CYAN, "ARM")
        self.draw_bar(stat_rect.x + 16, stat_rect.y + 78, stat_rect.width - 32, 16, self.player.stamina, self.player.max_stamina, YELLOW, "STM")
        
        # Current Weapon
        weapon_name = self.weapon_manager.current_weapon.name
        screen.blit(self.font_small.render(f"Weapon: {weapon_name}", True, WHITE), (stat_rect.x + 16, stat_rect.y + 110))

        # Skills
        skill_rect = pygame.Rect(MAP_WIDTH + 14, 258, SIDEBAR_WIDTH - 28, 120)
        self.draw_card(skill_rect, BLUE, title="Skills [4-6]")
        for i, skill in enumerate(self.skill_manager.skills):
            sx = skill_rect.x + 16 + i * 70
            sy = skill_rect.y + 44
            screen.blit(skill.icon, (sx, sy))
            if not skill.can_use():
                cd_ratio = 1 - (pygame.time.get_ticks() - skill.last_used) / skill.cooldown
                pygame.draw.rect(screen, (0, 0, 0, 150), (sx, sy, 48, 48 * cd_ratio))
            pygame.draw.rect(screen, WHITE, (sx, sy, 48, 48), 1)

        # Minimap
        minimap_frame = pygame.Rect(MAP_WIDTH + 14, 390, SIDEBAR_WIDTH - 28, 200)
        self.draw_card(minimap_frame, self.chapter.chapter_color, title="Tactical Map")
        self.draw_minimap(pygame.Rect(minimap_frame.x + 12, minimap_frame.y + 40, minimap_frame.width - 24, 140))

        # Info
        info_rect = pygame.Rect(MAP_WIDTH + 14, 600, SIDEBAR_WIDTH - 28, 180)
        self.draw_card(info_rect, CYAN, title="Control & Stats")
        y = info_rect.y + 40
        lines = [
            f"Kills: {self.kill_count}", f"Saved: {self.saved_npcs}",
            f"Money: {self.money}",
            "B: Open Shop", "TAB: Path Mode", "M: Full Map"
        ]
        for line in lines:
            screen.blit(self.font_small.render(line, True, SOFT), (info_rect.x + 14, y))
            y += 22

    def draw_shop(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 12, 220))
        screen.blit(overlay, (0, 0))
        
        shop_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, PANEL, shop_rect, border_radius=20)
        pygame.draw.rect(screen, WHITE, shop_rect, 2, border_radius=20)
        
        screen.blit(self.font_title.render("SURVIVOR SHOP", True, YELLOW), (shop_rect.x + 40, shop_rect.y + 30))
        screen.blit(self.font.render("Press B to close", True, WHITE), (shop_rect.right - 200, shop_rect.y + 40))
        screen.blit(self.font_big.render(f"Money: {self.money}", True, YELLOW), (shop_rect.right - 260, shop_rect.y + 84))
        
        # Curated shop inventory (each costs 1 money)
        self.shop_items = [
            ("heal", "Medkit +25", "Heal 25 HP"),
            ("armor", "Armor +15", "Gain 15 armor"),
            ("ammo", "Ammo +30", "Add 30 reserve ammo"),
            ("weapon_pistol", "Pistol", "Buy 1 Pistol"),
            ("weapon_minigun", "Minigun", "Buy 1 Minigun"),
            ("weapon_flamethrower", "FlameThrower", "Buy 1 FlameThrower"),
            ("weapon_grenadelauncher", "GrenadeLauncher", "Buy 1 GrenadeLauncher"),
            ("weapon_poisongun", "PoisonGun", "Buy 1 PoisonGun"),
            ("weapon_taesar", "Taesar Gun", "Buy 1 Taesar"),
            ("pet_blue_bird", "Blue Bird", "Pet: +15% Tốc độ"),
            ("pet_cat_gray", "Gray Cat", "Pet: +50 HP & Regen"),
            ("pet_cat_orange", "Orange Cat", "Pet: +20% Damage"),
            ("pet_eagle", "Eagle", "Pet: +15% Fire Rate"),
            ("pet_fox", "Fox", "Pet: +25 Giáp"),
            ("pet_racoon", "Racoon", "Pet: +50% Tiền"),
        ]
        weapon_cards = {
            "weapon_pistol": CARD_WEAPON_PISTOL,
            "weapon_minigun": CARD_WEAPON_MINIGUN,
            "weapon_flamethrower": CARD_WEAPON_FLAMETHROWER,
            "weapon_grenadelauncher": CARD_WEAPON_GRENADE,
            "weapon_poisongun": CARD_WEAPON_POISON,
            "weapon_taesar": CARD_WEAPON_TAESAR,
            "pet_blue_bird": CARD_PET_BIRD,
            "pet_cat_gray": CARD_PET_GRAY_CAT,
            "pet_cat_orange": CARD_PET_ORANGE_CAT,
            "pet_eagle": CARD_PET_EAGLE,
            "pet_fox": CARD_PET_FOX,
            "pet_racoon": CARD_PET_RACOON,
        }
        for i, (sid, title, desc) in enumerate(self.shop_items):
            r, c = i // 3, i % 3
            cx = shop_rect.x + 40 + c * 320
            cy = shop_rect.y + 140 + r * 135
            card_rect = pygame.Rect(cx, cy, 290, 115)
            pygame.draw.rect(screen, CARD, card_rect, border_radius=16)
            pygame.draw.rect(screen, STROKE, card_rect, 1, border_radius=16)
            pygame.draw.rect(screen, YELLOW, (card_rect.x, card_rect.y, card_rect.width, 4), border_top_left_radius=16, border_top_right_radius=16)
            # show Shop_Cards for weapon categories
            card = weapon_cards.get(sid)
            if card:
                screen.blit(card, (card_rect.x + 10, card_rect.y + 10))
                tx = card_rect.x + 10 + 72 + 12
            else:
                tx = card_rect.x + 14
                icon = ITEM_SURFACES.get("heal" if sid == "heal" else "armor" if sid == "armor" else "ammo")
                if icon:
                    screen.blit(icon, (card_rect.right - 44, card_rect.y + 14))
            screen.blit(self.font_big.render(title, True, WHITE), (tx, card_rect.y + 14))
            screen.blit(self.font.render(desc, True, SOFT), (tx, card_rect.y + 56))
            screen.blit(self.font.render("Price: 1", True, YELLOW), (tx, card_rect.y + 86))

    def handle_shop_click(self, mx, my):
        if not hasattr(self, "shop_items"):
            return
        shop_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        for i, (sid, title, desc) in enumerate(self.shop_items):
            r, c = i // 3, i % 3
            cx = shop_rect.x + 40 + c * 320
            cy = shop_rect.y + 140 + r * 135
            card_rect = pygame.Rect(cx, cy, 290, 115)
            if card_rect.collidepoint(mx, my):
                if self.money < 1:
                    self.popup = "Không đủ tiền."
                    self.popup_timer = pygame.time.get_ticks() + 1200
                    return
                self.money -= 1
                if sid == "heal":
                    self.player.heal(25)
                elif sid == "armor":
                    self.player.add_armor(15)
                elif sid == "ammo":
                    w = self.weapon_manager.current_weapon
                    if w and not getattr(w, "melee", False):
                        w.reserve_ammo += 30
                elif sid.startswith("weapon_"):
                    # Filter big pool by type
                    want = sid.replace("weapon_", "")
                    alias = {
                        "grenadelauncher": "grenade_launcher",
                        "poisongun": "poison",
                    }
                    want = alias.get(want, want)
                    candidates = [w for w in WEAPON_DROP_POOL if w.get("type") == want]
                    if not candidates:
                        candidates = WEAPON_DROP_POOL
                    data = dict(random.choice(candidates))
                    self.unlock_weapon(data, equip_now=True)
                elif sid.startswith("pet_"):
                    pet_id = sid.replace("pet_", "")
                    if pet_id not in self.unlocked_pets:
                        self.unlocked_pets.append(pet_id)
                        self.popup = f"Đã mua Pet: {title}"
                    else:
                        self.popup = f"Đã trang bị Pet: {title}"
                    
                    self.current_pet_id = pet_id
                    self.current_pet_instance = self.all_pets[pet_id]
                    self.apply_pet_effects()
                
                self.popup_timer = pygame.time.get_ticks() + 1400
                sound_manager.play("nhat_do")
                return
            
    def draw(self):
        screen.fill(BLACK)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "intro":
            self.draw_intro()
        elif self.state in ["playing", "pause"]:
            self.render_world(screen)
            self.draw_sidebar()
            self.draw_overlays()
            if self.show_shop:
                self.draw_shop()
            if self.state == "pause":
                self.draw_pause()
        elif self.state in ["win", "lose"]:
            self.draw_end_screen()
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    sound_manager.play("nut_bam")
                    self.trailer_started_at = pygame.time.get_ticks()
                    self.state = "intro"
                    # Bắt đầu phát nhạc chương 1 khi vào trailer/game
                    if self.chapters:
                        sound_manager.play_music(f"nhac_nen_{self.chapters[0].id}")
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    self.set_map_background_by_index(self.selected_map_index - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    self.set_map_background_by_index(self.selected_map_index + 1)
                elif event.key == pygame.K_h:
                    sound_manager.play("nut_bam")
                    self.show_help = not self.show_help
            return

        if self.state == "intro":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "playing"
            return

        if self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if self.dialog_npc:
                    if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                        # Finish typing current page, then next page, then next queue entry
                        pages = []
                        for raw in (self.dialog_lines or [""]):
                            pages.extend(wrap_text(raw, self.font, (SCREEN_WIDTH - 96) - 150))
                        if not pages:
                            pages = [""]
                        page = pages[max(0, min(self.dialog_page_index, len(pages) - 1))]
                        now = pygame.time.get_ticks()
                        elapsed = max(0, now - getattr(self, "dialog_started_at", now))
                        max_chars = int((elapsed / 1000.0) * float(getattr(self, "dialog_speed_cps", 70)))
                        if max_chars < len(page):
                            # fast-forward typewriter
                            self.dialog_started_at = now - int((len(page) / float(getattr(self, "dialog_speed_cps", 70))) * 1000)
                        else:
                            if self.dialog_page_index < len(pages) - 1:
                                self.dialog_page_index += 1
                                self.dialog_started_at = now
                            else:
                                self.dialog_npc = None
                                self.dialog_page_index = 0
                                self.dialog_started_at = now
                                # Advance queued story if any
                                self.advance_dialog_queue()
                    return

                if event.key == pygame.K_q:
                    self.weapon_manager.cycle_weapon()
                # No manual ENTER-to-progress; progression is via gates

                if event.key == pygame.K_b:
                    self.show_shop = not self.show_shop
                if self.show_shop: return

                if event.key == pygame.K_ESCAPE:
                    self.state = "pause"
                elif event.key == pygame.K_m:
                    self.show_map = not self.show_map
                elif event.key == pygame.K_TAB:
                    self.hint_mode_index = (self.hint_mode_index + 1) % len(self.hint_modes)
                elif event.key == pygame.K_r:
                    # Manual reload
                    self.weapon_manager.reload()
                elif event.key == pygame.K_e:
                    self.interact()
                
                # Skills selection
                elif event.key == pygame.K_4:
                    mx, my = pygame.mouse.get_pos()
                    wmx, wmy = self.camera.screen_to_world(mx, my)
                    self.skill_manager.use_skill(0, self.player.x, self.player.y, wmx, wmy)
                elif event.key == pygame.K_5:
                    mx, my = pygame.mouse.get_pos()
                    wmx, wmy = self.camera.screen_to_world(mx, my)
                    self.skill_manager.use_skill(1, self.player.x, self.player.y, wmx, wmy)
                elif event.key == pygame.K_6:
                    mx, my = pygame.mouse.get_pos()
                    wmx, wmy = self.camera.screen_to_world(mx, my)
                    self.skill_manager.use_skill(2, self.player.x, self.player.y, wmx, wmy)

        if self.state == "pause" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "playing"
            elif event.key == pygame.K_RETURN:
                self.state = "playing"
            elif event.key == pygame.K_m:
                self.state = "menu"
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
        
        if self.state in ["win", "lose"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.__init__()
                self.state = "playing"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down = True
            if self.state == "playing" and self.show_shop:
                mx, my = pygame.mouse.get_pos()
                self.handle_shop_click(mx, my)
            if self.state == "pause":
                mx, my = pygame.mouse.get_pos()
                btns = getattr(self, "pause_buttons", {}) or {}
                if btns.get("continue") and btns["continue"].collidepoint(mx, my):
                    sound_manager.play("nut_bam")
                    self.state = "playing"
                elif btns.get("menu") and btns["menu"].collidepoint(mx, my):
                    sound_manager.play("nut_bam")
                    self.state = "menu"
                    sound_manager.play_music("nhac_cho_sanh")
                elif btns.get("quit") and btns["quit"].collidepoint(mx, my):
                    sound_manager.play("nut_bam")
                    pygame.quit()
                    sys.exit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down = False


def main():
    game = Game()
    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        
        game.update()
        game.draw()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
