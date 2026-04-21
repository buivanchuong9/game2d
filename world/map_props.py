# map_props.py
# Quản lý các props, gate, wall, decor, obstacle, tile...
import pygame
from systems.ui import safe_load

TILE_SIZE = 16
GRID_SIZE = 44

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

CHAPTER_TILES = {
    "roof": {
        "floor1": safe_load("Sprites/Sprites_Environment/roof_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/roof_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/roof_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "office": {
        "floor1": safe_load("Sprites/Sprites_Environment/office_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/office_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/office_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "medical": {
        "floor1": safe_load("Sprites/Sprites_Environment/medical_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/medical_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/medical_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "ground": {
        "floor1": safe_load("Sprites/Sprites_Environment/lobby_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/lobby_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/lobby_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "basement": {
        "floor1": safe_load("Sprites/Sprites_Environment/lobby_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/lobby_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/lobby_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "lab": {
        "floor1": safe_load("Sprites/Sprites_Environment/medical_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/medical_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/medical_wall.png", (TILE_SIZE, TILE_SIZE)),
    },
    "escape": {
        "floor1": safe_load("Sprites/Sprites_Environment/heli_tile.png", (TILE_SIZE, TILE_SIZE)),
        "floor2": safe_load("Sprites/Sprites_Environment/heli_tile2.png", (TILE_SIZE, TILE_SIZE)),
        "wall": safe_load("Sprites/Sprites_Environment/heli_wall.png", (TILE_SIZE, TILE_SIZE)),
    }
}

PROPS = {
    "roof_vent": safe_load("Sprites/Sprites_Environment/props/roof_vent_32.png", (32, 32)),
    "roof_ac": safe_load("Sprites/Sprites_Environment/props/roof_ac_48.png", (48, 48)),
    "roof_water_tank": safe_load("Sprites/Sprites_Environment/props/roof_water_tank_64.png", (64, 64)),
    "roof_stairwell": safe_load("Sprites/Sprites_Environment/props/roof_stairwell_64.png", (64, 64)),
    "roof_sat_dish": safe_load("Sprites/Sprites_Environment/props/roof_satdish_48.png", (48, 48)),
    "office_desk": safe_load("Sprites/Sprites_Environment/props/office_desk_48.png", (48, 48)),
    "office_table": safe_load("Sprites/Sprites_Environment/props/office_table_64.png", (64, 64)),
    "office_cabinet": safe_load("Sprites/Sprites_Environment/props/office_cabinet_48.png", (48, 48)),
    "office_glass": safe_load("Sprites/Sprites_Environment/props/office_glasswall_64.png", (64, 64)),
    "medical_bed": safe_load("Sprites/Sprites_Environment/props/medical_bed_64.png", (64, 64)),
    "medical_cabinet": safe_load("Sprites/Sprites_Environment/props/medical_cabinet_48.png", (48, 48)),
    "medical_trolley": safe_load("Sprites/Sprites_Environment/props/medical_trolley_48.png", (48, 48)),
    "basement_generator": safe_load("Sprites/Sprites_Environment/props/basement_generator_64.png", (64, 64)),
    "basement_pipes": safe_load("Sprites/Sprites_Environment/props/basement_pipes_64.png", (64, 64)),
    "basement_crates": safe_load("Sprites/Sprites_Environment/props/basement_crates_48.png", (48, 48)),
    "basement_panel": safe_load("Sprites/Sprites_Environment/props/basement_panel_48.png", (48, 48)),
    "lab_freezer": safe_load("Sprites/Sprites_Environment/props/lab_freezer_64.png", (64, 64)),
    "lab_console": safe_load("Sprites/Sprites_Environment/props/lab_console_64.png", (64, 64)),
    "lab_bench": safe_load("Sprites/Sprites_Environment/props/lab_bench_64.png", (64, 64)),
    "lab_tubes": safe_load("Sprites/Sprites_Environment/props/lab_tubes_48.png", (48, 48)),
    "gate_closed": safe_load("Sprites/Sprites_Environment/props/gate_closed_64.png", (64, 64)),
    "gate_open": safe_load("Sprites/Sprites_Environment/props/gate_open_64.png", (64, 64)),
}

def draw_prop(surface, prop_key: str, sx: int, sy: int, scale: float = 1.0):
    spr = PROPS.get(prop_key)
    if spr is None:
        return
    if scale != 1.0:
        sw = int(spr.get_width() * scale)
        sh = int(spr.get_height() * scale)
        spr = pygame.transform.scale(spr, (sw, sh))
    # Offset y to stick to the bottom of the tile
    surface.blit(spr, (sx, sy + int(TILE_SIZE * scale) - spr.get_height()))

def obstacle_prop_for_tile(chapter_id: str, tx: int, ty: int):
    if tx in (0, GRID_SIZE - 1) or ty in (0, GRID_SIZE - 1):
        return None
    r = (tx * 73856093) ^ (ty * 19349663) ^ (hash(chapter_id) & 0xFFFFFFFF)
    roll = r % 100
    if chapter_id == "roof":
        if roll < 55:
            return "roof_vent"
        if roll < 85:
            return "roof_ac"
        return "roof_sat_dish"
    if chapter_id == "office":
        if roll < 45:
            return "office_desk"
        if roll < 70:
            return "office_cabinet"
        if roll < 92:
            return "office_glass"
        return "office_table"
    if chapter_id == "medical":
        if roll < 55:
            return "medical_bed"
        if roll < 85:
            return "medical_cabinet"
        return "medical_trolley"
    if chapter_id == "basement":
        if roll < 45:
            return "basement_crates"
        if roll < 75:
            return "basement_pipes"
        if roll < 92:
            return "basement_panel"
        return "basement_generator"
    if chapter_id == "lab":
        if roll < 38:
            return "lab_bench"
        if roll < 65:
            return "lab_freezer"
        if roll < 88:
            return "lab_console"
        return "lab_tubes"
    return None
