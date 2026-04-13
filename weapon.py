import pygame
import math

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=5, damage=3000, radius=0, image_path="Sprites/Sprites_Effect/Bullets/14.png", scale=(48, 48)):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.exploded = False
        self.explosion_timer = 0
        
        # Load and scale bullet image
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, scale)

        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0
        
        # Calculate angle and rotate image
        self.angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        
    def update(self):
        if self.exploded:
            self.explosion_timer -= 1
            return
        self.x += self.dx
        self.y += self.dy

    def explode(self):
        self.exploded = True
        self.explosion_timer = 8
        
    def draw(self, surface):
        if self.exploded and self.radius > 0:
            pygame.draw.circle(surface, (255, 160, 70), (int(self.x), int(self.y)), self.radius, 3)
            pygame.draw.circle(surface, (255, 220, 120), (int(self.x), int(self.y)), max(6, self.radius // 2))
            return
        surface.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))

class Weapon:
    def __init__(self, name, fire_rate, reload_time, image_path, projectile_speed=5, damage=3000, projectile_radius=0, projectile_image="Sprites/Sprites_Effect/Bullets/14.png", projectile_scale=(48, 48)):
        self.name = name
        self.fire_rate = fire_rate  # Shots per second
        self.reload_time = reload_time  # Seconds
        self.last_shot_time = 0
        self.bullets = []
        self.offset = 30  # Distance from player
        self.angle = 0  # Current angle of weapon
        self.x = 0
        self.y = 0
        self.projectile_speed = projectile_speed
        self.damage = damage
        self.projectile_radius = projectile_radius
        self.projectile_image = projectile_image
        self.projectile_scale = projectile_scale
        
        # Load weapon image
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((100, 100, 100))
        self.rotated_image = self.image
    
    def update_position(self, player_x, player_y, target_x, target_y):
        # Calculate angle to target
        dx = target_x - player_x
        dy = target_y - player_y
        self.angle = math.atan2(dy, dx)
        
        # Position weapon at offset distance from player
        self.x = player_x + math.cos(self.angle) * self.offset
        self.y = player_y + math.sin(self.angle) * self.offset
        
        # Rotate weapon image
        self.rotated_image = pygame.transform.rotate(
            self.image, 
            -math.degrees(self.angle) - 0
        )
        
    def move_with_player(self, player_x, player_y):
        # Keep weapon at current angle but update position with player
        self.x = player_x + math.cos(self.angle) * self.offset
        self.y = player_y + math.sin(self.angle) * self.offset
    
    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time > (1000 / self.fire_rate)
    
    def shoot(self, target_x, target_y):
        if self.can_shoot():
            self.bullets.append(
                Bullet(
                    self.x,
                    self.y,
                    target_x,
                    target_y,
                    speed=self.projectile_speed,
                    damage=self.damage,
                    radius=self.projectile_radius,
                    image_path=self.projectile_image,
                    scale=self.projectile_scale,
                )
            )
            self.last_shot_time = pygame.time.get_ticks()
            return True
        return False
    
    def update_bullets(self, enemies):
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.update()
            
            # Check collision with enemies
            for enemy in enemies:
                if not enemy.is_dead:
                    enemy_rect = pygame.Rect(enemy.x - 25, enemy.y - 25, 50, 50)
                    bullet_rect = pygame.Rect(bullet.x - 2, bullet.y - 2, 4, 4)
                    
                    if not bullet.exploded and bullet_rect.colliderect(enemy_rect):
                        if bullet.radius > 0:
                            bullet.explode()
                            for splash_enemy in enemies:
                                if not splash_enemy.is_dead:
                                    dist = math.hypot(splash_enemy.x - bullet.x, splash_enemy.y - bullet.y)
                                    if dist <= bullet.radius:
                                        splash_enemy.take_damage(bullet.damage)
                        else:
                            enemy.take_damage(bullet.damage)
                        bullets_to_remove.append(bullet)
                        break
            
            # Remove bullets that are off screen
            if (bullet.x < 0 or bullet.x > 800 or 
                bullet.y < 0 or bullet.y > 800):
                bullets_to_remove.append(bullet)
            if bullet.exploded and bullet.explosion_timer <= 0:
                bullets_to_remove.append(bullet)
        
        # Remove used bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
    
    def draw(self, surface):
        # Draw weapon
        weapon_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, weapon_rect)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)

class WeaponManager:
    def __init__(self):
        self.weapons = []
        self.max_weapons = 6
        self.current_weapon = None
        
        # Add initial test weapon
        self.add_weapon("Basic Gun", 5, 1, "Sprites/Sprites_Weapon/Assaut-rifle-4-scoped.png", projectile_speed=8, damage=55, projectile_scale=(36, 36))
        
    def get_weapon(self, name):
        for weapon in self.weapons:
            if weapon.name.lower() == name.lower():
                return weapon
        return None

    def select_weapon(self, name):
        weapon = self.get_weapon(name)
        if weapon:
            self.current_weapon = weapon
            return True
        return False

    def add_weapon(self, name, fire_rate, reload_time, image_path, projectile_speed=5, damage=3000, projectile_radius=0, projectile_image="Sprites/Sprites_Effect/Bullets/14.png", projectile_scale=(48, 48), equip_on_add=False):
        existing = self.get_weapon(name)
        if existing:
            if equip_on_add:
                self.current_weapon = existing
            return False
        if len(self.weapons) >= self.max_weapons:
            return False

        weapon = Weapon(name, fire_rate, reload_time, image_path, projectile_speed, damage, projectile_radius, projectile_image, projectile_scale)
        self.weapons.append(weapon)
        if self.current_weapon is None or equip_on_add:
            self.current_weapon = weapon
        return True

    def cycle_weapon(self, direction=1):
        if not self.weapons:
            return
        index = self.weapons.index(self.current_weapon)
        self.current_weapon = self.weapons[(index + direction) % len(self.weapons)]
    
    def update(self, player_x, player_y, target_x, target_y, is_shooting, enemies):
        if not self.current_weapon:
            return False

        self.current_weapon.update_position(player_x, player_y, target_x, target_y)
        shot_fired = False
        if is_shooting:
            shot_fired = self.current_weapon.shoot(target_x, target_y)
        self.current_weapon.update_bullets(enemies)
        return shot_fired
    
    def draw(self, surface):
        if self.current_weapon:
            self.current_weapon.draw(surface)
