#Code for Main player

import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5  # Movement speed
        self.dx = 0
        self.dy = 0
        self.health = 300
        self.max_health = 300
        self.armor = 0
        self.hitbox_size = 26
        self.stamina = 100
        self.max_stamina = 100
        self.poison_timer = 0

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

    def update(self, keys, blocked_tiles=None, map_width=None, map_height=None, tile_size=16):
        """Update player position, collision and animation based on input."""
        dx, dy = 0, 0  # Movement vector components
        moving = False
        running = keys[pygame.K_LSHIFT] and self.stamina > 0

        current_speed = self.speed * 1.6 if running else self.speed

        # Movement logic
        #up-down 
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            self.direction = "down"
            moving = True
        #left-right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.direction = "right"
            moving = True

        # Stamina logic
        if moving:
            if running:
                self.stamina = max(0, self.stamina - 0.5)
            else:
                self.stamina = min(self.max_stamina, self.stamina + 0.2)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 0.4)

        # Normalize the movement vector
        if dx != 0 or dy != 0:  # If there's movement
            magnitude = (dx ** 2 + dy ** 2) ** 0.5
            dx /= magnitude
            dy /= magnitude

        self.dx = dx * current_speed
        self.dy = dy * current_speed

        self._move_axis(self.dx, 0, blocked_tiles, map_width, map_height, tile_size)
        self._move_axis(0, self.dy, blocked_tiles, map_width, map_height, tile_size)

        # Handle poison
        if self.poison_timer > 0:
            self.poison_timer -= 1
            if self.poison_timer % 60 == 0:
                self.health -= 1

        # Update animation frame
        if moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
        else:
            self.current_frame = 0  # Idle state resets to the first frame

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
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        surface.blit(sprite, sprite_rect.topleft)

