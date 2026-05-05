import pygame
import os

def generate_npcs():
    pygame.init()
    screen = pygame.display.set_mode((1, 1), pygame.NOFRAME) # Need display for convert()
    
    base_path = "Sprites/Sprites_Player/Char_003_Idle.png"
    if not os.path.exists(base_path):
        print("Base sprite not found!")
        return
        
    base_sheet = pygame.image.load(base_path).convert_alpha()
    # First frame is 32x32 (judging by the 128x128 image with 4x4 grid)
    # Let's check size
    w, h = base_sheet.get_size()
    fw, fh = w // 4, h // 4
    base_frame = base_sheet.subsurface((0, 0, fw, fh)).copy()
    
    npc_dir = "Sprites/Sprites_NPC"
    os.makedirs(npc_dir, exist_ok=True)
    
    def save_recolored(name, color_mod):
        surf = base_frame.copy()
        # Apply color modulation
        # This is a simple way: multiply by color
        # Or replace specific colors.
        # Let's try simple blend
        overlay = pygame.Surface((fw, fh), pygame.SRCALPHA)
        overlay.fill(color_mod)
        surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.image.save(surf, os.path.join(npc_dir, name))
        print(f"Saved {name}")

    # Pilot: Dark Blue/Cyan
    save_recolored("pilot.png", (100, 150, 255, 255))
    # Guard: Gray/Dark
    save_recolored("guard.png", (150, 150, 160, 255))
    # Medic: White/Green
    save_recolored("medic.png", (200, 255, 200, 255))
    # Engineer: Orange
    save_recolored("engineer.png", (255, 200, 100, 255))
    # Doctor: White/Cyan
    save_recolored("doctor.png", (200, 240, 255, 255))
    
    # Also others for variety
    save_recolored("child.png", (255, 220, 220, 255))
    save_recolored("elder.png", (230, 230, 200, 255))
    save_recolored("journalist.png", (220, 100, 255, 255))
    save_recolored("soldier.png", (100, 255, 100, 255))
    save_recolored("survivor_f.png", (255, 150, 150, 255))

    pygame.quit()

if __name__ == "__main__":
    generate_npcs()
