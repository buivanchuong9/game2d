#Code for Main player

import pygame
from systems.sound_manager import sound_manager

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2  # Reduced base speed from 5
        self.dx = 0
        self.dy = 0
        self.health = 300
        self.max_health = 300
        self.armor = 0
        self.hitbox_size = 26
        self.stamina = 100
        self.max_stamina = 100
        self.poison_timer = 0
        
        # Hit effects
        self.hit_timer = 0
        self.slow_timer = 0
        self.slow_multiplier = 1.0

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Player/mega_scientist_walk.png").convert_alpha()
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjusts animation speed

        # Player direction and frame setup
        self.direction = "down"  # Default direction
        self.frames = self.load_frames()

    def load_frames(self):
        """Extract frames from sprite sheet for animation."""
        frames = {
            #Explaintation: (x,y,Width,Height)
            #In properties , you see mega_scientist_walk is 576*256 pixels
            #64X64 is each grid
            "up": [self.sprite_sheet.subsurface((i * 64, 0, 64, 64)) for i in range(8)],
            "left": [self.sprite_sheet.subsurface((i * 64, 64, 64, 64)) for i in range(8)],
            "down": [self.sprite_sheet.subsurface((i * 64, 128, 64, 64)) for i in range(8)],
            "right": [self.sprite_sheet.subsurface((i * 64, 192, 64, 64)) for i in range(8)],
        }
        return frames

    def take_damage(self, amount):
        """Handle damage with armor reduction."""
        if self.armor > 0:
            reduction = min(self.armor, amount * 0.4) # 40% reduction if armor exists
            self.armor -= reduction * 0.5 # Armor takes half the reduction amount as wear
            amount -= reduction
        self.health -= amount

    def on_hit(self, damage):
        """Called when the player is hit by an enemy attack."""
        if self.hit_timer > 0:
            return # Invulnerability or skip if already hit recently? 
                   # User didn't ask for invulnerability, but let's prevent sound spam.
        
        self.take_damage(damage)
        self.hit_timer = 15 # Flash for 15 frames
        self.slow_timer = 40 # Slow down for 40 frames
        self.slow_multiplier = 0.5 # 50% speed reduction
        
        # Play hit sound here
        sound_manager.play("nhan_vat_trung_don")

    def update(self, keys, blocked_tiles=None, map_width=None, map_height=None, tile_size=16):
        """Update player position, collision and animation based on input."""
        dx, dy = 0, 0  # Movement vector components
        running = keys[pygame.K_LSHIFT] and self.stamina > 0

        # Apply slow effect and Frenzy effect
        frenzy_mult = 1.3 if getattr(self, "frenzy_active", False) else 1.0
        current_base_speed = self.speed * self.slow_multiplier * frenzy_mult
        current_speed = current_base_speed * 1.6 if running else current_base_speed
        
        # Adjust animation speed based on movement state
        dynamic_delay = 4 if (running or frenzy_mult > 1.0) else 10

        # Movement logic
        #up-down 
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            self.direction = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            self.direction = "down"
        #left-right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.direction = "right"

        # Stamina logic - only consume/recover based on actual movement effort
        # Note: actually_moved is calculated after the axis movement below

        # Normalize the movement vector
        if dx != 0 or dy != 0:  # If there's movement
            magnitude = (dx ** 2 + dy ** 2) ** 0.5
            dx /= magnitude
            dy /= magnitude

        self.dx = dx * current_speed
        self.dy = dy * current_speed

        old_x, old_y = self.x, self.y
        self._move_axis(self.dx, 0, blocked_tiles, map_width, map_height, tile_size)
        self._move_axis(0, self.dy, blocked_tiles, map_width, map_height, tile_size)

        # Check if we actually moved in the world (not blocked by walls)
        actually_moved = (abs(self.x - old_x) > 0.1 or abs(self.y - old_y) > 0.1)

        # Apply Stamina logic after we know if movement actually happened
        if actually_moved:
            if running:
                self.stamina = max(0, self.stamina - 0.5)
            else:
                self.stamina = min(self.max_stamina, self.stamina + 0.2)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 0.4)

        # Handle hit effects timers
        if self.hit_timer > 0:
            self.hit_timer -= 1
        
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.slow_multiplier = 1.0 # Recover speed
        
        # Handle poison
        if self.poison_timer > 0:
            self.poison_timer -= 1
            if self.poison_timer % 60 == 0:
                self.health -= 1

        # Update animation frame and footstep sounds
        # Only animate and play sounds if the player is actually moving (not stuck against a wall)
        if actually_moved:
            # If we just started moving, trigger the first frame and sound immediately for responsiveness
            if self.current_frame == 0 and self.frame_timer == 0:
                self.frame_timer = dynamic_delay
                
            self.frame_timer += 1
            if self.frame_timer >= dynamic_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
                
                # Play footstep sound on specific frames (1 and 5 in the 8-frame walk cycle)
                if self.current_frame in [1, 5]:
                    if running:
                        sound_manager.play("nhan_vat_chay_nhanh")
                    else:
                        sound_manager.play("nhan_vat_chay")
        else:
            # When stopping, reset to idle frame and clear timer
            self.current_frame = 0  # Idle state resets to the first frame
            self.frame_timer = 0

    def _move_axis(self, dx, dy, blocked_tiles, map_width, map_height, tile_size):
        self.x += dx
        self.y += dy

        if blocked_tiles:
            # Check only the tiles the player's hitbox actually overlaps with
            min_tx = int((self.x - self.hitbox_size / 2) // tile_size)
            max_tx = int((self.x + self.hitbox_size / 2) // tile_size)
            min_ty = int((self.y - self.hitbox_size / 2) // tile_size)
            max_ty = int((self.y + self.hitbox_size / 2) // tile_size)
            
            for tx in range(min_tx, max_tx + 1):
                for ty in range(min_ty, max_ty + 1):
                    if (tx, ty) in blocked_tiles:
                        tile_rect = pygame.Rect(tx * tile_size, ty * tile_size, tile_size, tile_size)
                        player_rect = self.get_rect()
                        if player_rect.colliderect(tile_rect):
                            if dx > 0:
                                self.x = tile_rect.left - self.hitbox_size / 2
                            elif dx < 0:
                                self.x = tile_rect.right + self.hitbox_size / 2
                            if dy > 0:
                                self.y = tile_rect.top - self.hitbox_size / 2
                            elif dy < 0:
                                self.y = tile_rect.bottom + self.hitbox_size / 2
                            # Re-calculate to avoid multi-collision jitter in the same axis
                            player_rect = self.get_rect()

        if map_width is not None:
            self.x = max(self.hitbox_size / 2, min(self.x, map_width - self.hitbox_size / 2))
        if map_height is not None:
            self.y = max(self.hitbox_size / 2, min(self.y, map_height - self.hitbox_size / 2))

    def get_rect(self):
        return pygame.Rect(
            self.x - self.hitbox_size / 2,
            self.y - self.hitbox_size / 2,
            self.hitbox_size,
            self.hitbox_size,
        )

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def add_armor(self, amount):
        self.armor = min(100, self.armor + amount)

    def draw(self, surface):
        # Draw the actual player sprite
        sprite = self.frames[self.direction][self.current_frame]
        
        # Flash white effect
        if self.hit_timer > 0:
            # Create a white silhouette
            white_surf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            white_surf.fill((255, 255, 255, 180)) # Semi-transparent white
            sprite = sprite.copy()
            sprite.blit(white_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            # Alternatively, use a simpler fill for better visibility
            # sprite.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        surface.blit(sprite, sprite_rect.topleft)

