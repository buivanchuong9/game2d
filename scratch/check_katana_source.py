import pygame
import os

def check():
    pygame.init()
    path = 'Sprites/Sprites_Effect/Bullets/custom_katana_slash_no_bg.png'
    img = pygame.image.load(path)
    w, h = img.get_size()
    min_x, max_x = w, 0
    for x in range(w):
        for y in range(h):
            if img.get_at((x, y))[3] > 50:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
    print(f"BB X: {min_x} to {max_x} (Width: {max_x - min_x + 1})")

if __name__ == "__main__":
    check()
