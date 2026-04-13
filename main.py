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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Last Roof: Escape City")
clock = pygame.time.Clock()

from enemy import FlyingEye, Goblin, Mushroom, Skeleton, BigFlyingEye, DashingGoblin, TeleportingMushroom, EvilWizard, OldGuardian
from pathfinding import a_star, bfs, dfs, greedy_safe
from player import Player
from weapon import WeaponManager
from all_graphics import ALL_GRAPHICS
from camera import Camera

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

TILE_SIZE = 16
GRID_SIZE = 44

# Tự động load toàn bộ card shop
SHOP_CARD_SURFACES = {}
for path in glob.glob("Shop_Cards/*.png"):
    try:
        img = pygame.image.load(path).convert_alpha()
        SHOP_CARD_SURFACES[path] = img
    except Exception as e:
        print(f"[SHOP CARD LOAD ERROR] {path}: {e}")

# Tự động load toàn bộ sound
SOUND_EFFECTS = {}
for path in glob.glob("Sounds/*.mp3"):
    try:
        SOUND_EFFECTS[path] = pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[SOUND LOAD ERROR] {path}: {e}")

# Hàm phát nhạc nền
def play_bg_music():
    try:
        pygame.mixer.music.load("Sounds/Game_loop_music.mp3")
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[MUSIC ERROR] {e}")

# Hàm lấy card shop ngẫu nhiên
def get_random_shop_card():
    import random
    if SHOP_CARD_SURFACES:
        return random.choice(list(SHOP_CARD_SURFACES.values()))
    return None

# Hàm phát hiệu ứng âm thanh
def play_sound_effect(name):
    for path, snd in SOUND_EFFECTS.items():
        if name.lower() in path.lower():
            snd.play()
            break

# Hàm lấy pet/card/weapon ngẫu nhiên (ví dụ)
def get_random_pet_card():
    pet_cards = [k for k in SHOP_CARD_SURFACES if "Pet" in k]
    if pet_cards:
        return SHOP_CARD_SURFACES[random.choice(pet_cards)]
    return None


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


DESERT_TILE = safe_load("Sprites/Sprites_Environment/desert_tile.png", (TILE_SIZE, TILE_SIZE))
DESERT_TILE_ALT = safe_load("Sprites/Sprites_Environment/desert_tile2.png", (TILE_SIZE, TILE_SIZE))
DESERT_GRASS = safe_load("Sprites/Sprites_Environment/desert_grass_patch.png", (TILE_SIZE, TILE_SIZE))
DESERT_GRASS_TUFT = safe_load("Sprites/Sprites_Environment/desert_grass.png", (TILE_SIZE, TILE_SIZE))
DESERT_ROCK = safe_load("Sprites/Sprites_Environment/desert_rock_tile.png", (TILE_SIZE, TILE_SIZE))
DESERT_WALL = DESERT_ROCK.copy()
DESERT_WALL.fill((40, 40, 52), special_flags=pygame.BLEND_RGB_MULT)
DESERT_HUT = safe_load("Sprites/Sprites_Environment/desert_Hut.png", (64, 64))
DESERT_BIG_GRASS = safe_load("Sprites/Sprites_Environment/desert_big_grass.png", (44, 44))
DESERT_BIG_ROCK = safe_load("Sprites/Sprites_Environment/desert_big_rock.png", (54, 54))
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

