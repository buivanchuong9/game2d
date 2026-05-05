import pygame
pygame.init()
img = pygame.image.load("Sprites/Sprites_Enemy/All Characters.png")
print(f"All Characters: {img.get_width()}x{img.get_height()}")
pygame.quit()
