import pygame
import sys
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

files_to_process = {
    r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\katana_base_1776074583458.png": r"Sprites\Sprites_Weapon\Katana.png",
    r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\katana_slash_1776074601238.png": r"Sprites\Sprites_Effect\Bullets\KatanaSlash.png",
    r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\plasma_gun_1776074700946.png": r"Sprites\Sprites_Weapon\PlasmaGun.png",
    r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\skill_fireball_1776074770143.png": r"Sprites\Sprites_Effect\Bullets\Fireball.png",
    r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\skill_frost_1776074782868.png": r"Sprites\Sprites_Effect\Bullets\FrostNova.png",
}

for src, dst in files_to_process.items():
    if not os.path.exists(src):
        print(f"Source not found: {src}")
        continue
    img = pygame.image.load(src).convert_alpha()
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            c = img.get_at((x, y))
            if c.r > 240 and c.g > 240 and c.b > 240:
                img.set_at((x, y), pygame.Color(0, 0, 0, 0))
    pygame.image.save(img, dst)
    print(f"Processed {dst}")

sys.exit(0)
