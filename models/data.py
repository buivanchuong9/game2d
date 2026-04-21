# data.py
# Module chứa các class dữ liệu: ItemPickup, Particle, NPC, Chapter, StoryEnemy, EscortTank, MissionTracker
import pygame
from dataclasses import dataclass, field
from typing import Optional

GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)

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
    reward: Optional[str] = None
    color: tuple[int, int, int] = CYAN
    once: bool = True
    interacted: bool = False
    portrait_color: tuple[int, int, int] = CYAN
    sprite_path: Optional[str] = None
    quest: Optional[str] = None

@dataclass
class Chapter:
    id: str
    title: str
    subtitle: str
    intro_lines: list[str]
    objective_titles: list[str]
    exit_pos: Optional[tuple[int, int]]
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
        return (int(self.enemy.x // 16), int(self.enemy.y // 16))

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
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 50:
            self.active = False
            return
        self.x += dx / distance * self.speed
        self.y += dy / distance * self.speed
        self.angle = math.degrees(math.atan2(dy, dx))

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
        # ... (giữ nguyên logic từ main.py)
        pass
    def complete(self):
        # ... (giữ nguyên logic từ main.py)
        pass
