import pygame
import os
import random

pygame.init()
pygame.display.set_mode((1, 1))

def create_tile(filename, base_color, noise_range, border_color=None, is_wall=False):
    surf = pygame.Surface((32, 32))
    surf.fill(base_color)
    
    # Add noise
    for _ in range(150):
        nx, ny = random.randint(0, 31), random.randint(0, 31)
        noise = random.randint(-noise_range, noise_range)
        c = (
            max(0, min(255, base_color[0] + noise)),
            max(0, min(255, base_color[1] + noise)),
            max(0, min(255, base_color[2] + noise)),
        )
        surf.set_at((nx, ny), c)
        
    if is_wall:
        pygame.draw.rect(surf, border_color, (0, 0, 32, 32), 2)
        pygame.draw.line(surf, border_color, (0, 16), (32, 16), 1)
        pygame.draw.line(surf, border_color, (16, 0), (16, 32), 1)
    
    pygame.image.save(surf, filename)

def create_npc(filename, head_c, body_c, leg_c):
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 100), (4, 24, 24, 8))
    # legs
    pygame.draw.rect(surf, leg_c, (10, 20, 4, 8))
    pygame.draw.rect(surf, leg_c, (18, 20, 4, 8))
    # body
    pygame.draw.rect(surf, body_c, (8, 10, 16, 12))
    # head
    pygame.draw.rect(surf, head_c, (10, 2, 12, 10))
    # face / eyes
    pygame.draw.rect(surf, (0, 0, 0), (12, 6, 2, 2))
    pygame.draw.rect(surf, (0, 0, 0), (18, 6, 2, 2))
    
    pygame.image.save(surf, filename)

def main():
    os.makedirs("Sprites", exist_ok=True)
    os.makedirs("Sprites/Sprites_Environment", exist_ok=True)
    os.makedirs("Sprites/Sprites_NPC", exist_ok=True)

    # 1. Roof
    create_tile("Sprites/Sprites_Environment/roof_tile.png", (100, 100, 100), 15)
    create_tile("Sprites/Sprites_Environment/roof_tile2.png", (90, 90, 95), 20)
    create_tile("Sprites/Sprites_Environment/roof_wall.png", (70, 70, 70), 10, (40, 40, 40), True)

    # 2. Office
    create_tile("Sprites/Sprites_Environment/office_tile.png", (180, 200, 220), 10)
    create_tile("Sprites/Sprites_Environment/office_tile2.png", (170, 190, 210), 12)
    create_tile("Sprites/Sprites_Environment/office_wall.png", (220, 220, 220), 5, (150, 150, 150), True)

    # 3. Medical
    create_tile("Sprites/Sprites_Environment/medical_tile.png", (240, 240, 245), 5)
    create_tile("Sprites/Sprites_Environment/medical_tile2.png", (230, 240, 240), 8)
    create_tile("Sprites/Sprites_Environment/medical_wall.png", (200, 230, 230), 5, (100, 150, 150), True)

    # 4. Ground Lobby
    create_tile("Sprites/Sprites_Environment/lobby_tile.png", (200, 190, 170), 5)
    create_tile("Sprites/Sprites_Environment/lobby_tile2.png", (180, 170, 150), 10)
    create_tile("Sprites/Sprites_Environment/lobby_wall.png", (100, 80, 60), 10, (50, 40, 30), True)

    # 5. Escape (Helipad)
    create_tile("Sprites/Sprites_Environment/heli_tile.png", (60, 60, 65), 15)
    create_tile("Sprites/Sprites_Environment/heli_tile2.png", (50, 50, 55), 20)
    create_tile("Sprites/Sprites_Environment/heli_wall.png", (120, 120, 120), 20, (60, 60, 60), True)

    # NPCs
    create_npc("Sprites/Sprites_NPC/pilot.png", (255, 210, 160), (50, 100, 50), (40, 40, 40))
    create_npc("Sprites/Sprites_NPC/guard.png", (255, 210, 160), (50, 50, 150), (30, 30, 30))
    create_npc("Sprites/Sprites_NPC/medic.png", (255, 220, 180), (240, 240, 240), (200, 200, 200))
    create_npc("Sprites/Sprites_NPC/engineer.png", (255, 210, 160), (255, 120, 20), (50, 50, 50))
    create_npc("Sprites/Sprites_NPC/survivor_f.png", (255, 220, 180), (200, 80, 150), (80, 80, 120))
    create_npc("Sprites/Sprites_NPC/soldier.png", (255, 210, 160), (80, 120, 60), (50, 80, 40))
    create_npc("Sprites/Sprites_NPC/doctor.png", (255, 210, 160), (200, 220, 220), (100, 100, 100))
    create_npc("Sprites/Sprites_NPC/elder.png", (240, 200, 150), (120, 100, 80), (60, 50, 40))
    create_npc("Sprites/Sprites_NPC/journalist.png", (255, 220, 180), (150, 80, 80), (40, 40, 60))
    create_npc("Sprites/Sprites_NPC/child.png", (255, 220, 180), (80, 180, 80), (50, 100, 50))
    
    print("Assets generated successfully!")

if __name__ == '__main__':
    main()
