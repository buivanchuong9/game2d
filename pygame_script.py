import pygame
import sys
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)
img = pygame.image.load(r"C:\Users\daova\.gemini\antigravity\brain\5155c686-ef25-4f31-a700-01c3476c2e34\helicopter_1776070347518.png").convert_alpha()
for x in range(img.get_width()):
    for y in range(img.get_height()):
        c = img.get_at((x, y))
        if c.r > 240 and c.g > 240 and c.b > 240:
            img.set_at((x, y), pygame.Color(0, 0, 0, 0))
pygame.image.save(img, r"Sprites\Sprites_Building\Helicopter.png")
sys.exit(0)
