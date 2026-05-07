
import pygame
import os

pygame.display.set_mode((1, 1), pygame.NOFRAME)
image_path = r"c:\Users\daova\Downloads\game2d\Sprites\Sprites_Effect\Bullets\bullet_icon.png"
if os.path.exists(image_path):
    surf = pygame.image.load(image_path).convert_alpha()
    width, height = surf.get_size()
    
    # Simple bounding box detection by checking colors that are NOT the checkerboard gray
    # Grid colors are usually around (128, 128, 128) and (192, 192, 192) or similar
    
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found = False
    
    for x in range(0, width, 5): # Step for speed
        for y in range(0, height, 5):
            r, g, b, a = surf.get_at((x, y))
            # If color is yellow-ish or copper-ish (the bullet)
            if (r > 100 and g > 50 and b < 100) or (r > 150 and g > 150 and b < 100):
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                
    if found:
        # Add some padding
        min_x = max(0, min_x - 10)
        min_y = max(0, min_y - 10)
        max_x = min(width, max_x + 10)
        max_y = min(height, max_y + 10)
        print(f"BBOX: {min_x}, {min_y}, {max_x - min_x}, {max_y - min_y}")
    else:
        print("NOT FOUND")
else:
    print("FILE NOT FOUND")
pygame.quit()
