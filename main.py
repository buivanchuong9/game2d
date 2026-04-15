from map_props import CHAPTER_TILES, DESERT_TILE, DESERT_TILE_ALT, DESERT_WALL, DESERT_GRASS, DESERT_GRASS_TUFT, DESERT_HUT, DESERT_BIG_GRASS, DESERT_BIG_ROCK, obstacle_prop_for_tile, draw_prop
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
from audio import play_bg_music, play_sound_effect
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
from pathfinding import a_star, bfs, dfs, greedy_safe
from player import Player
from weapon import WeaponManager
from all_graphics import ALL_GRAPHICS
from camera import Camera
from ui import load_ui_font, wrap_text, safe_load, safe_sheet_frame

# Tự động load toàn bộ file đồ họa vào dict ALL_GRAPHICS_SURFACES
ALL_GRAPHICS_SURFACES = {}
for path in ALL_GRAPHICS:
    try:
        # Tải ảnh và chuyển đổi sang định dạng pixel của màn hình
        img = pygame.image.load(path).convert_alpha()
        ALL_GRAPHICS_SURFACES[path] = img
    except Exception as e:
        print(f"[GRAPHICS LOAD ERROR] {path}: {e}")

from skill import SkillManager, Skill

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

INTERACT_RADIUS = 60
TILE_SIZE = 16
GRID_SIZE = 44


from shop import SHOP_CARD_SURFACES, get_random_shop_card, get_random_pet_card

# Tự động load toàn bộ sound (recursive)
SOUND_EFFECTS = {}
SOUND_BY_BASENAME = {}
for path in glob.glob("Sounds/**/*.*", recursive=True):
    try:
        if not path.lower().endswith((".mp3", ".wav", ".ogg")):
            continue
        SOUND_EFFECTS[path] = pygame.mixer.Sound(path)
        SOUND_BY_BASENAME[os.path.basename(path).lower()] = SOUND_EFFECTS[path]
    except Exception as e:
        print(f"[SOUND LOAD ERROR] {path}: {e}")

SOUND_EXTS = (".mp3", ".wav", ".ogg")

# Mapping key -> candidate base filenames (WITHOUT extension).
# Game will try base + .mp3/.wav/.ogg, plus legacy names.
SOUND_CANDIDATES: dict[str, list[str]] = {
    # Weapons (new Vietnamese names)
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

    # Combat/UI
    "sfx_enemy_hit": ["zombie_trung_dan", "sfx_enemy_hit"],
    "sfx_enemy_death": ["zombie_chet", "sfx_enemy_death"],
    "sfx_player_hit": ["nhan_vat_trung_don", "sfx_player_hit"],

    "sfx_gate_open": ["mo_cong", "sfx_gate_open"],
    "sfx_item_drop": ["roi_vat_pham", "sfx_item_drop"],
    "sfx_quest_complete": ["hoan_thanh_nhiem_vu", "sfx_quest_complete"],
}





def load_ui_font(size, bold=False):
    # Chi dung font Arial
    path = pygame.font.match_font("Arial", bold=bold)
    if path:
        return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def safe_load(path, size):
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except Exception:
        fallback = pygame.Surface(size, pygame.SRCALPHA)
        fallback.fill((100, 100, 100, 255))
        return fallback


def safe_sheet_frame(path, rect, size):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frame = sheet.subsurface(rect)
        return pygame.transform.scale(frame, size)
    except Exception:
        fallback = pygame.Surface(size, pygame.SRCALPHA)
        fallback.fill((120, 120, 120, 255))
        return fallback


