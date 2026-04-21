import pygame
import math
import os

class Pet:
    def __init__(self, name, sprite_path, attributes, description):
        self.name = name
        self.sprite_path = sprite_path
        self.attributes = attributes # e.g. {"speed": 1.1, "damage": 1.2}
        self.description = description
        
        # Animation setup
        self.frames = self.load_frames(sprite_path)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150 # ms per frame
        self.direction = "down"
        
        # Position for floating/following
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.follow_speed = 0.08
        self.orbit_angle = 0
        
    def load_frames(self, path):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            w, h = sheet.get_size()
            frame_size = 32
            cols = w // frame_size
            rows = h // frame_size
            
            # Organize frames by direction (typical RPG Maker layout: Down, Left, Right, Up)
            frames = {
                "down": [],
                "left": [],
                "right": [],
                "up": []
            }
            
            # Map rows to directions (assuming 3 rows per direction or similar)
            # Typically: Down (0-2), Left (3-5), Right (6-8), Up (9-11)
            for r in range(rows):
                if r < 3: dir_key = "down"
                elif r < 6: dir_key = "left"
                elif r < 9: dir_key = "right"
                elif r < 12: dir_key = "up"
                else: dir_key = "down" # Fallback
                
                for c in range(cols):
                    rect = pygame.Rect(c * frame_size, r * frame_size, frame_size, frame_size)
                    frame = sheet.subsurface(rect)
                    frames[dir_key].append(pygame.transform.scale(frame, (32, 32)))
            
            # Ensure no empty lists
            for k in frames:
                if not frames[k]:
                    frames[k] = [pygame.Surface((32, 32))]
            return frames
        except Exception as e:
            print(f"Error loading pet frames from {path}: {e}")
            fallback = pygame.Surface((32, 32))
            fallback.fill((255, 0, 255))
            return {"down": [fallback], "left": [fallback], "right": [fallback], "up": [fallback]}

    def update(self, player_x, player_y, player_direction, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            
        self.direction = player_direction
        
        # Smooth trailing follow logic
        # Pet target is slightly behind the player based on direction
        offset_dist = 40
        if self.direction == "down":
            self.target_x, self.target_y = player_x, player_y - offset_dist
        elif self.direction == "up":
            self.target_x, self.target_y = player_x, player_y + offset_dist
        elif self.direction == "left":
            self.target_x, self.target_y = player_x + offset_dist, player_y
        elif self.direction == "right":
            self.target_x, self.target_y = player_x - offset_dist, player_y
            
        # Add a little bobbing/floating
        now = pygame.time.get_ticks()
        bob_y = math.sin(now * 0.005) * 5
        
        # Lerp towards target
        self.x += (self.target_x - self.x) * self.follow_speed
        self.y += (self.target_y + bob_y - self.y) * self.follow_speed
        
    def draw(self, surface, camera):
        if not self.frames: return
        
        # Get current frame based on direction
        dir_frames = self.frames.get(self.direction, self.frames["down"])
        frame = dir_frames[self.current_frame % len(dir_frames)]
        
        sx, sy = camera.world_to_screen(self.x, self.y)
        
        # Draw a small shadow
        shadow_surf = pygame.Surface((24, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 24, 10))
        surface.blit(shadow_surf, (sx - 12, sy + 18))
        
        # Draw the pet
        rect = frame.get_rect(center=(sx, sy))
        surface.blit(frame, rect.topleft)
        
        # Magic particles
        for i in range(3):
            ang = pygame.time.get_ticks() * 0.003 + i * 2.09
            px = sx + math.cos(ang) * 16
            py = sy + math.sin(ang) * 16
            pygame.draw.circle(surface, (150, 200, 255, 120), (int(px), int(py)), 2)

PETS_DATA = [
    {
        "id": "blue_bird",
        "name": "Blue Bird",
        "path": "Sprites/Sprites_Pet/PET_BlueBird.png",
        "desc": "+15% Tốc độ di chuyển",
        "attr": {"speed_mult": 1.15}
    },
    {
        "id": "cat_gray",
        "name": "Gray Cat",
        "path": "Sprites/Sprites_Pet/PET_Cat_Gray.png",
        "desc": "+50 Máu tối đa & Hồi phục chậm",
        "attr": {"max_health_add": 50, "regen": 0.05}
    },
    {
        "id": "cat_orange",
        "name": "Orange Cat",
        "path": "Sprites/Sprites_Pet/PET_Cat_Orange.png",
        "desc": "+20% Sát thương vũ khí",
        "attr": {"damage_mult": 1.2}
    },
    {
        "id": "eagle",
        "name": "Eagle",
        "path": "Sprites/Sprites_Pet/PET_Eagle.png",
        "desc": "+15% Tốc độ bắn",
        "attr": {"fire_rate_mult": 1.15}
    },
    {
        "id": "fox",
        "name": "Fox",
        "path": "Sprites/Sprites_Pet/PET_Fox.png",
        "desc": "+25 Giáp khởi điểm",
        "attr": {"armor_add": 25}
    },
    {
        "id": "racoon",
        "name": "Racoon",
        "path": "Sprites/Sprites_Pet/PET_Racoon.png",
        "desc": "+50% Tiền từ zombie",
        "attr": {"money_mult": 1.5}
    }
]
