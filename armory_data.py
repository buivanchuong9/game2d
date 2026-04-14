from __future__ import annotations

# Big armory (50 weapons) generated to Sprites/Sprites_Weapon/armory/
# Used by main.py for drops + shop.

FIRE_BULLET_A = "Sprites/Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_00.png"
FIRE_BULLET_B = "Sprites/Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_05.png"
MELEE_EFFECT = "Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif"
MELEE_EFFECT_GREEN = "Sprites/Sprites_Effect/Bullets/Introl Green Effect Bullet Impact Explosion 32x32.gif"
MELEE_EFFECT_YELLOW = "Sprites/Sprites_Effect/Bullets/Introl Yellow Effect Bullet Impact Explosion 32x32.gif"

RARITY_COLORS = {
    "common": (210, 210, 220),
    "rare": (80, 170, 255),
    "epic": (190, 90, 255),
}


def _slice(path: str, tile_x: int, tile_y: int, tile_w: int = 16, tile_h: int = 16) -> str:
    """Return atlas slice spec: path#x,y,w,h"""
    return f"{path}#{tile_x * tile_w},{tile_y * tile_h},{tile_w},{tile_h}"


# Curated effect coords (tile indices) to avoid "mostly circles"
FIRE_COORDS_A = [
    (1, 0), (2, 0), (3, 0), (6, 1), (7, 1),
    (10, 2), (11, 2), (12, 2), (13, 2),
    (16, 3), (18, 3), (20, 3),
    (24, 6), (26, 6), (28, 6), (30, 6),
    (22, 10), (24, 10), (26, 10), (28, 10), (30, 10),
    (22, 14), (24, 14), (26, 14), (28, 14), (30, 14),
]
FIRE_COORDS_B = [
    (1, 0), (2, 0), (3, 0), (6, 1), (7, 1),
    (10, 2), (11, 2), (12, 2), (13, 2),
    (16, 3), (18, 3), (20, 3),
    (24, 6), (26, 6), (28, 6), (30, 6),
    (22, 10), (24, 10), (26, 10), (28, 10), (30, 10),
    (22, 14), (24, 14), (26, 14), (28, 14), (30, 14),
]

MELEE_COORDS_32 = [
    # Assumes 8x6-ish layout; invalid coords are auto-ignored at runtime
    (0, 0), (1, 0), (2, 0), (6, 0), (7, 0),
    (0, 1), (2, 1), (3, 1), (5, 1), (6, 1),
    (0, 2), (3, 2), (4, 2), (5, 2), (7, 2),
    (0, 3), (1, 3), (3, 3), (4, 3), (5, 3), (7, 3),
    (0, 4), (2, 4), (3, 4), (5, 4), (7, 4),
]


def _rarity_for_variant(i: int) -> str:
    if i >= 5:
        return "epic"
    if i >= 3:
        return "rare"
    return "common"


def _mk(name: str, wtype: str, img: str, fire_rate: float, reload_time: float, speed: float, dmg: int, scale=(32, 32), proj=None, radius: int = 0, rarity: str = "common"):
    return {
        "name": name,
        "type": wtype,
        "rarity": rarity,
        "fire_rate": fire_rate,
        "reload_time": reload_time,
        "image_path": img,
        "projectile_speed": speed,
        "damage": dmg,
        "projectile_scale": scale,
        **({"projectile_image": proj} if proj else {}),
        **({"projectile_radius": radius} if radius else {}),
    }


ARMORY = []

# Pistols (fast swap, accurate)
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Pistol MK{i}", "pistol",
        f"Sprites/Sprites_Weapon/armory/pistol_{i:02}.png",
        fire_rate=4.8 + i * 1, reload_time=0.5,
        speed=11, dmg=34 + i * 3, scale=(28, 28),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# Rifles
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Assault Rifle A{i}", "rifle",
        f"Sprites/Sprites_Weapon/armory/rifle_{i:02}.png",
        fire_rate=6.5 + i * 1.2, reload_time=0.5,
        speed=12, dmg=42 + i * 4, scale=(30, 30),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# SMGs