def wrap_text(text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines



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
    "heal": safe_load("Sprites/Sprites_Weapon/Grenade-2.png", (24, 24)), # TODO: replace with medkit sprite
    "armor": safe_load("Sprites/Sprites_Effect/Pet_Power.png", (24, 24)),
    "ammo": safe_load("Sprites/Sprites_Weapon/Amo1.png", (20, 20)),
    "weapon": safe_load("Sprites/Sprites_Weapon/Shotgun-4.png", (34, 24)),
    "rocket_weapon": safe_load("Sprites/Sprites_Weapon/RPG-reisized.png", (38, 38)),
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
            elif "sniper" in wname:
                wtype = "sniper"
            elif "smg" in wname:
                wtype = "smg"
            elif "rocket" in wname or "rpg" in wname or "b40" in wname:
                wtype = "rocket"
            else:
                wtype = "rifle"

            if evt == "shot":
                play_sound_effect(f"sfx_shot_{wtype}")
            elif evt in {"reload_start", "reload_complete"}:
                play_sound_effect(f"sfx_reload_{wtype}")
        self.weapon_manager.on_event = _weapon_event
        self.story_flags = set()
        self.last_hint_path = []
        self.last_spawn_at = 0
        self.shot_counter = 0
        self.frenzy_window_until = 0
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
        self.current_pet = PET_BIRD
        self.unlocked_pets = [PET_BIRD]
        
        # --- Infinite Map ---
        self.chunks = {} # (cx, cy) -> list of objects
        self.visited_chunks = set()
        
        self.mouse_down = False
        self.state = "menu"
        self.show_help = False
        self.show_shop = False
        self.show_map = False
        self.hint_mode_index = 0
        self.hint_modes = ["BFS", "DFS", "SAFE", "A*"]
        
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
        
        play_bg_music()
        self.set_chapter(0)

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
        # Rooftop: open space, obstacle clusters as vents/AC, clear path to exit
        add_block_rect(roof_blocked, 6, 10, 16, 12)   # vent cluster
        add_block_rect(roof_blocked, 22, 6, 26, 9)    # AC cluster
        add_block_rect(roof_blocked, 30, 26, 34, 30)  # water tank zone
        add_block_rect(roof_blocked, 18, 30, 22, 34)  # debris
        # carve walkable lanes
        carve(roof_blocked, 3, 3, 40, 40)
        roof_blocked |= ring_walls()
        # keep obstacle islands but ensure corridors
        carve(roof_blocked, 3, 34, 40, 36)
        carve(roof_blocked, 4, 4, 10, 10)
        carve(roof_blocked, 34, 30, 38, 34)
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
            ItemPickup((10, 31), "Bandage", "Bang gac tu tui cuu ho san thuong.", "heal", amount=25),
        ]
        roof_npcs = [
            NPC("Phi cong", (38, 5), ["Toi chi lien lac duoc qua bo dam.", "Xuong cac tang duoi, mo cong san va goi tin hieu."], reward="radio", portrait_color=YELLOW, sprite_path="Sprites/Sprites_NPC/pilot.png",
                quest="Nhat sung + ha 1 zombie -> cong xuong tang se mo"),
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
            ItemPickup((35, 28), "Fuse", "Cau chi phu cho dien hanh lang.", "power", color=YELLOW),
            ItemPickup((14, 20), "Katana", "Thanh kiem nhat gia: Sac lem va toc do cao.", "weapon", weapon_data={
                "name": "Katana", "fire_rate": 2.5, "reload_time": 0.0,
                "image_path": "Sprites/Sprites_Weapon/Katana.png",
                "projectile_speed": 0, "damage": 110, "projectile_scale": (96, 96), "type": "melee",
                "projectile_image": [
                    {"atlas": "Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif", "tile": (32, 32)},
                    {"atlas": "Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif", "tile": (32, 32)},
                ],
            }),
            ItemPickup((24, 5), "Ammo", "Dan du tru tu phong nhan su.", "ammo", amount=18, color=WHITE),
        ]
        office_npcs = [
            NPC("Bao ve Nam", (21, 17), ["Toi giu duoc phong camera nhung cua dang ket.", "Ha zombie dac biet de lay the tu, roi khoi phuc dien de mo loi xuong."], reward="map", portrait_color=BLUE, sprite_path="Sprites/Sprites_NPC/guard.png",
                quest="Checkpoint: Ha du 10 zombie -> rơi Keycard. Sau do tim cau chi va bat hop dien."),
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
            ItemPickup((6, 6), "Medkit", "Mot hop cuu thuong lon trong phong cap cuu.", "heal", amount=50),
            ItemPickup((19, 20), "Armor Vest", "Ao giap nhe giup giam sat thuong.", "armor", amount=25, color=CYAN),
            ItemPickup((10, 26), "Rocket Launcher", "Vu khi no manh de quet dam dong zombie.", "rocket_weapon", color=ORANGE),
            ItemPickup((37, 33), "Control Fuse", "Thiet bi mo cong tang 1.", "exit", color=YELLOW),
            ItemPickup((27, 8), "Rifle Ammo", "Dan hiem cho sung truong.", "ammo", amount=28, color=WHITE),
        ]
        med_npcs = [
            NPC("Y ta Linh", (18, 7), ["Toi van con giu duoc kho thuoc.", "Ha 3 zombie dac biet va mo loi xuong tang 1, toi se giup cau."], reward="medkit", portrait_color=GREEN, sprite_path="Sprites/Sprites_NPC/medic.png",
                quest="Checkpoint: Ha 3 zombie dac biet -> mo duong xuong tang 1."),
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
            ItemPickup((7, 7), "Gate Switch", "Cong tac mo cong san.", "gate", color=ORANGE),
            ItemPickup((34, 29), "Signal Beacon", "Thiet bi phat tin hieu cho truc thang.", "signal", color=YELLOW),
            ItemPickup((38, 36), "Rescue Flare", "Phao sang dung de xac nhan vi tri ha canh.", "flare", color=RED),
        ]
        ground_npcs = [
            NPC("Ky thuat vien Huy", (17, 18), ["Toi giu duoc bo phat o san.", "Mo cong chinh, ra san va bat beacon. Quai ngoai san chi phat hien cau sau khi cong mo."], reward="shortcut", portrait_color=ORANGE, sprite_path="Sprites/Sprites_NPC/engineer.png",
                quest="Checkpoint: Mo cong chinh -> quái ngoài sân xuất hiện. Bat beacon -> tru vung."),
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
        # Basement: trục hành lang trung tâm + các phòng máy/ kho hai bên
        add_rect_walls(basement_blocked, 3, 3, 40, 40, doors=[(4, 35), (40, 35)])
        # Ensure player start area is walkable and connected
        carve(basement_blocked, 2, 33, 8, 39)           # spawn pocket
        carve(basement_blocked, 8, 33, 14, 35)          # connector to corridor
        # central hallway rails
        for x in range(10, 34):   # thu ngắn lại
            basement_blocked.add((x, 22))   # chỉ giữ 1 line thôi
        for pos in [(16, 20), (17, 20), (28, 24), (29, 24), (10, 24), (11, 24), (34, 20), (35, 20)]:
            basement_blocked.discard(pos)

        # generator room (top-right)

        # Right room
        add_rect_walls(basement_blocked, 26, 4, 40, 18, doors=[(38, 18), (26, 10)])
        carve(basement_blocked, 37, 17, 39, 19)
        carve(basement_blocked, 25, 9, 27, 11)
        # clutter piles
        for pos in [(8, 30), (9, 30), (8, 31), (30, 10), (31, 10), (32, 10), (14, 10), (14, 11), (15, 11), (34, 16)]:
            basement_blocked.add(pos)
        basement_decor = {
            (36, 8): "basement_panel",
            (34, 12): "basement_generator",
            (12, 30): "basement_crates",
            (30, 18): "basement_pipes",
        }

        lab_blocked = ring_walls()
        # Lab: hành lang chữ U + phòng lạnh + phòng điều khiển
        add_rect_walls(lab_blocked, 3, 3, 40, 40, doors=[(3, 6), (39, 35)])
        # cold storage (top)
        add_rect_walls(lab_blocked, 8, 4, 34, 16, doors=[(18, 16), (24, 4)])
        # research wing (left-bottom)
        add_rect_walls(lab_blocked, 4, 20, 18, 38, doors=[(18, 30), (10, 20)])
        # security/control (right-bottom)
        add_rect_walls(lab_blocked, 22, 22, 40, 38, doors=[(22, 30), (32, 22)])
        corridor(lab_blocked, 18, 16, 18, 20, width=5)
        corridor(lab_blocked, 18, 30, 22, 30, width=5)
        # benches / broken glass spots
        for pos in [(12, 10), (13, 10), (14, 10), (28, 8), (29, 8), (30, 8), (26, 28), (27, 28), (30, 32), (31, 32), (32, 32)]:
            lab_blocked.add(pos)
        lab_decor = {
            (30, 8): "lab_freezer",
            (24, 10): "lab_freezer",
            (12, 26): "lab_bench",
            (30, 26): "lab_console",
            (18, 18): "lab_tubes",
        }

        return [
            Chapter(
                "roof",
                "Chuong 1: Tang thuong",
                "Tinh day giua tan the",
                ["Mot vu no rung chuyen toa nha.", "Ban tinh day tren tang thuong, bo dam chi con tieng nhieu.", "Mot truc thang cuu ho dang do tin hieu tu duoi san."],
                ["Nhat sung", "Lay bang gac", "Ha zombie dau tien", "Mo loi xuong tang 3"],
                (38, 34),
                (4, 5),
                roof_blocked,
                roof_decor,
                roof_items,
                roof_npcs,
                roof_enemies,
                ORANGE,
                "Phi cong: Neu con nghe thay toi, hay xuong cac tang duoi va mo cong san.",
                quest_line="Thoat khoi san thuong: nhat sung, ha 1 zombie, mo cong xuong tang 3.",
                spawn_pool=[],
                max_alive_enemies=5,
                spawn_interval_ms=999999,
            ),
            Chapter(
                "office",
                "Chuong 2: Tang 3",
                "Khu van phong cu",
                ["Dien hanh lang chap chon, van phong bien thanh me cung.", "Zombie bat dau di chuyen nhanh hon trong khong gian hep."],
                ["Lay the tu", "Khoi phuc dien", "Noi chuyen voi bao ve", "Toi thang xuong tang 2"],
                (37, 35),
                (3, 34),
                office_blocked,
                office_decor,
                office_items,
                office_npcs,
                office_enemies,
                BLUE,
                "Bao ve Nam: Toi thay cau thang ky thuat o goc dong nam. Nhung phai co dien.",
                quest_line="Tang 3: ha du 10 zombie lay the tu, khoi phuc dien, mo loi xuong tang 2.",
                spawn_pool=[Goblin, DashingGoblin, FlyingEye],
                max_alive_enemies=11,
                spawn_interval_ms=3200,
            ),
            Chapter(
                "medical",
                "Chuong 3: Tang 2",
                "Khu y te va kho chua",
                ["Mui hoa chat va mau tron lan trong hanh lang.", "Day la noi con nhieu tiep te nhat, cung la noi nguy hiem nhat."],
                ["Lay kho thuoc", "Diet 3 zombie dac biet", "Giup y ta", "Mo duong xuong tang 1"],
                (39, 35),
                (4, 34),
                med_blocked,
                med_decor,
                med_items,
                med_npcs,
                med_enemies,
                GREEN,
                "Y ta Linh: Cong tang 1 chi mo neu cap dien dung tuyen ky thuat.",
                quest_line="Tang 2: thu thap vat tu, ha 3 zombie dac biet, mo duong xuong tang 1.",
                spawn_pool=[Goblin, Mushroom, TeleportingMushroom, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=3000,
            ),
            # --------- NEW CHAPTER: Basement ----------
            Chapter(
                "basement",
                "Chuong 4: Tang ham",
                "May phat du phong va cua sat",
                [
                    "Khong khi am va mùi dau may xoc thang vao mui.",
                    "Tieng kim loai keo len lanh song lung — ben duoi co thu gi do dang di chuyen.",
                ],
                ["Tim ma cua", "Ha zombie dac biet", "Khoi dong may phat", "Mo cua den phong thi nghiem"],
                (40, 35),
                (4, 35),
                basement_blocked,
                basement_decor,
                [
                    ItemPickup((8, 34), "So tay ky thuat", "Trong so co ma cua phong may: 4821.", "code", color=WHITE),
                    ItemPickup((36, 8), "Dan du tru", "Hop dan con moi trong tu ky thuat.", "ammo", amount=24, color=WHITE),
                    ItemPickup((12, 10), "Ao giap", "Ao giap cu nhung van dung duoc.", "armor", amount=20, color=CYAN),
                ],
                [
                    NPC("Tho may Dung", (10, 26), ["May phat o phong may bi khoa ma.", "Tim so tay ky thuat, bat dien len thi cua sat se mo."], reward="shortcut", portrait_color=ORANGE, sprite_path="Sprites/Sprites_NPC/engineer.png"),
                ],
                [
                    (Skeleton, (22, 30), "special"),
                    (TeleportingMushroom, (30, 12), "special"),
                    (Mushroom, (16, 16), "tank"),
                    (EvilWizard, (36, 30), "ranged"),
                ],
                (160, 160, 200),
                "Radio: Tang ham rat nguy hiem. Bat duoc dien la se mo duoc cua sat dan den phong thi nghiem.",
                spawn_pool=[Goblin, Skeleton, TeleportingMushroom],
                max_alive_enemies=13,
                spawn_interval_ms=2600,
            ),
            # --------- NEW CHAPTER: Lab ----------
            Chapter(
                "lab",
                "Chuong 5: Phong thi nghiem",
                "Nguon goc dai dich",
                [
                    "Anh den nhap nhoang tren cac tủ lanh mau.",
                    "Co the o day co thu gi do giup ban song sot lau hon.",
                ],
                ["Lay mau khang the", "Cuu bac si", "Mo loi ra sanh chinh"],
                (39, 35),
                (3, 6),
                lab_blocked,
                lab_decor,
                [
                    ItemPickup((34, 10), "Mau khang the", "Mot ong mau duoc niem phong. Co the dung de pha che.", "antidote", color=GREEN),
                    ItemPickup((8, 34), "Medkit", "Hop cuu thuong con day.", "heal", amount=50),
                    ItemPickup((18, 30), "The tu an ninh", "Mo cua ra hanh lang chinh.", "keycard", color=BLUE),
                ],
                [
                    NPC("Bac si Hoa", (12, 8), ["Cau tim thay ong mau roi sao?", "Hay mo cua an ninh, chung ta can ra khoi day ngay!"], reward="medkit", portrait_color=CYAN, sprite_path="Sprites/Sprites_NPC/doctor.png"),
                ],
                [
                    (EvilWizard, (26, 8), "ranged"),
                    (Skeleton, (32, 24), "special"),
                    (Mushroom, (22, 34), "tank"),
                    (DashingGoblin, (37, 18), "fast"),
                ],
                (120, 220, 200),
                "Bac si: Neu lay duoc mau khang the, co the keo dai thoi gian song sot. Nhung hay ra khoi phong thi nghiem!",
                spawn_pool=[Goblin, DashingGoblin, FlyingEye, Skeleton],
                max_alive_enemies=14,
                spawn_interval_ms=2400,
            ),
            Chapter(
                "ground",
                "Chuong 6: Tang 1 - Sanh chinh",
                "Diem nghen cuoi cung ben trong toa nha",
                ["Ban da xuong toi tang tret. Coi bao dong vang doi khap sanh.", "Zombie dang tran vao qua cac cua kinh vo.", "Phai mo duoc cong chinh de ra san sau."],
                ["Mo cong chinh", "Ha 2 zombie dac biet", "Tim loi ra san"],
                (38, 36),
                (5, 5),
                ground_blocked,
                {(6, 6): "hut", (24, 20): "rock", (10, 30): "grass"},
                ground_items,
                ground_npcs,
                ground_enemies,
                RED,
                "Ky thuat vien Huy: Cong chinh dang ket. Toi se mo tu xa, hay giu chan chung!",
                spawn_pool=[Goblin, DashingGoblin, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=2800,
            ),
            Chapter(
                "escape",
                "Chuong 7: San bay - Thoat hiem",
                "Truc thang dang doi",
                ["Bau troi ruc lua, truc thang cuu ho da o phia truoc.", "Hay bat den hieu beacon va tru vung cho den khi chung co the ha canh."],
                ["Bat den hieu Beacon", "Tru vung trong 25 giay", "Ha boss Old Guardian", "Len truc thang"],
                (40, 37),
                (10, 10),
                ring_walls(),
                {(15, 15): "rock", (25, 25): "grass", (12, 30): "hut", (30, 12): "rock", (38, 36): "heli_pad"},
                [ItemPickup((34, 29), "Rescue Flare", "Phao sang xac nhan vi tri.", "flare", color=RED)],
                [],
                [
                    (BigFlyingEye, (33, 35), {"type": "boss", "health": 150}),
                    (OldGuardian, (25, 25), {"type": "boss", "health": 1200}),
                    (EvilWizard, (35, 10), "ranged"),
                    (EvilWizard, (10, 35), "ranged"),
                ],
                YELLOW,
                "Phi cong: Toi thay beacon roi! Dang ha do cao, hay quet sach khu vuc!",
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
                "title": "Thanh pho da sup do",
                "subtitle": "Virus la bien ca khu trung tam thanh o zombie chi sau mot dem.",
                "accent": RED,
                "art": [("player", 160, 360), ("eye", 590, 160), ("goblin", 770, 360)],
            },
            {
                "title": "Tinh day tren tang thuong",
                "subtitle": "Ban bi mac ket giua khoi lua, chi con tieng bo dam cuu ho vong lai.",
                "accent": ORANGE,
                "art": [("player", 220, 340), ("hut", 670, 340), ("eye", 760, 180)],
            },
            {
                "title": "Xuong tung tang, mo duong song",
                "subtitle": "Tim sung, vat tu, chia khoa va khoi phuc dien de mo loi thoat.",
                "accent": BLUE,
                "art": [("player", 170, 350), ("rocket", 540, 350), ("mortar", 760, 320)],
            },
            {
                "title": "Tru vung toi chuyen bay cuoi",
                "subtitle": "Ra san, bat den hieu va chong lai dot zombie cuoi cung de thoat khoi thanh pho.",
                "accent": YELLOW,
                "art": [("player", 160, 360), ("mushroom", 620, 330), ("rocket", 800, 240)],
            },
        ]

    def set_chapter(self, index):
        self.chapter_index = index
        self.chapter = self.chapters[index]
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
        self.hint_mode_index = 0
        self.next_chapter_ready = False
        self.exit_unlocked = False
        self.yard_spawned = False
        self.yard_enemy_plan = []
        self.yard_gate_tile = (26, 22)
        self.last_objective_text = self.objective_label() if self.chapter else ""
        self.objective_flash_until = pygame.time.get_ticks() + 1800
        self.last_hint_path = []
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

    def item_at_player(self):
        player_tile = self.current_tile()
        for item in self.chapter.items:
            # Money is auto-picked up; never require E
            if item.item_type == "money":
                continue
            if not item.collected and abs(item.grid_pos[0] - player_tile[0]) <= 1 and abs(item.grid_pos[1] - player_tile[1]) <= 1:
                return item
        return None

    def npc_near_player(self):
        px, py = self.current_tile()
        for npc in self.chapter.npcs:
            if abs(npc.grid_pos[0] - px) <= 1 and abs(npc.grid_pos[1] - py) <= 1:
                return npc
        return None

    def interact(self):
        item = self.item_at_player()
        if item:
            self.collect_item(item)
            return
        npc = self.npc_near_player()
        if npc:
            self.open_dialog(npc)
            return
        player_tile = self.current_tile()
        if player_tile in self.power_boxes:
            self.activate_box(player_tile)

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
                f"Zombie da roi {weapon_data['name']}. Bam E de nhat.",
                "weapon_drop",
                color=RARITY_COLORS.get(weapon_data.get("rarity", "common"), ORANGE),
                weapon_data=weapon_data,
                sprite_surface=wp_sprite
            )
        )

    def spawn_mission_item_at(self, tile: tuple[int, int], item_type: str, name: str, description: str, color=YELLOW):
        """Spawn a mission item on a walkable tile if free."""
        tx, ty = tile
        if not (1 <= tx < GRID_SIZE - 1 and 1 <= ty < GRID_SIZE - 1):
            return False
        if (tx, ty) in self.current_blocked:
            return False
        for it in self.chapter.items:
            if not it.collected and it.grid_pos == (tx, ty):
                return False
        self.chapter.items.append(ItemPickup((tx, ty), name, description, item_type, color=color))
        play_sound_effect("sfx_item_drop")
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

    def collect_item(self, item):
        item.collected = True
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
            self.popup = "Da nhat Shotgun. Da chuyen sang sung moi."
            self.queue_story_lines("Nhan vat chinh", ["Duoc roi, co them hoa luc roi.", "Giet 1 zombie nua la xong man khoi dong."], ORANGE)
        elif item.item_type == "heal":
            self.player.heal(item.amount)
            self.mission.data["medkit_collected"] = True
            if self.chapter.id == "medical":
                self.mission.data["supply_cache"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
                self.queue_story_lines("Y ta Linh", ["Lay them bang gac va thuoc tang luc neu thay.", "Tang duoi nguy hiem hon nhieu."], GREEN)
        elif item.item_type == "ammo":
            self.popup = f"Nhat {item.amount} vien dan du tru."
            # Feed reserve ammo into current weapon if applicable
            w = self.weapon_manager.current_weapon
            if w and not getattr(w, "melee", False):
                w.reserve_ammo += item.amount
        elif item.item_type == "armor":
            self.player.add_armor(item.amount)
            self.mission.data["supply_cache"] = True
            if self.chapter.id == "medical":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
            self.queue_story_dialog("Hero", "Ao giap nay se giup minh song dai hon.", CYAN)
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
            self.popup = "Da mo khoa Rocket Launcher va chuyen sang vu khi moi."
            self.queue_story_lines("Y ta Linh", ["Phia duoi dang co dam dong rat lon.", "Lay vu khi no nay, no se giup cau mo duong."], GREEN)
        elif item.item_type == "weapon_drop":
            weapon_data = item.weapon_data or dict(random.choice(WEAPON_DROP_POOL))
            was_new = self.unlock_weapon(weapon_data, equip_now=True)
            if was_new:
                self.popup = f"Da nhat {weapon_data['name']}. Da trang bi ngay."
            else:
                self.popup = f"Ban da co {weapon_data['name']}. Da chuyen sang vu khi nay."
        elif item.item_type == "keycard":
            self.mission.data["keycard_collected"] = True
            self.queue_story_lines("Bao ve Nam", ["Tot, do la the tu cua phong an ninh.", "Mang no toi hop dien ben phai."], BLUE)
            if self.chapter.id in {"office", "lab"}:
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2 if self.chapter.id == "office" else 2)
        elif item.item_type == "code":
            # Used in basement
            self.mission.data["basement_code"] = True
            self.popup = "Da lay duoc ma cua: 4821. Hay toi phong may va khoi dong may phat."
            self.queue_story_dialog("Hero", "Ma cua phong may... minh can tim bang dieu khien dien.", ORANGE)
            if self.chapter.id == "basement":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
        elif item.item_type == "antidote":
            # Used in lab
            self.mission.data["antidote_collected"] = True
            self.popup = "Da lay mau khang the. Co the dung de keo dai suc ben."
            self.queue_story_lines("Bac si Hoa", ["Tot! Day la mau quan trong.", "Gio mo cua an ninh va thoat ra sanh chinh!"], CYAN)
            if self.chapter.id == "lab":
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
        elif item.item_type == "power":
            self.popup = "Da lay cau chi. Toi hop dien de khoi phuc nguon."
            self.queue_story_dialog("Radio", "Dien phu dang o trang thai offline. Hay lap cau chi ngay.", YELLOW)
            if self.chapter.id == "office":
                self.mission.data["fuse_collected"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
        elif item.item_type == "exit":
            self.mission.data["supply_cache"] = True
            self.popup = "Thiet bi dieu khien cong da co trong tay."
            self.queue_story_dialog("Hero", "Mo duoc cong tang 1 roi. Phai tiep tuc di chuyen.", ORANGE)
            if self.chapter.id == "medical":
                self.mission.data["control_fuse_collected"] = True
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
        elif item.item_type == "gate":
            self.mission.data["gate_opened"] = True
            self.popup = "Cong san da mo. Di toi beacon."
            if self.chapter.id == "ground":
                self.remove_gate_collision(self.yard_gate_tile)
                self.spawn_particles(self.yard_gate_tile[0] * TILE_SIZE + 8, self.yard_gate_tile[1] * TILE_SIZE + 8, YELLOW, count=18)
                play_sound_effect("sfx_gate_open")
            else:
                self.remove_gate_collision(item.grid_pos)
            self.queue_story_lines("Ky thuat vien Huy", ["Cong san da mo.", "Toi se giu he thong dien on dinh, cau ra beacon di."], ORANGE)
        elif item.item_type == "signal":
            self.mission.data["signal_started"] = True
            self.beacon_started_at = pygame.time.get_ticks()
            self.holdout_until = self.beacon_started_at + self.chapter.holdout_seconds * 1000
            self.popup = "Tin hieu cuu ho da phat. Tru vung toi khi truc thang toi."
            self.queue_story_lines("Phi cong", ["Da nhan duoc tin hieu.", "Giu vi tri, toi se ha canh trong it phut nua."], YELLOW)
        elif item.item_type == "flare":
            self.popup = "Phao sang da san sang cho diem ha canh."
        elif item.item_type == "money":
            self.money += max(1, int(item.amount or 1))
            self.popup = f"+{max(1, int(item.amount or 1))} tien"
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
                self.popup = "Dien da tro lai. Thang ky thuat tang 2 da mo."
                self.remove_gate_collision((37, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 4)
            else:
                self.popup = "Can Keycard + Fuse truoc khi kich hoat lai hanh lang."
        elif cid == "medical":
            # Require picking up Control Fuse first
            if self.mission.data.get("control_fuse_collected"):
                self.mission.data["gate_opened"] = True
                self.popup = "Loi xuong tang 1 da duoc mo."
                self.remove_gate_collision((39, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Can nhat thiet bi mo cong (Control Fuse) truoc."
        elif cid == "basement":
            if self.mission.data.get("basement_code", False) and self.mission.data.get("special_kills", 0) >= 2:
                self.mission.data["power_restored"] = True
                self.mission.data["gate_opened"] = True
                self.popup = "May phat da khoi dong. Cua sat den phong thi nghiem da mo."
                self.remove_gate_collision((40, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Can ma cua + ha du 2 zombie dac biet truoc."
        elif cid == "lab":
            if self.mission.data.get("antidote_collected", False) and self.mission.data.get("keycard_collected", False):
                self.mission.data["gate_opened"] = True
                self.popup = "Cua an ninh mo. Duong ra sanh chinh da thong."
                self.remove_gate_collision((39, 35))
                self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 3)
            else:
                self.popup = "Can the tu va mau khang the truoc khi mo cua an ninh."
        elif cid == "ground":
            self.mission.data["signal_started"] = True
            self.beacon_started_at = pygame.time.get_ticks()
            self.holdout_until = self.beacon_started_at + self.chapter.holdout_seconds * 1000
            self.popup = "Beacon da bat. Giu vi tri."
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
                self.popup = "Ban nhan duoc so do an ninh tang hien tai."
            elif npc.reward == "medkit":
                self.player.heal(20)
                self.popup = "Y ta Linh hoi mau cho ban."
            elif npc.reward == "shortcut":
                self.popup = "Ky thuat vien danh dau duong tat ra san."
            elif npc.reward == "radio":
                self.popup = "Bo dam bat duoc kenh cuu ho on dinh hon."
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
            self.player.x = max(TILE_SIZE, min(self.player.x, self.world_w - TILE_SIZE))
            self.player.y = max(TILE_SIZE, min(self.player.y, self.world_h - TILE_SIZE))

            # Auto-pickup money on contact
            ptx, pty = self.current_tile()
            for it in self.chapter.items:
                if it.collected:
                    continue
                if it.item_type != "money":
                    continue
                # within 1 tile radius, so "chạy vào là nhặt"
                if abs(it.grid_pos[0] - ptx) <= 1 and abs(it.grid_pos[1] - pty) <= 1:
                    it.collected = True
                    self.money += int(getattr(it, "amount", 1) or 1)
                    play_sound_effect("sfx_item_drop")
            
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
                self.current_blocked
            )
            
            self.skill_manager.update([entry.enemy for entry in self.story_enemies], self.current_blocked)
            self.update_particles()
            self.handle_progression()
            self.check_auto_transition()
            self.update_hint_path()

            # Player hit SFX (throttled)
            now = pygame.time.get_ticks()
            if self.player.health < self._last_player_hp and now - self._last_player_hit_sfx_at > 120:
                self._last_player_hit_sfx_at = now
                play_sound_effect("sfx_player_hit")
            self._last_player_hp = self.player.health
            
            if self.chapter.id == "escape" and hasattr(self, 'rescue_arrived') and self.rescue_arrived:
                # Kiem tra xem nguoi choi da den Helipad chua
                dist_to_extract = math.hypot(self.player.x - 38*TILE_SIZE, self.player.y - 36*TILE_SIZE)
                if dist_to_extract < 64:
                    self.state = "win"

            if self.player.health <= 0:
                self.end_reason = "Ban da bi zombie ap dao truoc khi thoat duoc khoi thanh pho."
                self.state = "lose"

    def update_frenzy(self, shot_fired):
        now = pygame.time.get_ticks()
        if shot_fired:
            if now > self.frenzy_window_until:
                self.shot_counter = 0
            self.shot_counter += 1
            self.frenzy_window_until = now + 2200
        elif now > self.frenzy_window_until:
            self.shot_counter = 0

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
                play_sound_effect("sfx_enemy_hit")
            entry._last_health = cur_hp

            enemy.obstacle_map = self.build_obstacle_grid()
            enemy.update(self.player)
            enemy.x = max(TILE_SIZE, min(enemy.x, MAP_WIDTH - TILE_SIZE))
            enemy.y = max(TILE_SIZE, min(enemy.y, MAP_HEIGHT - TILE_SIZE))
            if enemy.is_dead and not entry.dead_registered:
                entry.dead_registered = True
                play_sound_effect("sfx_enemy_death")
                self.kill_count += 1
                self.mission.data["zombies_killed"] += 1
                # Stage progression hooks (linear missions)
                if self.chapter.id == "roof" and self.mission.data.get("weapon_collected") and self.mission.data["zombies_killed"] >= 1:
                    self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
                # Each kill drops 1 money
                etile = entry.tile()
                self.spawn_mission_item_at(etile, "money", "Tien", "1 tien roi tu zombie.", color=YELLOW)
                if entry.archetype in {"special", "tank"}:
                    self.mission.data["special_kills"] += 1
                if entry.archetype == "boss":
                    self.mission.data["boss_down"] = True

                # Mission drops to make objectives obvious
                if self.chapter.id == "office" and not self.mission.data.get("keycard_collected", False):
                    # Guaranteed: kill 10 zombies -> keycard drops (not RNG)
                    if self.mission.data.get("zombies_killed", 0) >= 10 and "office_keycard_drop" not in self.story_flags:
                        # Only mark dropped when we successfully place it
                        if self.spawn_mission_item_near(etile, "keycard", "Keycard", "The tu an ninh roi ra sau khi ha 10 zombie.", color=BLUE, radius=3):
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
                        if self.spawn_mission_item_near(etile, "antidote", "Mau khang the", "Ong mau roi tu ke tan cong.", color=GREEN, radius=3):
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
            self.queue_story_lines("Bao ve Nam", ["Khu này sạch. Cậu làm tốt lắm.", "Nhớ nhặt Keycard, nó mở cửa an ninh."], BLUE)
            self.queue_story_lines("Hero", ["Rõ. Mình sẽ tìm trong xác bọn đặc biệt."], ORANGE)
        elif cid == "medical":
            self.queue_story_lines("Y ta Linh", ["Cậu vẫn ổn chứ?", "Lấy đồ y tế rồi đi nhanh, chúng sẽ quay lại."], GREEN)
            self.queue_story_lines("Hero", ["Ừ. Mình đi đây."], ORANGE)
        elif cid == "basement":
            self.queue_story_lines("Radio", ["Dưới tầng hầm có máy phát.", "Khởi động được nó thì đường thoát sẽ mở."], YELLOW)
            self.queue_story_lines("Hero", ["Nghe như kế hoạch duy nhất."], ORANGE)
        elif cid == "lab":
            self.queue_story_lines("Nha nghien cuu An", ["Tốt! Khu lab đã yên.", "Mau khang the phải được mang ra ngoài ngay."], CYAN)
            self.queue_story_lines("Hero", ["Mở cổng. Mình ra sảnh."], ORANGE)
        elif cid == "ground":
            self.queue_story_lines("Phi cong", ["Khu vực tạm sạch!", "Bật beacon lên, tôi sẽ hạ độ cao."], YELLOW)
            self.queue_story_lines("Hero", ["Đã rõ. Mình giữ vị trí."], ORANGE)
        else:
            self.queue_story_lines("Hero", ["Khu này sạch... đi tiếp thôi."], ORANGE)

    def handle_progression(self):
        if self.chapter.id == "roof" and self.mission.data["zombies_killed"] >= 1 and "roof_first_kill" not in self.story_flags:
            self.story_flags.add("roof_first_kill")
            self.queue_story_lines("Nhan vat chinh", ["Con dau tien da guc.", "Minh phai lay do roi mo loi xuong ngay."], ORANGE)
        if self.chapter.id == "roof" and self.mission.data["weapon_collected"] and self.mission.data["zombies_killed"] >= 1:
            # Chapter 1: open gate immediately after the simple starter objectives
            self.mission.data["medkit_collected"] = True
            self.mission.data["power_restored"] = True
            self.mission.data["gate_opened"] = True
            self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 2)
        if self.chapter.id == "office" and self.mission.data["power_restored"] and "office_power" not in self.story_flags:
            self.story_flags.add("office_power")
            self.queue_story_lines("Bao ve Nam", ["Dien da len. Camera cho thay cau thang ky thuat da mo.", "Di nhanh len, chung dang ap sat tu hanh lang sau."], BLUE)

        # Failsafe: if player reached 10 kills but keycard never spawned (blocked tile etc)
        if self.chapter.id == "office" and not self.mission.data.get("keycard_collected", False):
            if int(self.mission.data.get("zombies_killed", 0) or 0) >= 10:
                has_keycard_on_ground = any((not it.collected) and it.item_type == "keycard" for it in self.chapter.items)
                if not has_keycard_on_ground:
                    ptile = self.current_tile()
                    if self.spawn_mission_item_near(ptile, "keycard", "Keycard", "The tu an ninh (failsafe).", color=BLUE, radius=2):
                        self.popup = "Keycard da xuat hien gan ban!"
                        self.popup_timer = pygame.time.get_ticks() + 2200
                        self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)

        # Failsafe: lab antidote can never get lost due to blocked tiles
        if self.chapter.id == "lab" and not self.mission.data.get("antidote_collected", False):
            has_on_ground = any((not it.collected) and it.item_type == "antidote" for it in self.chapter.items)
            if self.mission.data.get("special_kills", 0) >= 1 and not has_on_ground:
                ptile = self.current_tile()
                if self.spawn_mission_item_near(ptile, "antidote", "Mau khang the", "Mau khang the (failsafe).", color=GREEN, radius=2):
                    self.popup = "Mau khang the da xuat hien gan ban!"
                    self.popup_timer = pygame.time.get_ticks() + 2200
                    self.mission.data["stage"] = max(int(self.mission.data.get("stage", 0) or 0), 1)
        if self.chapter.id == "medical" and self.mission.data["special_kills"] >= 2 and "medical_warning" not in self.story_flags:
            self.story_flags.add("medical_warning")
            self.queue_story_lines("Y ta Linh", ["Co loai dot bien dang di trong kho.", "Dung doi mat qua lau, no rat trau."], GREEN)
        if self.chapter.id == "medical" and self.mission.data["special_kills"] >= 3:
            self.mission.data["specials_cleared"] = True
        if self.chapter.id == "ground" and self.mission.data["signal_started"] and pygame.time.get_ticks() >= self.holdout_until:
            self.mission.data["holdout_complete"] = True
        if self.chapter.id == "ground" and self.mission.data["signal_started"] and "ground_hold" not in self.story_flags:
            self.story_flags.add("ground_hold")
            self.queue_story_lines("Phi cong", ["Toi dang ha do cao.", "Dung de boss dot bien ap sat beacon."], YELLOW)
            
        if self.chapter.id == "escape" and self.mission.data["boss_down"]:
            if not getattr(self, "countdown_started", False):
                self.countdown_started = True
                self.holdout_until = pygame.time.get_ticks() + 30 * 1000  # 30 giây
                self.queue_story_lines("Phi cong", ["Da xac nhan muc tieu nguy hiem bi ha.", "Dang bay toi vi tri. Giu vung trong 30 giay!"], YELLOW)

            if getattr(self, "countdown_started", False) and pygame.time.get_ticks() >= self.holdout_until and not getattr(self, "rescue_arrived", False):
                self.rescue_arrived = True
                self.mission.data["helicopter_arrived"] = True
                self.queue_story_lines("Phi cong", ["Truc thang da ha canh! Len nhanh nao!"], YELLOW)

        # Auto unlock exit gate when objectives done
        if self.mission.complete() and not self.exit_unlocked:
            self.exit_unlocked = True
        if self.chapter.exit_pos in self.current_blocked:
            self.current_blocked.remove(self.chapter.exit_pos)
            if self.chapter.exit_pos:
                self.remove_gate_collision(self.chapter.exit_pos)
            play_sound_effect("sfx_quest_complete")
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
        """Walk-through gate to go next chapter (no button press)."""
        if not self.exit_unlocked:
            return
        if not self.chapter.exit_pos:
            return
        # Ground -> Yard should be seamless (stay in same chapter)
        if self.chapter.id == "ground":
            return

        px, py = self.current_tile()
        ex, ey = self.chapter.exit_pos
        if abs(px - ex) <= 0 and abs(py - ey) <= 0:
            if self.chapter_index < len(self.chapters) - 1:
                self.set_chapter(self.chapter_index + 1)
                self.state = "playing"

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
        return "Ra diem truc thang"

    def auto_select_hint_mode(self):
        cid = self.chapter.id
        if cid == "roof":
            self.hint_mode_index = 0
            return
        if cid == "office":
            if not self.mission.data["keycard_collected"] or not self.mission.data["npc_saved"]:
                self.hint_mode_index = 1
            else:
                self.hint_mode_index = 0
            return
        if cid == "medical":
            if not self.mission.data["gate_opened"]:
                self.hint_mode_index = 2
            else:
                self.hint_mode_index = 3
            return
        self.hint_mode_index = 3 if self.mission.data["signal_started"] else 2

    def unexplored_goals(self):
        goals = set()
        for item in self.chapter.items:
            if not item.collected:
                goals.add(item.grid_pos)
        for npc in self.chapter.npcs:
            if not npc.interacted:
                goals.add(npc.grid_pos)
        if self.chapter.exit_pos:
            goals.add(self.chapter.exit_pos)
        return goals

    def update_hint_path(self):
        self.auto_select_hint_mode()
        current_objective = self.objective_label()
        if current_objective != self.last_objective_text:
            self.last_objective_text = current_objective
            self.objective_flash_until = pygame.time.get_ticks() + 1800
        start = self.current_tile()
        goal = self.objective_tile()
        danger = self.build_danger_map()
        blocked = self.current_blocked
        mode = self.hint_modes[self.hint_mode_index]
        if mode == "BFS":
            self.last_hint_path = bfs(start, goal, GRID_SIZE, GRID_SIZE, blocked)
        elif mode == "DFS":
            self.last_hint_path = dfs(start, self.unexplored_goals(), GRID_SIZE, GRID_SIZE, blocked)
        elif mode == "SAFE":
            self.last_hint_path = greedy_safe(start, goal, GRID_SIZE, GRID_SIZE, blocked, danger)
        else:
            self.last_hint_path = a_star(start, goal, GRID_SIZE, GRID_SIZE, blocked, danger)

    def draw_path_overlay(self, surface):
        if not self.last_hint_path: return
        mode = self.hint_modes[self.hint_mode_index]
        color = CYAN if mode == "A*" else GREEN if mode == "BFS" else RED if mode == "DFS" else YELLOW
        points = []
        for x, y in self.last_hint_path:
            sx, sy = self.camera.world_to_screen(x * TILE_SIZE + 8, y * TILE_SIZE + 8)
            points.append((sx, sy))
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 3)
            # Draw node pulses for clarity
            for i, p in enumerate(points):
                if i % 3 == 0:
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
        self.draw_path_overlay(screen)
        # Vẽ hiệu ứng kỹ năng
        self.skill_manager.draw(screen, self.camera)

        # Darkness overlay (power-out ambience)
        self.draw_darkness(screen)
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
                base_tile = base_2 if (tx * 3 + ty * 5) % 11 == 0 else base_1
                sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
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
                mission_types = {"keycard", "power", "code", "antidote", "exit", "exit_key", "gate", "signal"}
                is_mission = item.item_type in mission_types
                if is_mission or item.item_type == "weapon_drop":
                    pulse = 10 + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 6)
                    ring_col = (255, 220, 80) if is_mission else item.color
                    pygame.draw.circle(surface, ring_col, (sx + 8, sy + 8), pulse, 2)
                    # Name label
                    label_col = YELLOW if is_mission else item.color
                    label = self.font_small.render(item.name, True, label_col)
                    surface.blit(label, (sx - 4, sy - 14))
                if item.sprite_surface:
                    surface.blit(item.sprite_surface, (sx, sy))
                else:
                    # Fallback if no sprite
                    sprite = ITEM_SURFACES.get(item.item_type)
                    if sprite:
                        surface.blit(sprite, (sx, sy))
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
            
        self.draw_world_fx(surface)

    def draw_world_props(self, surface):
        pass

    def draw_pet_companion(self, surface):
        now = pygame.time.get_ticks()
        orbit_x = self.player.x - 34 + math.sin(now * 0.004) * 18
        orbit_y = self.player.y + 22 + math.cos(now * 0.003) * 12
        sx, sy = self.camera.world_to_screen(orbit_x, orbit_y)
        surface.blit(self.current_pet, self.current_pet.get_rect(center=(sx, sy)))
        # Enhanced orbital effect
        for i in range(3):
            ang = now * 0.005 + i * 2.09
            px = sx + math.cos(ang) * 15
            py = sy + math.sin(ang) * 15
            pygame.draw.circle(screen, (200, 220, 255, 100), (int(px), int(py)), 3)

    def draw_chapter_backdrop(self, surface):
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
        self.draw_card(header_rect, self.chapter.chapter_color, title="San Thuong Cuoi", subtitle=self.chapter.title)

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
        self.draw_card(objective_rect, YELLOW, title=f"Goi y: {self.hint_modes[self.hint_mode_index]}", subtitle=self.objective_label())

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
        self.draw_card(minimap_frame, self.chapter.chapter_color, title="Minimap", subtitle="Muc tieu va duong di")
        minimap_rect = pygame.Rect(minimap_frame.x + 12, minimap_frame.y + 44, minimap_frame.width - 24, 152)
        self.draw_minimap(minimap_rect)

        info_rect = pygame.Rect(MAP_WIDTH + 14, 666, SIDEBAR_WIDTH - 28, 86)
        self.draw_card(info_rect, CYAN, title="Thong tin", subtitle=f"Zombie: {self.kill_count}  |  NPC: {self.saved_npcs}")
        y = info_rect.y + 48
        stats = [
            "Chuot trai ban  |  E nhat",
            "Q doi sung  |  Tu dong qua cong",
            f"Thuat toan: {self.hint_modes[self.hint_mode_index]}",
        ]
        for line in stats:
            screen.blit(self.font_small.render(line, True, SOFT), (info_rect.x + 14, y))
            y += 18

        asset_rect = pygame.Rect(MAP_WIDTH + 14, 752, SIDEBAR_WIDTH - 28, 40)
        self.draw_card(asset_rect, ORANGE, title="Loadout & Ho tro", subtitle="Card asset dang dung")
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
        if self.last_hint_path:
            for tile in self.last_hint_path:
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
        if nearby_npc and not self.dialog_npc:
            hint_rect = pygame.Rect(24, MAP_HEIGHT - 118, 300, 32)
            pygame.draw.rect(screen, CARD_ALT, hint_rect, border_radius=10)
            pygame.draw.rect(screen, CYAN, hint_rect, 1, border_radius=10)
            screen.blit(self.font.render(f"Nhấn E để nói chuyện với {nearby_npc.name}", True, WHITE), (hint_rect.x + 10, hint_rect.y + 8))
        item = self.item_at_player()
        if item and not self.dialog_npc:
            hint_rect = pygame.Rect(24, MAP_HEIGHT - 118, 300, 32)
            pygame.draw.rect(screen, CARD_ALT, hint_rect, border_radius=10)
            pygame.draw.rect(screen, ORANGE, hint_rect, 1, border_radius=10)
            screen.blit(self.font.render(f"Nhấn E để nhặt {item.name}", True, WHITE), (hint_rect.x + 10, hint_rect.y + 8))
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
        for tile in self.last_hint_path:
            pygame.draw.rect(screen, YELLOW, (rect.x + tile[0] * scale, rect.y + tile[1] * scale, scale, scale), 1)
        px, py = self.current_tile()
        pygame.draw.circle(screen, WHITE, (int(rect.x + px * scale), int(rect.y + py * scale)), 5)
        screen.blit(self.font_big.render("Ban Do Chien Thuat", True, WHITE), (rect.x + 18, rect.y - 34))

    def draw_menu(self):
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(screen, (28, 30, 40), (0, y), (SCREEN_WIDTH, y), 1)
        shadow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shadow.fill((10, 8, 12, 180))
        screen.blit(shadow, (0, 0))
        screen.blit(self.font_title.render("LAST ROOF", True, WHITE), (120, 110))
        screen.blit(self.font_big.render("Escape City", True, ORANGE), (124, 164))
        menu_lines = [
            "ENTER  Xem trailer & bat dau",
            "H      How To Play",
            "ESC    Thoat",
        ]
        y = 280
        for line in menu_lines:
            screen.blit(self.font_big.render(line, True, WHITE), (126, y))
            y += 44
        teaser = [
            "Sinh ton 2D theo chuong, co NPC va he goi y duong di.",
            "Bam TAB trong game de doi BFS / DFS / SAFE / A*.",
        ]
        y = 500
        for line in teaser:
            screen.blit(self.font.render(line, True, WHITE), (126, y))
            y += 28
        if self.show_help:
            help_rect = pygame.Rect(520, 100, 330, 280)
            pygame.draw.rect(screen, PANEL, help_rect)
            pygame.draw.rect(screen, CYAN, help_rect, 2)
            lines = [
                "WASD: Di chuyen",
                "E: Tuong tac / nhat do",
                "Q / Lan chuot: Doi sung",
                "1-2-3: Chon nhanh sung",
                "B: Mo shop vat pham",
                "TAB: Doi thuat toan tim duong",
                "M: Mo minimap lon",
                "ESC: Tam dung",
                "Muc tieu moi chuong o bang ben phai",
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
        ]
        weapon_cards = {
            "weapon_pistol": CARD_WEAPON_PISTOL,
            "weapon_minigun": CARD_WEAPON_MINIGUN,
            "weapon_flamethrower": CARD_WEAPON_FLAMETHROWER,
            "weapon_grenadelauncher": CARD_WEAPON_GRENADE,
            "weapon_poisongun": CARD_WEAPON_POISON,
            "weapon_taesar": CARD_WEAPON_TAESAR,
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
                    self.popup = "Khong du tien."
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
                self.popup = f"Da mua: {title}"
                self.popup_timer = pygame.time.get_ticks() + 1400
                play_sound_effect("sfx_item_drop")
                return
            
    def draw(self):
        screen.fill(BLACK)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "intro":
            self.draw_intro()
        elif self.state in ["playing", "pause"]:
            self.draw_world()
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
                    self.trailer_started_at = pygame.time.get_ticks()
                    self.state = "intro"
                elif event.key == pygame.K_h:
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
                    self.state = "playing"
                elif btns.get("menu") and btns["menu"].collidepoint(mx, my):
                    self.state = "menu"
                elif btns.get("quit") and btns["quit"].collidepoint(mx, my):
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
