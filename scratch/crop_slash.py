
import pygame
import os

def process_katana_slash():
    pygame.init()
    path = 'Sprites/Sprites_Effect/Bullets/custom_katana_slash_no_bg.png'
    img = pygame.image.load(path)
    w, h = img.get_size()
    
    # Find bounding box of all non-transparent pixels
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    
    for x in range(w):
        for y in range(h):
            alpha = img.get_at((x, y))[3]
            if alpha > 50:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
    
    print(f"Alpha at (0,0): {img.get_at((0,0))[3]}")
    print(f"Alpha at (512,512): {img.get_at((512,512))[3]}")
    print(f"Bounding box: {min_x}, {min_y}, {max_x}, {max_y}")
    
    # Crop to bounding box
    cropped = pygame.Surface((max_x - min_x + 1, max_y - min_y + 1), pygame.SRCALPHA)
    cropped.blit(img, (0, 0), (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
    
    # Save the cropped version
    pygame.image.save(cropped, 'Sprites/Sprites_Effect/Bullets/custom_katana_slash_clean.png')
    print("Saved custom_katana_slash_clean.png")

if __name__ == "__main__":
    process_katana_slash()
