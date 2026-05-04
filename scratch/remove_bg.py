
import pygame

def remove_background():
    pygame.init()
    path = 'Sprites/Sprites_Effect/Bullets/custom_katana_slash.png'
    img = pygame.image.load(path)
    w, h = img.get_size()
    
    new_img = pygame.Surface((w, h), pygame.SRCALPHA)
    
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            
            # If it's a greyish pixel (checkerboard), make it transparent
            # Blue effect pixels should have high B and some G, and be different from grey.
            # Grey pixels have r, g, b close to each other.
            diff_rg = abs(r - g)
            diff_rb = abs(r - b)
            diff_gb = abs(g - b)
            
            # If it's very grey (low difference between channels), it's likely background
            if diff_rg < 20 and diff_rb < 20 and diff_gb < 20:
                new_img.set_at((x, y), (0, 0, 0, 0))
            else:
                new_img.set_at((x, y), (r, g, b, 255))
                
    pygame.image.save(new_img, 'Sprites/Sprites_Effect/Bullets/custom_katana_slash_no_bg.png')
    print("Saved custom_katana_slash_no_bg.png")

if __name__ == "__main__":
    remove_background()
