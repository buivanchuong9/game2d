import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1))

sprites = [
    "Sprites/Sprites_Enemy/Skeleton/Attack.png",
    "Sprites/Sprites_Enemy/Skeleton/Idle.png",
    "Sprites/Sprites_Enemy/Skeleton/Walk.png",
    "Sprites/Sprites_Enemy/Skeleton/Shield.png",
    "Sprites/Sprites_Enemy/Skeleton/Take Hit.png",
    "Sprites/Sprites_Enemy/Skeleton/Death.png",
    "Sprites/Sprites_Enemy/All Characters.png",
    "Sprites/Sprites_Enemy/Boss1-SpritSheet.png",
    "Sprites/Sprites_Enemy/Evil Wizard/Idle.png",
    "Sprites/Sprites_Enemy/Evil Wizard/Run.png",
    "Sprites/Sprites_Enemy/Evil Wizard/Attack1.png",
    "Sprites/Sprites_Enemy/Old_Guardian/Old_Guardian_idle.png"
]

for s in sprites:
    if os.path.exists(s):
        img = pygame.image.load(s)
        print(f"{s}: {img.get_size()}")
    else:
        print(f"{s}: NOT FOUND")
