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

# Định nghĩa các màu cơ bản
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 128, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

"""
Shop chọn card (vũ khí, pet, hiệu ứng) xuất hiện khi nhấn S.
Đổi nhạc nền khi qua màn hoặc khi vào boss.
Hiệu ứng âm thanh khi bắn, trúng địch, dùng kỹ năng, mở rương.
Hiển thị pet đồng hành và cho phép đổi pet.
Hiển thị card shop, pet, weapon ngẫu nhiên khi mở shop.
Hướng dẫn phím tắt mới trên giao diện.
"""
import math
import os
import random
import sys
from dataclasses import dataclass, field

import pygame

from enemy import FlyingEye, Goblin, Mushroom, Skeleton, BigFlyingEye, DashingGoblin, TeleportingMushroom
from pathfinding import a_star, bfs, dfs, greedy_safe
from player import Player
from weapon import WeaponManager
from all_graphics import ALL_GRAPHICS

pygame.init()

# Tự động load toàn bộ file đồ họa vào dict ALL_GRAPHICS_SURFACES
ALL_GRAPHICS_SURFACES = {}
for path in ALL_GRAPHICS:
    try:
        img = pygame.image.load(path).convert_alpha()
        ALL_GRAPHICS_SURFACES[path] = img
    except Exception as e:
        print(f"[GRAPHICS LOAD ERROR] {path}: {e}")
from skill import SkillManager, Skill


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


pygame.init()


TILE_SIZE = 16
GRID_SIZE = 44
# SCREEN_WIDTH và SCREEN_HEIGHT sẽ được lấy từ infoObject phía dưới
MAP_WIDTH = TILE_SIZE * GRID_SIZE
MAP_HEIGHT = TILE_SIZE * GRID_SIZE
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- FULLSCREEN + TỰ ĐỘNG LOAD ASSET ---
SIDEBAR_WIDTH = 256
import glob
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
MAP_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("San thuong cuoi: Thoat khoi thanh pho")
clock = pygame.time.Clock()

# Tự động load toàn bộ file đồ họa vào dict ALL_GRAPHICS_SURFACES
ALL_GRAPHICS_SURFACES = {}
for path in ALL_GRAPHICS:
    try:
        img = pygame.image.load(path).convert_alpha()
        ALL_GRAPHICS_SURFACES[path] = img
    except Exception as e:
        print(f"[GRAPHICS LOAD ERROR] {path}: {e}")

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

WEAPON_DROP_POOL = [
    {
        "name": "AK-47",
        "fire_rate": 6.2,
        "reload_time": 1.0,
        "image_path": "Sprites/Sprites_Weapon/Assaut-rifle-3-scoped.png",
        "projectile_speed": 9,
        "damage": 48,
        "projectile_scale": (36, 36),
    },
    {
        "name": "SMG",
        "fire_rate": 9.0,
        "reload_time": 0.9,
        "image_path": "Sprites/Sprites_Weapon/SMG-4.png",
        "projectile_speed": 10,
        "damage": 34,
        "projectile_scale": (34, 34),
    },
    {
        "name": "Sniper",
        "fire_rate": 1.2,
        "reload_time": 1.8,
        "image_path": "Sprites/Sprites_Weapon/Sniper-rifle-2-scoped.png",
        "projectile_speed": 12,
        "damage": 170,
        "projectile_scale": (42, 42),
    },
]


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
        return [
            ("Mo cong ra san", d["gate_opened"]),
            ("Kich hoat tin hieu cuu ho", d["signal_started"]),
            ("Tru vung toi khi truc thang toi", d["holdout_complete"]),
            ("Ha boss dot bien", d["boss_down"]),
        ]

    def complete(self):
        return all(done for _, done in self.objectives())


