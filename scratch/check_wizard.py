import pygame
pygame.init()
img = pygame.image.load("Sprites/Sprites_Enemy/Evil Wizard/Attack1.png")
print(f"Attack1: {img.get_width()}x{img.get_height()}")
img2 = pygame.image.load("Sprites/Sprites_Enemy/Evil Wizard/Attack2.png")
print(f"Attack2: {img2.get_width()}x{img2.get_height()}")
pygame.quit()