for i in range(1, 6):
    ARMORY.append(_mk(
        f"SMG V{i}", "smg",
        f"Sprites/Sprites_Weapon/armory/smg_{i:02}.png",
        fire_rate=9.5 + i * 1.5, reload_time=0.5,
        speed=13, dmg=28 + i * 2, scale=(26, 26),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# Shotguns
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Shotgun S{i}", "shotgun",
        f"Sprites/Sprites_Weapon/armory/shotgun_{i:02}.png",
        fire_rate=1.6 + i * 0.6, reload_time=0.5,
        speed=9, dmg=110 + i * 10, scale=(34, 26),
        proj={"atlas": FIRE_BULLET_B, "tile": (16, 16), "coords": FIRE_COORDS_B},
        rarity=_rarity_for_variant(i),
    ))

# Snipers
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Sniper X{i}", "sniper",
        f"Sprites/Sprites_Weapon/armory/sniper_{i:02}.png",
        fire_rate=1.1 + i * 0.05, reload_time=0.8,
        speed=16, dmg=190 + i * 20, scale=(38, 38),
        proj={"atlas": FIRE_BULLET_B, "tile": (16, 16), "coords": FIRE_COORDS_B},
        rarity=_rarity_for_variant(i),
    ))

# Miniguns
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Minigun G{i}", "minigun",
        f"Sprites/Sprites_Weapon/armory/minigun_{i:02}.png",
        fire_rate=14 + i * 2, reload_time=0.5,
        speed=13, dmg=22 + i * 2, scale=(24, 24),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# Flamethrowers (DoT-like feel)
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Flamethrower F{i}", "flamethrower",
        f"Sprites/Sprites_Weapon/armory/flamethrower_{i:02}.png",
        fire_rate=11 + i * 2, reload_time=0.5,
        speed=7, dmg=18 + i * 2, scale=(36, 36),
        proj={"atlas": FIRE_BULLET_B, "tile": (16, 16), "coords": FIRE_COORDS_B},
        rarity=_rarity_for_variant(i),
    ))

# Grenade launchers (AoE)
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Grenade Launcher GL{i}", "grenade_launcher",
        f"Sprites/Sprites_Weapon/armory/grenade_launcher_{i:02}.png",
        fire_rate=1.2 + i * 2, reload_time=0.5,
        speed=6, dmg=150 + i * 15, scale=(34, 34),
        proj={"atlas": FIRE_BULLET_B, "tile": (16, 16), "coords": FIRE_COORDS_B},
        radius=70 + i * 6,
        rarity=_rarity_for_variant(i),
    ))

# Poison guns
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Poison Gun P{i}", "poison",
        f"Sprites/Sprites_Weapon/armory/poison_gun_{i:02}.png",
        fire_rate=6.8 + i * 2, reload_time=0.5,
        speed=10, dmg=36 + i * 3, scale=(30, 30),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# Taesar (stun-ish)
for i in range(1, 6):
    ARMORY.append(_mk(
        f"Taesar Gun T{i}", "taesar",
        f"Sprites/Sprites_Weapon/armory/taesar_gun_{i:02}.png",
        fire_rate=5.6 + i * 2, reload_time=0.5,
        speed=12, dmg=46 + i * 4, scale=(30, 30),
        proj={"atlas": FIRE_BULLET_A, "tile": (16, 16), "coords": FIRE_COORDS_A},
        rarity=_rarity_for_variant(i),
    ))

# Extra melee variants using GIF effect (safe fallback in Bullet loader)
for i in range(1, 11):
    ARMORY.append({
        "name": f"Blade {i}",
        "type": "melee",
        "rarity": "rare" if i >= 6 else "common",
        "fire_rate": 2.3 + (i * 0.05),
        "reload_time": 0.0,
        "image_path": "Sprites/Sprites_Weapon/Katana.png",
        "projectile_speed": 0,
        "damage": 80 + i * 6,
        "projectile_image": [
            {"atlas": MELEE_EFFECT_GREEN, "tile": (32, 32), "coords": MELEE_COORDS_32},
            {"atlas": MELEE_EFFECT_YELLOW, "tile": (32, 32), "coords": MELEE_COORDS_32},
        ],
        "projectile_scale": (96, 96),
        "type_hint": "melee",
    })