class Game:
    def __init__(self):
        self.font = load_ui_font(22)
        # Pet mặc định (nếu chưa chọn pet, sẽ là PET_BIRD)
        self.current_pet = PET_BIRD
        self.font_big = load_ui_font(40, bold=True)
        self.font_title = load_ui_font(64, bold=True)
        self.font_small = load_ui_font(18)
        self.player = Player(120, 120)
        self.weapon_manager = WeaponManager()
        # --- Kỹ năng ---
        self.skill_manager = SkillManager()
        # Thêm kỹ năng mẫu, bạn có thể thêm nhiều kỹ năng khác nhau ở đây
        self.skill_manager.add_skill(Skill(
            "Fireball", 2000, "Sprites/Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_05.png",
            effect_image_path="Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif",
            scale=(40,40), effect_scale=(48,48)
        ))
        self.skill_manager.add_skill(Skill(
            "Ice Blast", 3000, "Sprites/Sprites_Effect/Bullets/Introl Blue Effect Bullet Impact Explosion 32x32.gif",
            effect_image_path="Sprites/Sprites_Effect/Bullets/Introl Blue Effect Bullet Impact Explosion 32x32.gif",
            scale=(40,40), effect_scale=(48,48)
        ))
        self.skill_manager.add_skill(Skill(
            "Green Wave", 2500, "Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif",
            effect_image_path="Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif",
            scale=(40,40), effect_scale=(48,48)
        ))
        # ---
        self.mouse_down = False
        self.shot_counter = 0
        self.frenzy_until = 0
        self.frenzy_window_until = 0
        self.state = "menu"
        self.show_help = False
        self.show_map = False
        self.debug_path = True
        self.hint_mode_index = 0
        self.hint_modes = ["BFS", "DFS", "SAFE", "A*"]
        self.radio_log = []
        self.popup = ""
        self.popup_timer = 0
        self.dialog_npc = None
        self.dialog_speaker = ""
        self.dialog_color = CYAN
        self.dialog_lines = []
        self.dialog_choice = 0
        self.dialog_queue = []
        self.story_flags = set()
        self.kill_count = 0
        self.saved_npcs = 0
        self.next_chapter_ready = False
        self.last_objective_text = ""
        self.objective_flash_until = 0
        self.chapter_card_timer = 0
        self.intro_index = 0
        self.trailer_started_at = 0
        self.end_reason = ""
        self.chapter_index = 0
        self.last_hint_path = []
        self.beacon_started_at = 0
        self.holdout_until = 0
        self.last_spawn_at = 0
        self.stats_start = pygame.time.get_ticks()
        self.chapters = self.build_chapters()
        self.chapter = None
        self.mission = None
        self.story_enemies = []
        self.current_blocked = set()
        self.power_boxes = []
        self.gates = []
        self.heli_zone = None
        self.tank = EscortTank(120, 120)
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
            ItemPickup((24, 5), "Ammo", "Dan du tru tu phong nhan su.", "ammo", amount=18, color=WHITE),
        ]
        office_npcs = [
            NPC("Bao ve Nam", (21, 17), ["Toi giu duoc phong camera nhung cua dang ket.", "Lay the tu, gan cau chi roi mo loi xuong."], reward="map", portrait_color=BLUE),
        ]
        office_enemies = [
            (Goblin, (9, 17), "basic"),
            (DashingGoblin, (24, 16), "fast"),
            (FlyingEye, (33, 6), "fast"),
            (Goblin, (35, 31), "basic"),
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
            (DashingGoblin, (35, 9), "fast"),
            (Mushroom, (28, 18), "tank"),
            (Skeleton, (6, 28), "special"),
            (FlyingEye, (37, 24), "fast"),
            # Boss to, máu 100
            (BigFlyingEye, (33, 35), {"type": "boss", "health": 100}),
            (Goblin, (14, 27), "basic"),
            (DashingGoblin, (30, 31), "fast"),
        ]

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
                {(5, 5): "grass", (32, 6): "hut", (25, 33): "rock"},
                roof_items,
                roof_npcs,
                roof_enemies,
                ORANGE,
                "Phi công: Nếu còn nghe thấy tôi, hãy xuống các tầng dưới và mở cổng sân.",
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
                {(6, 7): "hut", (22, 16): "rock", (34, 29): "grass"},
                office_items,
                office_npcs,
                office_enemies,
                BLUE,
                "Bảo vệ Nam: Tôi thấy cầu thang kỹ thuật ở góc đông nam. Nhưng phải có điện.",
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
                {(7, 6): "hut", (27, 8): "rock", (18, 31): "grass"},
                med_items,
                med_npcs,
                med_enemies,
                GREEN,
                "Y tá Linh: Cổng tầng 1 chỉ mở nếu cấp điện đúng tuyến kỹ thuật.",
                spawn_pool=[Goblin, Mushroom, TeleportingMushroom, Skeleton],
                max_alive_enemies=12,
                spawn_interval_ms=3000,
            ),
            Chapter(
                "ground",
                "Chương 4: Tầng 1 và Sân",
                "Cuộc tháo chạy cuối cùng",
                ["Còi báo động rít lên. Cả tầng 1 bắt đầu đổ dồn zombie về phía sân.", "Bạn chỉ còn vài phút để mở cổng, kích hoạt tín hiệu và giữ vững vị trí."],
                ["Mở cổng sân", "Bật beacon", "Giữ vị trí", "Hạ boss đột biến"],
                (40, 37),
                (5, 5),
                ground_blocked,
                {(6, 6): "hut", (28, 18): "rock", (38, 36): "grass"},
                ground_items,
                ground_npcs,
                ground_enemies,
                RED,
                "Phi công: Khi beacon sáng, tôi cần cậu sống sót thêm một chút nữa.",
                holdout_seconds=25,
                chapter_type="holdout",
                spawn_pool=[Goblin, DashingGoblin, Skeleton, FlyingEye, Mushroom],
                max_alive_enemies=14,
                spawn_interval_ms=2600,
            ),
        ]

    def trailer_scenes(self):
        return [
            {
                "title": "Thành phố đã sụp đổ",
                "subtitle": "Virus lạ biến cả khu trung tâm thành ổ zombie chỉ sau một đêm.",
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
            # Nếu là boss cuối cùng và có dict health
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
        self.chapter.items.append(
            ItemPickup(
                (tile_x, tile_y),
                weapon_data["name"],
                f"Zombie da roi {weapon_data['name']}. Bam E de nhat.",
                "weapon_drop",
                color=ORANGE,
                weapon_data=weapon_data,
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
            self.queue_story_lines("Nhân vật chính", ["Được rồi, có thêm hỏa lực rồi.", "Giết 1 zombie nữa là xong màn khởi động."], ORANGE)
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
            self.queue_story_lines("Y tá Linh", ["Phia duoi dang co dam dong rat lon.", "Lay vu khi no nay, no se giup cau mo duong."], GREEN)
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
        if self.state != "playing":
            return
        keys = pygame.key.get_pressed()
        # Map vô hạn: không giới hạn MAP_WIDTH, MAP_HEIGHT
        self.player.update(keys, self.current_blocked, None, None, TILE_SIZE)
        self.update_enemies()
        self.spawn_dynamic_enemies_infinite()
        if self.chapter.id == "ground" and self.mission.data["gate_opened"]:
            self.tank.set_target(self.player.x - 40, self.player.y + 35)
        self.tank.update()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        shot_fired = self.weapon_manager.update(
            self.player.x,
            self.player.y,
            mouse_x,
            mouse_y,
            self.mouse_down and mouse_x < SCREEN_WIDTH - SIDEBAR_WIDTH,
            [entry.enemy for entry in self.story_enemies],
        )
        # Update kỹ năng
        self.skill_manager.update()
        self.update_frenzy(shot_fired)
        self.handle_progression()
        self.update_hint_path()
        # Spawn item ngẫu nhiên trên map lớn
        import random
        if hasattr(self, "chapter") and self.chapter and random.random() < 0.002:
            gx = random.randint(-100, 100)
            gy = random.randint(-100, 100)
            if not any(item.grid_pos == (gx, gy) for item in self.chapter.items):
                self.chapter.items.append(ItemPickup((gx, gy), "Random Item", "Vat pham ngau nhien", "heal", amount=10, color=YELLOW))
        if self.player.health <= 0:
            self.end_reason = "Ban da bi zombie ap dao truoc khi thoat duoc khoi thanh pho."
            self.state = "lose"

    def spawn_dynamic_enemies_infinite(self):
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
            self.queue_story_lines("Nhân vật chính", ["Con đầu tiên đã gục.", "Mình phải lấy đồ rồi mở lối xuống ngay."], ORANGE)
        if self.chapter.id == "roof" and self.mission.data["weapon_collected"] and self.mission.data["zombies_killed"] >= 1:
            self.mission.data["medkit_collected"] = True
            self.mission.data["power_restored"] = True
        if self.chapter.id == "office" and self.mission.data["power_restored"] and "office_power" not in self.story_flags:
            self.story_flags.add("office_power")
            self.queue_story_lines("Bảo vệ Nam", ["Điện đã lên. Camera cho thấy cầu thang kỹ thuật đã mở.", "Đi nhanh lên, chúng đang áp sát từ hành lang sau."], BLUE)
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
        if self.mission.complete() and not self.next_chapter_ready:
            self.next_chapter_ready = True
            if self.chapter.id == "roof":
                self.popup = "Hoàn thành màn khởi động. Nhấn ENTER để bắt đầu Chương 2."
            elif self.chapter_index == len(self.chapters) - 1:
                self.popup = "Đã hoàn thành nhiệm vụ cuối. Nhấn ENTER để lên trực thăng."
            else:
                self.popup = "Đã hoàn thành màn chơi. Nhấn ENTER để sang màn tiếp theo."
            self.popup_timer = pygame.time.get_ticks() + 4000

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
                return "Nhặt súng"
            if self.mission.data["zombies_killed"] < 1:
                return "Hạ 1 zombie để hoàn tất màn khởi động"
            return "Nhấn ENTER để vào màn 2"
        if cid == "office":
            if not self.mission.data["keycard_collected"]:
                return "Tìm thẻ từ"
            if not self.mission.data["npc_saved"]:
                return "Nói chuyện với bảo vệ"
            if not self.mission.data["power_restored"]:
                return "Khôi phục điện"
            return "Đi tới cầu thang xuống tầng 2"
        if cid == "medical":
            if not self.mission.data["npc_saved"]:
                return "Nói chuyện với y tá Linh"
            if not self.mission.data["supply_cache"]:
                return "Lấy vật tư y tế"
            if not self.mission.data["gate_opened"]:
                return "Mở lối xuống tầng 1"
            return "Đi xuống tầng 1"
        if not self.mission.data["gate_opened"]:
            return "Mở cổng ra sân"
        if not self.mission.data["signal_started"]:
            return "Kích hoạt đèn hiệu"
        return "Ra điểm trực thăng"

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
        world_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
        self.render_world(world_surface)
        # Vẽ hiệu ứng kỹ năng lên world_surface
        self.skill_manager.draw(world_surface)
        screen.blit(world_surface, (0, 0))

    def render_world(self, surface):
        self.draw_chapter_backdrop(surface)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                base_tile = DESERT_TILE_ALT if (x * 3 + y * 5) % 11 == 0 else DESERT_TILE
                surface.blit(base_tile, (x * TILE_SIZE, y * TILE_SIZE))
                if (x + y) % 9 == 0:
                    surface.blit(DESERT_GRASS, (x * TILE_SIZE, y * TILE_SIZE))
                elif (x * 7 + y * 3) % 19 == 0:
                    surface.blit(DESERT_GRASS_TUFT, (x * TILE_SIZE, y * TILE_SIZE))
        for (x, y), decor in self.chapter.decor_tiles.items():
            if decor == "rock":
                surface.blit(DESERT_ROCK, (x * TILE_SIZE, y * TILE_SIZE))
            elif decor == "hut":
                surface.blit(DESERT_HUT, (x * TILE_SIZE - 18, y * TILE_SIZE - 18))
            else:
                surface.blit(DESERT_GRASS, (x * TILE_SIZE, y * TILE_SIZE))
        for x in range(3, GRID_SIZE, 10):
            y = ((x * 7) + 9) % (GRID_SIZE - 6) + 2
            surface.blit(DESERT_BIG_GRASS, (x * TILE_SIZE - 10, y * TILE_SIZE - 10))
        for x in range(6, GRID_SIZE, 13):
            y = ((x * 5) + 13) % (GRID_SIZE - 6) + 2
            surface.blit(DESERT_BIG_ROCK, (x * TILE_SIZE - 14, y * TILE_SIZE - 14))
        self.draw_world_props(surface)
        for x, y in self.current_blocked:
            pygame.draw.rect(surface, (78, 63, 55), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        if self.last_hint_path:
            color = {"BFS": BLUE, "DFS": CYAN, "SAFE": GREEN, "A*": YELLOW}[self.hint_modes[self.hint_mode_index]]
            for tile in self.last_hint_path:
                px = tile[0] * TILE_SIZE + TILE_SIZE // 2
                py = tile[1] * TILE_SIZE + TILE_SIZE // 2
                pygame.draw.circle(surface, color, (px, py), 3)
        for item in self.chapter.items:
            if item.collected:
                continue
            if item.item_type == "rocket_weapon":
                icon_rect = ROCKET_PICKUP.get_rect(center=(item.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2, item.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2))
                surface.blit(ROCKET_PICKUP, icon_rect)
                pygame.draw.circle(surface, ORANGE, icon_rect.center, 14, 2)
            elif item.item_type == "weapon":
                icon_rect = SHOTGUN_PICKUP.get_rect(center=(item.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2, item.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2))
                surface.blit(SHOTGUN_PICKUP, icon_rect)
                pulse = 16 + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 6)
                pygame.draw.circle(surface, ORANGE, icon_rect.center, pulse, 2)
            elif item.item_type == "weapon_drop":
                drop_name = (item.weapon_data or {}).get("name", "")
                if "sniper" in drop_name.lower():
                    icon = SNIPER_PICKUP
                elif "smg" in drop_name.lower():
                    icon = SMG_PICKUP
                else:
                    icon = AK_PICKUP
                icon_rect = icon.get_rect(center=(item.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2, item.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2))
                surface.blit(icon, icon_rect)
                pulse = 12 + int(abs(math.sin(pygame.time.get_ticks() * 0.012)) * 5)
                pygame.draw.circle(surface, ORANGE, icon_rect.center, pulse, 2)
            else:
                rect = pygame.Rect(item.grid_pos[0] * TILE_SIZE + 2, item.grid_pos[1] * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                pygame.draw.rect(surface, item.color, rect, border_radius=4)
        for npc in self.chapter.npcs:
            color = GRAY if npc.interacted else npc.color
            center = (npc.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2, npc.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(surface, color, center, 7)
            pygame.draw.circle(surface, WHITE, center, 7, 1)
        if self.chapter.id == "ground":
            self.tank.draw(surface)
        self.draw_pet_companion(surface)
        self.player.draw(surface)
        self.weapon_manager.draw(surface)
        for entry in self.story_enemies:
            entry.enemy.draw(surface)
        goal = self.objective_tile()
        if goal:
            center = (goal[0] * TILE_SIZE + TILE_SIZE // 2, goal[1] * TILE_SIZE + TILE_SIZE // 2)
            pulse = 8 + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 6)
            pygame.draw.circle(surface, YELLOW, center, pulse, 2)
            pygame.draw.circle(surface, WHITE, center, 4)
        if self.chapter.exit_pos:
            exit_rect = pygame.Rect(self.chapter.exit_pos[0] * TILE_SIZE, self.chapter.exit_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.chapter.chapter_color, exit_rect, 2)
        self.draw_world_fx(surface)

    def draw_world_props(self, surface):
        prop_sets = {
            "roof": [(BUILD_ROCKET, 32, 6), (BUILD_MORTAR, 35, 34)],
            "office": [(BUILD_CANNON, 6, 30), (BUILD_ROCKET, 33, 5)],
            "medical": [(BUILD_MORTAR, 28, 27), (BUILD_CANNON, 8, 17)],
            "ground": [(BUILD_ROCKET, 36, 8), (BUILD_MORTAR, 12, 34), (BUILD_CANNON, 30, 30)],
        }
        for sprite, gx, gy in prop_sets.get(self.chapter.id, []):
            surface.blit(sprite, (gx * TILE_SIZE - 18, gy * TILE_SIZE - 18))

    def draw_pet_companion(self, surface):
        now = pygame.time.get_ticks()
        orbit_x = int(self.player.x - 34 + math.sin(now * 0.004) * 18)
        orbit_y = int(self.player.y + 22 + math.cos(now * 0.003) * 12)
        pet = self.current_pet
        surface.blit(pet, pet.get_rect(center=(orbit_x, orbit_y)))
        surface.blit(PET_POWER, PET_POWER.get_rect(center=(orbit_x + 10, orbit_y - 12)))

    def draw_chapter_backdrop(self, surface):
        top = self.chapter.chapter_color
        for y in range(MAP_HEIGHT):
            blend = y / max(1, MAP_HEIGHT - 1)
            color = (
                int(8 + top[0] * 0.08 + 20 * blend),
                int(10 + top[1] * 0.05 + 14 * blend),
                int(14 + top[2] * 0.04 + 10 * blend),
            )
            pygame.draw.line(surface, color, (0, y), (MAP_WIDTH, y))

    def draw_world_fx(self, surface):
        now = pygame.time.get_ticks()
        for i in range(6):
            px = int((now * (0.02 + i * 0.003) + i * 120) % MAP_WIDTH)
            py = int((50 + i * 90 + math.sin(now * 0.002 + i) * 18))
            pygame.draw.circle(surface, (255, 210, 130, 35), (px, py), 12)
        if self.chapter.id == "ground":
            alpha = 70 + int(abs(math.sin(now * 0.01)) * 80)
            overlay = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
            overlay.fill((120, 8, 8, alpha))
            surface.blit(overlay, (0, 0))

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
            "ENTER  Xem trailer & bắt đầu",
            "H      How To Play",
            "ESC    Quit",
        ]
        y = 280
        for line in menu_lines:
            screen.blit(self.font_big.render(line, True, WHITE), (126, y))
            y += 44
        teaser = [
            "Sinh tồn 2D theo chương, có NPC và hệ gợi ý đường đi.",
            "Bấm TAB trong game để đổi BFS / DFS / SAFE / A*.",
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
                "WASD: Di chuyển",
                "E: Tương tác / nhặt đồ",
                "Q / Lăn chuột: Đổi súng",
                "1-2-3: Chọn nhanh súng",
                "TAB: Đổi thuật toán tìm đường",
                "M: Mở minimap lớn",
                "ESC: Pause",
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
        screen.blit(self.font.render("ENTER để bỏ qua trailer", True, WHITE), (90, 580))
        screen.blit(self.font.render(f"Cảnh {scene_index + 1}/{len(scenes)}", True, WHITE), (470, 606))

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
        elif key == "hut":
            screen.blit(DESERT_HUT, DESERT_HUT.get_rect(center=(x, y)))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        screen.blit(overlay, (0, 0))
        screen.blit(self.font_title.render("PAUSE", True, WHITE), (180, 160))
        lines = [
            "ESC de tiep tuc",
            "M de mo minimap",
            "TAB de doi thuat toan tim duong",
        ]
        y = 260
        for line in lines:
            screen.blit(self.font_big.render(line, True, WHITE), (160, y))
            y += 44

    def draw_end_screen(self):
        screen.fill((10, 10, 14))
        title = "THOAT THANH CONG" if self.state == "win" else "THAT BAI"
        title_color = GREEN if self.state == "win" else RED
        screen.blit(self.font_title.render(title, True, title_color), (110, 110))
        screen.blit(self.font_big.render(self.end_reason, True, WHITE), (110, 190))
        elapsed_seconds = (pygame.time.get_ticks() - self.stats_start) // 1000
        stats = [
            f"Zombie ha guc: {self.kill_count}",
            f"NPC da cuu: {self.saved_npcs}",
            f"Thoi gian song sot: {elapsed_seconds}s",
            f"Chuong cao nhat: {self.chapter.title}",
            "ENTER de choi lai",
            "ESC de thoat",
        ]
        y = 300
        for line in stats:
            screen.blit(self.font_big.render(line, True, WHITE), (112, y))
            y += 46

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down = True
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5) and self.state == "playing":
            if len(self.weapon_manager.weapons) > 1:
                direction = 1 if event.button == 4 else -1
                self.weapon_manager.cycle_weapon(direction)
                self.popup = f"Da chuyen sang {self.weapon_manager.current_weapon.name}"
                self.popup_timer = pygame.time.get_ticks() + 1200
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down = False
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "menu":
            if event.key == pygame.K_RETURN:
                self.stats_start = pygame.time.get_ticks()
                self.trailer_started_at = pygame.time.get_ticks()
                self.state = "intro"
            elif event.key == pygame.K_h:
                self.show_help = not self.show_help
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            return

        if self.state == "intro":
            if event.key == pygame.K_RETURN:
                self.state = "playing"
            elif event.key == pygame.K_SPACE:
                self.state = "playing"
            return

        if self.state in {"win", "lose"}:
            if event.key == pygame.K_RETURN:
                self.__init__()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            return

        if self.state == "playing" and event.key == pygame.K_RETURN and self.next_chapter_ready:
            if self.chapter_index == len(self.chapters) - 1:
                self.end_reason = "Bạn đã lên được trực thăng và thoát khỏi thành phố."
                self.state = "win"
            else:
                self.set_chapter(self.chapter_index + 1)
            return

        if self.dialog_npc:
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_ESCAPE):
                self.dialog_npc = None
                self.dialog_speaker = ""
                self.dialog_lines = []
                self.advance_dialog_queue()
            return

        if self.state == "playing":
            if event.key == pygame.K_ESCAPE:
                self.state = "pause"
            elif event.key == pygame.K_q:
                if len(self.weapon_manager.weapons) > 1:
                    self.weapon_manager.cycle_weapon()
                    self.popup = f"Đã chuyển sang {self.weapon_manager.current_weapon.name}"
                else:
                    self.popup = "Chưa có vũ khí phụ để đổi."
                self.popup_timer = pygame.time.get_ticks() + 1200
            elif event.key == pygame.K_1:
                if self.weapon_manager.weapons:
                    self.weapon_manager.current_weapon = self.weapon_manager.weapons[0]
                    self.popup = f"Da chuyen sang {self.weapon_manager.current_weapon.name}"
                    self.popup_timer = pygame.time.get_ticks() + 1200
            elif event.key == pygame.K_2:
                if len(self.weapon_manager.weapons) >= 2:
                    self.weapon_manager.current_weapon = self.weapon_manager.weapons[1]
                    self.popup = f"Da chuyen sang {self.weapon_manager.current_weapon.name}"
                    self.popup_timer = pygame.time.get_ticks() + 1200
            elif event.key == pygame.K_3:
                if len(self.weapon_manager.weapons) >= 3:
                    self.weapon_manager.current_weapon = self.weapon_manager.weapons[2]
                    self.popup = f"Da chuyen sang {self.weapon_manager.current_weapon.name}"
                    self.popup_timer = pygame.time.get_ticks() + 1200
            # --- Phím kỹ năng ---
            elif event.key == pygame.K_4:
                # Dùng kỹ năng 1
                mx, my = pygame.mouse.get_pos()
                self.skill_manager.use_skill(0, self.player.x, self.player.y, mx, my)
                self.popup = f"Dùng kỹ năng: {self.skill_manager.skills[0].name}" if len(self.skill_manager.skills) > 0 else ""
                self.popup_timer = pygame.time.get_ticks() + 1000
            elif event.key == pygame.K_5:
                mx, my = pygame.mouse.get_pos()
                self.skill_manager.use_skill(1, self.player.x, self.player.y, mx, my)
                self.popup = f"Dùng kỹ năng: {self.skill_manager.skills[1].name}" if len(self.skill_manager.skills) > 1 else ""
                self.popup_timer = pygame.time.get_ticks() + 1000
            elif event.key == pygame.K_6:
                mx, my = pygame.mouse.get_pos()
                self.skill_manager.use_skill(2, self.player.x, self.player.y, mx, my)
                self.popup = f"Dùng kỹ năng: {self.skill_manager.skills[2].name}" if len(self.skill_manager.skills) > 2 else ""
                self.popup_timer = pygame.time.get_ticks() + 1000
            # ---
            elif event.key == pygame.K_TAB:
                self.hint_mode_index = (self.hint_mode_index + 1) % len(self.hint_modes)
            elif event.key == pygame.K_m:
                self.show_map = not self.show_map
            elif event.key == pygame.K_e:
                self.interact()
            elif event.key == pygame.K_RETURN and self.chapter_card_timer > pygame.time.get_ticks():
                self.chapter_card_timer = 0
            elif event.key == pygame.K_SPACE and not self.dialog_npc and self.dialog_queue:
                self.advance_dialog_queue()
            return

        if self.state == "pause":
            if event.key == pygame.K_ESCAPE:
                self.state = "playing"
            elif event.key == pygame.K_m:
                self.show_map = not self.show_map
            elif event.key == pygame.K_TAB:
                self.hint_mode_index = (self.hint_mode_index + 1) % len(self.hint_modes)


def main():
    game = Game()
    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        if game.state == "intro" and pygame.time.get_ticks() > game.chapter_card_timer + 500:
            pass
        game.update()
        game.draw()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
