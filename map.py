# map.py
# Module quản lý bản đồ, tileset, props, obstacle, spawn, decor...
import pygame
from ui import safe_load

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

# ... (các tileset, props, CHAPTER_TILES, PROPS, draw_prop, obstacle_prop_for_tile...)

# Để trống các hàm chưa tách xong, sẽ bổ sung tiếp
# map.py
# Module quản lý bản đồ, tileset, props, obstacle, spawn, decor...
# Tách các hàm và dữ liệu liên quan đến map từ main.py

# Để trống, sẽ bổ sung sau khi tách xong các phần liên quan
