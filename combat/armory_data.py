# Big armory overhaul using new assets from Sprites/Sprites_Weapon/ and Sprites/Sprites_Effect/Bullets/

# Effects
EFFECT_DIR = "Sprites/Sprites_Effect/Bullets/"
WEAPON_DIR = "Sprites/Sprites_Weapon/"

# MELEE EFFECTS (GIFs)
MELEE_BLUE = EFFECT_DIR + "Introl Blue Effect Bullet Impact Explosion 32x32.gif"
MELEE_GREEN = EFFECT_DIR + "Introl Green Effect Bullet Impact Explosion 32x32.gif"
MELEE_YELLOW = EFFECT_DIR + "Introl Yellow Effect Bullet Impact Explosion 32x32.gif"

RARITY_COLORS = {
    "common": (210, 210, 220),
    "rare": (80, 170, 255),
    "epic": (190, 90, 255),
}

def _mk(name: str, wtype: str, img: str, fire_rate: float, reload_time: float, speed: float, dmg: int, scale=(36, 36), proj=None, radius: int = 0, rarity: str = "common"):
    return {
        "name": name,
        "type": wtype,
        "rarity": rarity,
        "fire_rate": fire_rate,
        "reload_time": reload_time,
        "image_path": WEAPON_DIR + img,
        "projectile_speed": speed,
        "damage": dmg,
        "projectile_scale": scale,
        **({"projectile_image": (EFFECT_DIR + proj) if isinstance(proj, str) else proj} if proj else {}),
        **({"projectile_radius": radius} if radius else {}),
    }

def fire_row(row: int, count: int = 8):
    return {
        "atlas": EFFECT_DIR + "All_Fire_Bullet_Pixel_16x16_00.png",
        "tile": (16, 16),
        "coords": [(i, row) for i in range(count)],
        "animate": True
    }

ARMORY = [
    # --- PISTOLS ---
    _mk("Pistol P1", "pistol", "Pistol-1.png", 5.0, 0.4, 12, 40, proj=fire_row(0)),
    _mk("Pistol P2", "pistol", "Pistol-2.png", 5.5, 0.4, 12, 45, proj=fire_row(1), rarity="rare"),
    _mk("Pistol P3", "pistol", "Pistol-3.png", 6.0, 0.3, 13, 50, proj=fire_row(2), rarity="rare"),
    _mk("Pistol Elite", "pistol", "Pistol-5.png", 7.0, 0.3, 14, 60, proj=fire_row(3), rarity="epic"),

    # --- RIFLES ---
    _mk("Assault Rifle A1", "rifle", "Assaut-rifle-1.png", 8.0, 0.5, 14, 55, proj=fire_row(4)),
    _mk("Assault Rifle A2", "rifle", "Assaut-rifle-2.png", 8.5, 0.5, 14, 60, proj=fire_row(5), rarity="rare"),
    _mk("Tactical Rifle", "rifle", "Assaut-rifle-3-scoped.png", 9.0, 0.4, 15, 70, proj=fire_row(6), rarity="rare"),
    _mk("Heavy Rifle", "rifle", "Assaut-rifle-4.png", 7.5, 0.6, 13, 85, proj=fire_row(7), rarity="epic"),

    # --- SMGs ---
    _mk("SMG S1", "smg", "SMG-1.png", 11.0, 0.4, 15, 30, proj=fire_row(8)),
    _mk("SMG S2", "smg", "SMG-2.png", 12.0, 0.4, 15, 35, proj=fire_row(9), rarity="rare"),
    _mk("Rapid SMG", "smg", "SMG-4.png", 14.0, 0.3, 16, 40, proj=fire_row(10), rarity="epic"),

    # --- SHOTGUNS ---
    _mk("Shotgun X1", "shotgun", "Shotgun-1.png", 2.0, 0.6, 10, 120, proj=fire_row(11), scale=(40, 40)),
    _mk("Shotgun X2", "shotgun", "Shotgun-2.png", 2.2, 0.6, 10, 140, proj=fire_row(12), scale=(40, 40), rarity="rare"),
    _mk("Heavy Shotgun", "shotgun", "Shotgun-4.png", 2.5, 0.5, 11, 160, proj=fire_row(13), scale=(45, 45), rarity="epic"),

    # --- SNIPERS ---
    _mk("Sniper R1", "sniper", "Sniper-rifle-1.png", 1.2, 0.8, 20, 200, proj=fire_row(14), scale=(50, 50)),
    _mk("Sniper R2", "sniper", "Sniper-rifle-2-scoped.png", 1.3, 0.8, 22, 230, proj=fire_row(15), scale=(50, 50), rarity="rare"),
    _mk("Modern Sniper", "sniper", "Sniper-rifle-4-scoped.png", 1.5, 0.7, 25, 280, proj=fire_row(16), scale=(55, 55), rarity="epic"),

    # --- HEAVY / SPECIAL ---
    _mk("Grenade Launcher", "grenade_launcher", "grenade launcher.png", 1.5, 0.8, 8, 150, proj=fire_row(17), radius=80, scale=(40, 40), rarity="rare"),
    _mk("Bazooka", "rocket", "Bazooka.png", 1.0, 1.2, 7, 300, proj=fire_row(18), radius=120, scale=(60, 60), rarity="epic"),
    _mk("RPG-7", "rocket", "RPG.png", 0.8, 1.5, 6, 400, proj=fire_row(19), radius=150, scale=(70, 70), rarity="epic"),
    _mk("Plasma Cannon", "taesar", "PlasmaGun.png", 4.0, 0.6, 14, 90, proj=fire_row(20), scale=(40, 40), rarity="epic"),

    # --- MELEE ---
    {
        "name": "Katana",
        "type": "melee",
        "rarity": "rare",
        "fire_rate": 3.0,
        "reload_time": 0.0,
        "image_path": WEAPON_DIR + "Katana.png",
        "projectile_speed": 0,
        "damage": 120,
        "projectile_image": [
            {"atlas": EFFECT_DIR + "custom_katana_slash_clean.png", "tile": (240, 363), "coords": [(0, 0), (1, 0), (2, 0), (3, 0)]},
        ],
        "projectile_scale": (80, 80),
        "melee": True,
    },
    {
        "name": "Dragon Blade",
        "type": "melee",
        "rarity": "epic",
        "fire_rate": 4.0,
        "reload_time": 0.0,
        "image_path": WEAPON_DIR + "Katana.png",
        "projectile_speed": 0,
        "damage": 180,
        "projectile_image": [
            {"atlas": EFFECT_DIR + "custom_katana_slash_clean.png", "tile": (240, 363), "coords": [(0, 0), (1, 0), (2, 0), (3, 0)]},
        ],
        "projectile_scale": (100, 100),
        "melee": True,
    }
]

