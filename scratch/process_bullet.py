
import pygame
import os

pygame.display.set_mode((1, 1), pygame.NOFRAME)
image_path = r"c:\Users\daova\Downloads\game2d\Sprites\Sprites_Effect\Bullets\bullet_icon.png"
if os.path.exists(image_path):
    surf = pygame.image.load(image_path).convert_alpha()
    
    # BBOX from previous run: 90, 390, 840, 245
    # We'll use a slightly tighter crop if possible or just use this.
    bullet_part = surf.subsurface((90, 390, 840, 245)).copy()
    
    # Rotate 90 degrees to make it stand up
    rotated = pygame.transform.rotate(bullet_part, 90)
    
    # Create a new surface with alpha
    final = pygame.Surface(rotated.get_size(), pygame.SRCALPHA)
    
    # Remove the checkerboard background
    # We'll assume anything that is "too gray" is background
    for x in range(rotated.get_width()):
        for y in range(rotated.get_height()):
            r, g, b, a = rotated.get_at((x, y))
            # If color is not gray-ish (where r,g,b are close and medium-bright)
            is_gray = abs(r-g) < 15 and abs(g-b) < 15 and abs(r-b) < 15
            # Also the grid is usually around 150-200
            if is_gray and r > 50:
                final.set_at((x, y), (0, 0, 0, 0))
            else:
                final.set_at((x, y), (r, g, b, a))
                
    pygame.image.save(final, image_path)
    print("PROCESSED")
else:
    print("FILE NOT FOUND")
pygame.quit()