ITEM_SURFACES = {
    "heal": safe_load("Sprites/Sprites_Weapon/Grenade-2.png", (24, 24)), # Use grenade as medkit icon for now or another
    "armor": safe_load("Sprites/Sprites_Effect/Pet_Power.png", (24, 24)),
    "ammo": safe_load("Sprites/Sprites_Weapon/Amo1.png", (20, 20)),
    "weapon": safe_load("Sprites/Sprites_Weapon/Shotgun-4.png", (34, 24)),
    "rocket_weapon": safe_load("Sprites/Sprites_Weapon/RPG-reisized.png", (38, 38)),
    "gate": safe_load("Sprites/Sprites_Weapon/Amo6.png", (24, 24)),
    "signal": safe_load("Sprites/Sprites_Weapon/AmoB1.png", (24, 24)),
    "flare": safe_load("Sprites/Sprites_Weapon/Grenade-1.png", (24, 24)),
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
        if distance < 4:
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
        if cid == "roof":
            return [
                ("Nhat vu khi co ban", d["weapon_collected"]),
                ("Tieu diet zombie dau tien", d["zombies_killed"] >= 1),
                ("San sang vao man choi chinh", d["weapon_collected"] and d["zombies_killed"] >= 1),
            ]
        if cid == "office":
            return [
                ("Tim the tu cua bao ve", d["keycard_collected"]),
                ("Khoi phuc dien hanh lang", d["power_restored"]),
                ("Gap NPC bao ve", d["npc_saved"] >= 1),
                ("Toi cau thang xuong tang 2", d["gate_opened"]),
            ]
        if cid == "medical":
            return [
                ("Thu thap kho thuoc", d["supply_cache"]),
                ("Ha zombie dac biet", d["special_kills"] >= 3),
                ("Ho tro y ta song sot", d["npc_saved"] >= 1),
                ("Mo duong xuong tang 1", d["gate_opened"]),
            ]
        if cid == "escape":
            return [
                ("Ha boss Old Guardian", d["boss_down"]),
                ("Cho truc thang den (1 phut)", d.get("helicopter_arrived", False)),
                ("Len truc thang de thoat", False)
            ]
        return [
            ("Mo cong ra san", d["gate_opened"]),
            ("Kich hoat tin hieu cuu ho", d["signal_started"]),
            ("Tru vung toi khi truc thang toi", d["holdout_complete"]),
            ("Ha boss dot bien", d["boss_down"]),
        ]

    def complete(self):
        return all(done for _, done in self.objectives())


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
        self.story_flags = set()
        self.last_hint_path = []
        self.last_spawn_at = 0
        self.shot_counter = 0
        self.frenzy_window_until = 0
        self.kill_count = 0
        self.saved_npcs = 0
        self.end_reason = ""
        
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

        roof_blocked = ring_walls()
        for x in range(8, 35):
            roof_blocked.add((x, 12))
        for x in range(10, 26):
            roof_blocked.add((x, 28))
        for y in range(12, 29):
            roof_blocked.add((28, y))
        for pos in [(14, 12), (22, 28), (28, 20), (35, 34)]:
            roof_blocked.discard(pos)
        roof_items = [
            ItemPickup((6, 7), "Shotgun", "Một khẩu shotgun còn hoạt động.", "weapon", color=ORANGE),
            ItemPickup((10, 31), "Bandage", "Bang gac tu tui cuu ho san thuong.", "heal", amount=25),
        ]
        roof_npcs = [
            NPC("Phi cong", (38, 5), ["Toi chi lien lac duoc qua bo dam.", "Xuong cac tang duoi, mo cong san va goi tin hieu."], reward="radio", portrait_color=YELLOW),
        ]
        roof_enemies = [
            (Goblin, (18, 7), "basic"),
            (FlyingEye, (31, 18), "fast"),
            (Goblin, (35, 31), "basic"),
            (Goblin, (12, 20), "basic"),
            (FlyingEye, (24, 34), "fast"),
        ]

        office_blocked = ring_walls()
        # Chỉ để lại một số vật cản nhỏ ở map office, không tạo tường kín
        # Ví dụ: chỉ để các vật cản ở góc hoặc một số điểm
        for pos in [(8, 10), (14, 15), (22, 18), (30, 12), (35, 20), (10, 28), (28, 30)]:
            office_blocked.add(pos)
        office_items = [
            ItemPickup((8, 6), "Keycard", "The tu mo cua an ninh tang 3.", "keycard", color=BLUE),
            ItemPickup((35, 28), "Fuse", "Cau chi phu cho dien hanh lang.", "power", color=YELLOW),
            ItemPickup((14, 20), "Katana", "Thanh kiem nhat gia: Sac lem va toc do cao.", "weapon", weapon_data={
                "name": "Katana", "fire_rate": 2.5, "reload_time": 0.0,
                "image_path": "Sprites/Sprites_Weapon/Sniper-rifle-1.png",
                "projectile_speed": 0, "damage": 110, "projectile_scale": (48, 48), "type": "melee"
            }),
            ItemPickup((24, 5), "Ammo", "Dan du tru tu phong nhan su.", "ammo", amount=18, color=WHITE),
        ]
        office_npcs = [
            NPC("Bao ve Nam", (21, 17), ["Toi giu duoc phong camera nhung cua dang ket.", "Lay the tu, gan cau chi roi mo loi xuong."], reward="map", portrait_color=BLUE),
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
        # Giảm số lượng tường ở màn 3 để dễ di chuyển hơn
        # Chỉ để một số vật cản nhỏ, không tạo tường kín
        for pos in [(8, 12), (14, 15), (22, 18), (30, 12), (35, 20), (10, 28), (28, 30), (18, 24), (24, 22), (34, 28)]:
            med_blocked.add(pos)
        med_items = [
            ItemPickup((6, 6), "Medkit", "Mot hop cuu thuong lon trong phong cap cuu.", "heal", amount=50),
            ItemPickup((19, 20), "Armor Vest", "Ao giap nhe giup giam sat thuong.", "armor", amount=25, color=CYAN),
            ItemPickup((10, 26), "Rocket Launcher", "Vu khi no manh de quet dam dong zombie.", "rocket_weapon", color=ORANGE),
            ItemPickup((37, 33), "Control Fuse", "Thiet bi mo cong tang 1.", "exit", color=YELLOW),
            ItemPickup((27, 8), "Rifle Ammo", "Dan hiem cho sung truong.", "ammo", amount=28, color=WHITE),
        ]
        med_npcs = [
            NPC("Y ta Linh", (18, 7), ["Toi van con giu duoc kho thuoc.", "Neu cau lay duoc nguon dien, toi se chi duong xuong tang 1."], reward="medkit", portrait_color=GREEN),
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
        for x in range(6, 37):
            ground_blocked.add((x, 12))
        for x in range(8, 32):
            ground_blocked.add((x, 24))
        for y in range(6, 33):
            ground_blocked.add((10, y))
            ground_blocked.add((24, y))
        for pos in [(10, 18), (24, 8), (24, 29), (18, 12), (30, 12), (16, 24), (30, 24)]:
            ground_blocked.discard(pos)
        ground_items = [
            ItemPickup((7, 7), "Gate Switch", "Cong tac mo cong san.", "gate", color=ORANGE),
            ItemPickup((34, 29), "Signal Beacon", "Thiet bi phat tin hieu cho truc thang.", "signal", color=YELLOW),
            ItemPickup((38, 36), "Rescue Flare", "Phao sang dung de xac nhan vi tri ha canh.", "flare", color=RED),
        ]
        ground_npcs = [
            NPC("Ky thuat vien Huy", (17, 18), ["Toi giu duoc bo phat o san.", "Mo cong roi bat beacon, toi se cau gio cho cau."], reward="shortcut", portrait_color=ORANGE),
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
                {(5, 5): "grass", (32, 6): "hut", (25, 33): "rock"},
                roof_items,
                roof_npcs,
                roof_enemies,
                ORANGE,
                "Phi cong: Neu con nghe thay toi, hay xuong cac tang duoi va mo cong san.",
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
                {(6, 7): "hut", (22, 16): "rock", (34, 29): "grass"},
                office_items,
                office_npcs,
                office_enemies,
                BLUE,
                "Bao ve Nam: Toi thay cau thang ky thuat o goc dong nam. Nhung phai co dien.",
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
                {(7, 6): "hut", (27, 8): "rock", (18, 31): "grass"},
                med_items,
                med_npcs,
                med_enemies,
                GREEN,
                "Y ta Linh: Cong tang 1 chi mo neu cap dien dung tuyen ky thuat.",
                spawn_pool=[Goblin, Mushroom, TeleportingMushroom, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=3000,
            ),
            Chapter(
                "ground",
                "Chuong 4: Tang 1 - Sanh chinh",
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
                "Chuong 5: San bay - Thoat hiem",
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

        for enemy_cls, grid_pos, archetype in self.chapter.enemy_plan:
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

    def current_tile(self):
        return (int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE))

    def item_at_player(self):
        player_tile = self.current_tile()
        for item in self.chapter.items:
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
            projectile_image=weapon_data.get("projectile_image", "Sprites/Sprites_Effect/Bullets/14.png"),
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

        weapon_data = dict(random.choice(WEAPON_DROP_POOL))
        # Find the sprite surface for this weapon
        wp_sprite = ALL_GRAPHICS_SURFACES.get(weapon_data["image_path"])
        if wp_sprite:
            wp_sprite = pygame.transform.scale(wp_sprite, (32, 24))

        self.chapter.items.append(
            ItemPickup(
                (tile_x, tile_y),
                weapon_data["name"],
                f"Zombie da roi {weapon_data['name']}. Bam E de nhat.",
                "weapon_drop",
                color=ORANGE,
                weapon_data=weapon_data,
                sprite_surface=wp_sprite
            )
        )

    def collect_item(self, item):
        item.collected = True
        self.popup = item.description
        self.popup_timer = pygame.time.get_ticks() + 2600
        if item.item_type == "weapon":
            self.mission.data["weapon_collected"] = True
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
                self.queue_story_lines("Y ta Linh", ["Lay them bang gac va thuoc tang luc neu thay.", "Tang duoi nguy hiem hon nhieu."], GREEN)
        elif item.item_type == "ammo":
            self.popup = f"Nhat {item.amount} vien dan du tru."
        elif item.item_type == "armor":
            self.player.add_armor(item.amount)
            self.mission.data["supply_cache"] = True
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
        elif item.item_type == "power":
            self.popup = "Da lay cau chi. Toi hop dien de khoi phuc nguon."
            self.queue_story_dialog("Radio", "Dien phu dang o trang thai offline. Hay lap cau chi ngay.", YELLOW)
        elif item.item_type == "exit":
            self.mission.data["supply_cache"] = True
            self.popup = "Thiet bi dieu khien cong da co trong tay."
            self.queue_story_dialog("Hero", "Mo duoc cong tang 1 roi. Phai tiep tuc di chuyen.", ORANGE)
        elif item.item_type == "gate":
            self.mission.data["gate_opened"] = True
            self.popup = "Cong san da mo. Di toi beacon."
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
        elif cid == "office":
            if self.mission.data["keycard_collected"]:
                self.mission.data["power_restored"] = True
                self.mission.data["gate_opened"] = True
                self.popup = "Dien da tro lai. Thang ky thuat tang 2 da mo."
                self.remove_gate_collision((37, 35))
            else:
                self.popup = "Can the tu truoc khi kich hoat lai hanh lang."
        elif cid == "medical":
            self.mission.data["gate_opened"] = True
            self.popup = "Loi xuong tang 1 da duoc mo."
            self.remove_gate_collision((39, 35))
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
        self.dialog_lines = list(npc.lines)
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

            keys = pygame.key.get_pressed()
            self.player.update(keys, self.current_blocked, None, None, TILE_SIZE)
            self.player.x = max(TILE_SIZE, min(self.player.x, self.world_w - TILE_SIZE))
            self.player.y = max(TILE_SIZE, min(self.player.y, self.world_h - TILE_SIZE))
            
            self.camera.update(self.player.x, self.player.y, self.world_w, self.world_h)
            
            self.update_enemies()
            self.spawn_dynamic_enemies()
            
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
            self.update_hint_path()
            
            if self.chapter.id == "escape" and hasattr(self, 'rescue_arrived') and self.rescue_arrived:
                # Kiem tra xem nguoi choi da den Helipad chua
                dist_to_extract = math.hypot(self.player.x - 38*TILE_SIZE, self.player.y - 36*TILE_SIZE)
                if dist_to_extract < 64:
                    self.state = "win"

            if self.player.health <= 0:
                self.end_reason = "Ban da bi zombie ap dao truoc khi thoat duoc khoi thanh pho."
                self.state = "lose"

    def spawn_dynamic_enemies(self):
        import random
        now = pygame.time.get_ticks()
        alive = [entry for entry in self.story_enemies if not entry.enemy.is_dead]
        if len(alive) >= self.chapter.max_alive_enemies:
            return
        if not self.chapter.spawn_pool:
            return
        # Enemy spawn ngẫu nhiên trên map lớn
        px, py = int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE)
        for _ in range(2):
            gx = px + random.randint(-40, 40)
            gy = py + random.randint(-40, 40)
            if abs(gx - px) + abs(gy - py) < 10:
                continue
            enemy_cls = random.choice(self.chapter.spawn_pool)
            ex = gx * TILE_SIZE + TILE_SIZE // 2
            ey = gy * TILE_SIZE + TILE_SIZE // 2
            enemy = enemy_cls(ex, ey)
            enemy.obstacle_map = self.build_obstacle_grid()
            archetype = "basic"
            self.story_enemies.append(StoryEnemy(enemy, archetype, (gx, gy)))

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
        self.popup = "Them zombie dang do vao khu vuc."
        self.popup_timer = now + 1500

    def update_enemies(self):
        for entry in self.story_enemies:
            enemy = entry.enemy
            enemy.obstacle_map = self.build_obstacle_grid()
            enemy.update(self.player)
            enemy.x = max(TILE_SIZE, min(enemy.x, MAP_WIDTH - TILE_SIZE))
            enemy.y = max(TILE_SIZE, min(enemy.y, MAP_HEIGHT - TILE_SIZE))
            if enemy.is_dead and not entry.dead_registered:
                entry.dead_registered = True
                self.kill_count += 1
                self.mission.data["zombies_killed"] += 1
                if entry.archetype in {"special", "tank"}:
                    self.mission.data["special_kills"] += 1
                if entry.archetype == "boss":
                    self.mission.data["boss_down"] = True
                self.spawn_weapon_drop(enemy.x, enemy.y)
        self.story_enemies = [
            entry for entry in self.story_enemies
            if not (entry.enemy.is_dead and entry.enemy.death_animation_completed)
        ]

    def handle_progression(self):
        if self.chapter.id == "roof" and self.mission.data["zombies_killed"] >= 1 and "roof_first_kill" not in self.story_flags:
            self.story_flags.add("roof_first_kill")
            self.queue_story_lines("Nhan vat chinh", ["Con dau tien da guc.", "Minh phai lay do roi mo loi xuong ngay."], ORANGE)
        if self.chapter.id == "roof" and self.mission.data["weapon_collected"] and self.mission.data["zombies_killed"] >= 1:
            self.mission.data["medkit_collected"] = True
            self.mission.data["power_restored"] = True
        if self.chapter.id == "office" and self.mission.data["power_restored"] and "office_power" not in self.story_flags:
            self.story_flags.add("office_power")
            self.queue_story_lines("Bao ve Nam", ["Dien da len. Camera cho thay cau thang ky thuat da mo.", "Di nhanh len, chung dang ap sat tu hanh lang sau."], BLUE)
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
                self.holdout_until = pygame.time.get_ticks() + 60 * 1000  # 1 phút
                self.queue_story_lines("Phi cong", ["Da xac nhan muc tieu nguy hiem bi ha.", "Dang bay toi vi tri. Giu vung trong 1 phut!"], YELLOW)

            if getattr(self, "countdown_started", False) and pygame.time.get_ticks() >= self.holdout_until and not getattr(self, "rescue_arrived", False):
                self.rescue_arrived = True
                self.mission.data["helicopter_arrived"] = True
                self.queue_story_lines("Phi cong", ["Truc thang da ha canh! Len nhanh nao!"], YELLOW)

        if self.mission.complete() or (self.chapter.id == "escape" and getattr(self, "rescue_arrived", False)) and not self.next_chapter_ready:
            self.next_chapter_ready = True
            if self.chapter.id == "roof":
                self.popup = "Hoan thanh man khoi dong. Nhan ENTER de bat dau Chuong 2."
            if self.chapter.id == "escape":
                self.popup = "CHO TRUC THANG HA CANH... CHAY DEN DIEM EXTRACT!"
                self.rescue_arrived = True # Flag for win condition at Helipad
            elif self.chapter_index == len(self.chapters) - 1:
                self.popup = "Da hoan thanh nhiem vu cuoi. Nhan ENTER de len truc thang."
            else:
                self.popup = "Da hoan thanh man choi. Nhan ENTER de sang man tiep theo."
            self.popup_timer = pygame.time.get_ticks() + 4000

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
        if chapter_id == "roof":
            if not self.mission.data["weapon_collected"]:
                return (6, 7)
            return (18, 7)
        if chapter_id == "office":
            if not self.mission.data["keycard_collected"]:
                return (8, 6)
            if not self.mission.data["npc_saved"]:
                return (21, 17)
            if not self.mission.data["power_restored"]:
                return (34, 28)
            return self.chapter.exit_pos
        if chapter_id == "medical":
            if not self.mission.data["npc_saved"]:
                return (18, 7)
            if not self.mission.data["supply_cache"]:
                return (6, 6)
            if not self.mission.data["gate_opened"]:
                return (37, 33)
            return self.chapter.exit_pos
        if not self.mission.data["gate_opened"]:
            return (7, 7)
        if not self.mission.data["signal_started"]:
            return (34, 29)
        return self.chapter.exit_pos

    def objective_label(self):
        cid = self.chapter.id
        if cid == "roof":
            if not self.mission.data["weapon_collected"]:
                return "Nhat sung"
            if self.mission.data["zombies_killed"] < 1:
                return "Ha 1 zombie de hoan tat man khoi dong"
            return "Nhan ENTER de vao man 2"
        if cid == "office":
            if not self.mission.data["keycard_collected"]:
                return "Tim the tu"
            if not self.mission.data["npc_saved"]:
                return "Noi chuyen voi bao ve"
            if not self.mission.data["power_restored"]:
                return "Khoi phuc dien"
            return "Di toi cau thang xuong tang 2"
        if cid == "medical":
            if not self.mission.data["npc_saved"]:
                return "Noi chuyen voi y ta Linh"
            if not self.mission.data["supply_cache"]:
                return "Lay vat tu y te"
            if not self.mission.data["gate_opened"]:
                return "Mo loi xuong tang 1"
            return "Di xuong tang 1"
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

    def render_world(self, surface):
        # Get visible tile range from camera
        min_tx, max_tx, min_ty, max_ty = self.camera.get_visible_tile_range(TILE_SIZE)
        
        # 1. Background Backdrop
        self.draw_chapter_backdrop(surface)
        
        # 2. Tiles
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                base_tile = DESERT_TILE_ALT if (tx * 3 + ty * 5) % 11 == 0 else DESERT_TILE
                sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
                surface.blit(base_tile, (sx, sy))
                
                # Vẽ bức tường (vật cản)
                if (tx, ty) in self.current_blocked:
                    # Sử dụng sprite gạch đá tông tối để trông chuyên nghiệp hơn
                    surface.blit(DESERT_WALL, (sx, sy))
                    pygame.draw.rect(surface, (20, 20, 30), (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                elif (tx + ty) % 9 == 0:
                    surface.blit(DESERT_GRASS, (sx, sy))
                elif (tx * 7 + ty * 3) % 19 == 0:
                    surface.blit(DESERT_GRASS_TUFT, (sx, sy))
                
                # Ve vat trang tri Chapter
                prop = self.chapter.decor_tiles.get((tx, ty))
                if prop:
                    if prop == "hut": surface.blit(DESERT_HUT, (sx, sy - 32))
                    elif prop == "rock": surface.blit(DESERT_BIG_ROCK, (sx, sy))
                    elif prop == "grass": surface.blit(DESERT_BIG_GRASS, (sx, sy))
                    elif prop == "heli_pad" and hasattr(self, 'rescue_arrived') and self.rescue_arrived:
                        # Draw Heli-pad and Rescue Helidrop
                        pygame.draw.rect(surface, YELLOW, (sx-32, sy-32, 96, 96), 3)
                        screen.blit(HELICOPTER, (sx-75, sy-75))
                    
        for item in self.chapter.items:
            if item.collected: continue
            if self.camera.is_visible(item.grid_pos[0]*TILE_SIZE, item.grid_pos[1]*TILE_SIZE):
                sx, sy = self.camera.world_to_screen(item.grid_pos[0]*TILE_SIZE, item.grid_pos[1]*TILE_SIZE)
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

        minimap_frame = pygame.Rect(MAP_WIDTH + 14, 312, SIDEBAR_WIDTH - 28, 214)
        self.draw_card(minimap_frame, self.chapter.chapter_color, title="Minimap", subtitle="Muc tieu va duong di")
        minimap_rect = pygame.Rect(minimap_frame.x + 12, minimap_frame.y + 44, minimap_frame.width - 24, 152)
        self.draw_minimap(minimap_rect)

        info_rect = pygame.Rect(MAP_WIDTH + 14, 536, SIDEBAR_WIDTH - 28, 86)
        self.draw_card(info_rect, CYAN, title="Thong tin", subtitle=f"Zombie: {self.kill_count}  |  NPC: {self.saved_npcs}")
        y = info_rect.y + 48
        stats = [
            "Chuot trai ban  |  E nhat",
            "Q doi sung  |  ENTER qua man",
            f"Thuat toan: {self.hint_modes[self.hint_mode_index]}",
        ]
        for line in stats:
            screen.blit(self.font_small.render(line, True, SOFT), (info_rect.x + 14, y))
            y += 18

        asset_rect = pygame.Rect(MAP_WIDTH + 14, 632, SIDEBAR_WIDTH - 28, 160)
        self.draw_card(asset_rect, ORANGE, title="Loadout & Ho tro", subtitle="Card asset dang dung")
        cards = [self.current_weapon_card(), CARD_PET_BIRD, CARD_PET_FOX, CARD_BUILD_MORTAR if self.chapter.id != "ground" else CARD_BUILD_CANNON]
        cx = asset_rect.x + 12
        for card in cards:
            screen.blit(card, (cx, asset_rect.y + 46))
            cx += 56

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
        dialog_rect = pygame.Rect(42, MAP_HEIGHT - 214, 628, 160)
        self.draw_card(dialog_rect, self.dialog_color)
        portrait_center = (dialog_rect.x + 42, dialog_rect.y + 40)
        pygame.draw.circle(screen, self.dialog_color, portrait_center, 22)
        pygame.draw.circle(screen, WHITE, portrait_center, 22, 2)
        pygame.draw.circle(screen, BLACK, (portrait_center[0], portrait_center[1] - 5), 4)
        pygame.draw.circle(screen, BLACK, (portrait_center[0] - 8, portrait_center[1] - 5), 3)
        pygame.draw.circle(screen, BLACK, (portrait_center[0] + 8, portrait_center[1] - 5), 3)
        screen.blit(self.font_big.render(self.dialog_speaker, True, self.dialog_color), (dialog_rect.x + 78, dialog_rect.y + 14))
        y = dialog_rect.y + 60
        for line in self.dialog_lines:
            for wrapped in wrap_text(line, self.font, dialog_rect.width - 40):
                screen.blit(self.font.render(wrapped, True, WHITE), (dialog_rect.x + 20, y))
                y += 22
        screen.blit(self.font_small.render("ENTER hoặc E để tiếp tục hội thoại", True, SOFT), (dialog_rect.x + 20, dialog_rect.y + 130))

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
        overlay.fill((10, 8, 12, 180))
        screen.blit(overlay, (0, 0))
        screen.blit(self.font_title.render("PAUSE", True, WHITE), (180, 160))
        lines = ["ESC de tiep tuc", "B de vao Shop", "M de mo ban do"]
        for i, line in enumerate(lines):
            screen.blit(self.font_big.render(line, True, WHITE), (160, 260 + i * 50))

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
        
        # Grid of cards
        all_cards = list(SHOP_CARD_SURFACES.values())
        for i, card in enumerate(all_cards[:20]):
            r, c = i // 5, i % 5
            cx = shop_rect.x + 60 + c * 160
            cy = shop_rect.y + 120 + r * 140
            
            # Draw card with border
            screen.blit(CARD_BORDER, (cx-4, cy-4))
            screen.blit(pygame.transform.scale(card, (140, 110)), (cx+5, cy+5))
            
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
                        self.dialog_npc = None
                        # Advance queue if needed
                    return

                if event.key == pygame.K_q:
                    self.weapon_manager.cycle_weapon()
                if event.key == pygame.K_RETURN:
                    if self.next_chapter_ready:
                        if self.chapter_index < len(self.chapters) - 1:
                            self.set_chapter(self.chapter_index + 1)
                            self.state = "playing"
                        else:
                            self.state = "win"
                    return

                if event.key == pygame.K_b:
                    self.show_shop = not self.show_shop
                if self.show_shop: return

                if event.key == pygame.K_ESCAPE:
                    self.state = "pause"
                elif event.key == pygame.K_m:
                    self.show_map = not self.show_map
                elif event.key == pygame.K_TAB:
                    self.hint_mode_index = (self.hint_mode_index + 1) % len(self.hint_modes)
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
        
        if self.state in ["win", "lose"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.__init__()
                self.state = "playing"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down = True
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
