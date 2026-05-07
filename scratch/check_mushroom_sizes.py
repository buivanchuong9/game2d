import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1))

mushroom_sprites = [
    "Sprites/Sprites_Enemy/Mushroom/Attack.png",
    "Sprites/Sprites_Enemy/Mushroom/Death.png",
    "Sprites/Sprites_Enemy/Mushroom/Idle.png",
    "Sprites/Sprites_Enemy/Mushroom/Run.png",
    "Sprites/Sprites_Enemy/Mushroom/Take Hit.png"
]

for s in mushroom_sprites:
    if os.path.exists(s):
        img = pygame.image.load(s)
        print(f"{s}: {img.get_size()}")
    else:
        print(f"{s}: NOT FOUND")
