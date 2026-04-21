# weapon.py
# Quản lý vũ khí, pool vũ khí, WeaponManager...

# Để trống, sẽ bổ sung sau khi tách xong các phần liên quan
import pygame
import math

_IMAGE_CACHE: dict[str, pygame.Surface] = {}

def _sheet(path: str) -> pygame.Surface:
    sheet = _IMAGE_CACHE.get(path)
    if sheet is None:
        sheet = pygame.image.load(path).convert_alpha()
        _IMAGE_CACHE[path] = sheet
    return sheet


def _slice_spec(path: str, x: int, y: int, w: int, h: int) -> str:
    return f"{path}#{x},{y},{w},{h}"


def _pick_from_atlas(atlas: str, tile_w: int, tile_h: int, coords: list[tuple[int, int]] | None = None) -> str:
    import random
    sheet = _sheet(atlas)
    max_tx = max(1, sheet.get_width() // max(1, tile_w))
    max_ty = max(1, sheet.get_height() // max(1, tile_h))

    if coords:
        valid = [(tx, ty) for (tx, ty) in coords if 0 <= tx < max_tx and 0 <= ty < max_ty]
        if valid:
            tx, ty = random.choice(valid)
            return _slice_spec(atlas, tx * tile_w, ty * tile_h, tile_w, tile_h)

    tx = random.randrange(0, max_tx)
    ty = random.randrange(0, max_ty)
    return _slice_spec(atlas, tx * tile_w, ty * tile_h, tile_w, tile_h)


class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=5, damage=3000, radius=0, image_path="Sprites/Sprites_Effect/Bullets/14.png", scale=(48, 48)):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.exploded = False
        self.explosion_timer = 0
        
        # Load and scale bullet image (safe fallback if missing/unsupported)
        # Supports atlas slicing with syntax: "path#x,y,w,h"
        try:
            path = image_path
            rect = None
            if "#" in image_path:
                path, spec = image_path.split("#", 1)
                parts = [p.strip() for p in spec.split(",")]
                if len(parts) == 4:
                    rect = pygame.Rect(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))

            sheet = _sheet(path)

            img = sheet
            if rect is not None:
                # Clamp rect into image bounds
                rect = rect.clip(sheet.get_rect())
                img = sheet.subsurface(rect).copy()

            self.original_image = pygame.transform.scale(img, scale)
        except Exception:
            self.original_image = pygame.Surface(scale, pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 220, 120, 220), (scale[0] // 2, scale[1] // 2), max(2, min(scale) // 4))

        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0
        
        # Calculate angle and rotate image
        self.angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.timer = 180 # Lifetime in frames
        self.melee = False
        
    def setup_melee(self, lifetime=12):
        self.melee = True
        self.timer = lifetime
        self.speed = 0
        self.dx = 0
        self.dy = 0
        
    def update(self):
        if self.exploded:
            self.explosion_timer -= 1
            return
        self.timer -= 1
        self.x += self.dx
        self.y += self.dy

    def explode(self):
        self.exploded = True
        self.explosion_timer = 8
        
    def draw(self, surface, camera=None):
        draw_pos = (int(self.x), int(self.y))
        zoom = 1.0
        if camera:
            draw_pos = camera.world_to_screen(self.x, self.y)
            zoom = camera.zoom
            
        if self.exploded and self.radius > 0:
            pygame.draw.circle(surface, (255, 160, 70), draw_pos, int(self.radius * zoom), 3)
            pygame.draw.circle(surface, (255, 220, 120), draw_pos, max(6, int(self.radius * zoom // 2)))
            return
        
        img = self.image
        if zoom != 1.0:
            img = pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
        
        rect = img.get_rect(center=draw_pos)
        surface.blit(img, rect.topleft)

class Weapon:
    def __init__(
        self,
        name,
        fire_rate,
        reload_time,
        image_path,
        projectile_speed=5,
        damage=3000,
        projectile_radius=0,
        projectile_image=None,
        projectile_scale=(48, 48),
        melee=False,
        mag_size=18,
        reserve_ammo=90,
    ):
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
        # Hiệu ứng đạn đẹp hơn
        if projectile_image is None:
            import random
            bullet_imgs = [f"Sprites/Sprites_Effect/Bullets/{i:02}.png" for i in range(1, 30)]
            self.projectile_image = random.choice(bullet_imgs)
        else:
            self.projectile_image = projectile_image
        self.projectile_scale = projectile_scale
        self.melee = melee
        # Ammo / reload
        self.mag_size = 9999 if self.melee else max(1, int(mag_size))
        self.ammo_in_mag = self.mag_size
        self.reserve_ammo = 0 if self.melee else max(0, int(reserve_ammo))
        self.reloading = False
        self.reload_end_time = 0
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
    
    def can_shoot(self, fire_rate_mult=1.0):
        if self.reloading:
            return False
        if not self.melee and self.ammo_in_mag <= 0:
            return False
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time > (1000 / (self.fire_rate * fire_rate_mult))

    def start_reload(self):
        if self.melee:
            return False
        if self.reloading:
            return False
        if self.reload_time <= 0:
            return False
        if self.ammo_in_mag >= self.mag_size:
            return False
        if self.reserve_ammo <= 0:
            return False
        self.reloading = True
        self.reload_end_time = pygame.time.get_ticks() + int(self.reload_time * 1000)
        return True

    def tick(self):
        """Returns True when a reload finishes."""
        if not self.reloading:
            return False
        if pygame.time.get_ticks() < self.reload_end_time:
            return False
        need = self.mag_size - self.ammo_in_mag
        take = min(need, self.reserve_ammo)
        self.ammo_in_mag += take
        self.reserve_ammo -= take
        self.reloading = False
        return True
    
    def shoot(self, target_x, target_y, fire_rate_mult=1.0, damage_mult=1.0):
        # Auto reload on empty
        if not self.melee and self.ammo_in_mag <= 0:
            self.start_reload()
            return False
        if self.can_shoot(fire_rate_mult):
            # Resolve projectile effect per shot (supports atlas random + list/dict)
            def pick_img(proj):
                import random
                if proj is None:
                    return None
                if isinstance(proj, (list, tuple)):
                    return pick_img(random.choice(proj)) if proj else None
                if isinstance(proj, dict):
                    atlas = proj.get("atlas")
                    tile = proj.get("tile")
                    tw = int(proj.get("tile_w", tile[0] if isinstance(tile, (list, tuple)) and len(tile) >= 1 else 16))
                    th = int(proj.get("tile_h", tile[1] if isinstance(tile, (list, tuple)) and len(tile) >= 2 else 16))
                    coords = proj.get("coords")
                    if atlas:
                        return _pick_from_atlas(atlas, tw, th, coords=coords)
                if isinstance(proj, str) and "#RANDOM" in proj:
                    # Syntax: "path#RANDOM,tw,th" or "path#RANDOM,tw,th,tx1:ty1|tx2:ty2..."
                    path, spec = proj.split("#", 1)
                    parts = [p.strip() for p in spec.split(",")]
                    if len(parts) >= 3 and parts[0].upper() == "RANDOM":
                        tw = int(parts[1])
                        th = int(parts[2])
                        coords = None
                        if len(parts) >= 4 and parts[3]:
                            coords = []
                            for pair in parts[3].split("|"):
                                if ":" in pair:
                                    a, b = pair.split(":", 1)
                                    try:
                                        coords.append((int(a), int(b)))
                                    except Exception:
                                        pass
                        return _pick_from_atlas(path, tw, th, coords=coords)
                return proj

            if self.melee:
                # Dung hieu ung slash tu projectile_image
                img_path = pick_img(self.projectile_image) if self.projectile_image else None
                img_path = img_path or "Sprites/Sprites_Effect/Pet_Power.png"
                slash = Bullet(self.x, self.y, target_x, target_y, speed=0, damage=self.damage * damage_mult, image_path=img_path, scale=self.projectile_scale)
                slash.setup_melee(lifetime=15)
                self.bullets.append(slash)
            else:
                import random
                if self.projectile_image:
                    img = pick_img(self.projectile_image)
                else:
                    bullet_imgs = [f"Sprites/Sprites_Effect/Bullets/{i:02}.png" for i in range(1, 30)]
                    img = random.choice(bullet_imgs)
                self.bullets.append(
                    Bullet(
                        self.x,
                        self.y,
                        target_x,
                        target_y,
                        speed=self.projectile_speed,
                        damage=self.damage * damage_mult,
                        radius=self.projectile_radius,
                        image_path=img,
                        scale=self.projectile_scale,
                    )
                )
                self.ammo_in_mag = max(0, self.ammo_in_mag - 1)
            self.last_shot_time = pygame.time.get_ticks()
            return True
        return False
    
    def update_bullets(self, enemies, blocked_tiles=None):
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.update()
            
            # Wall Collision
            if blocked_tiles:
                tx, ty = int(bullet.x // 16), int(bullet.y // 16)
                if (tx, ty) in blocked_tiles:
                    if bullet.radius > 0:
                        bullet.explode()
                        self._apply_explosion(bullet, enemies)
                    bullets_to_remove.append(bullet)
                    continue

            # Check collision with enemies
            for enemy in enemies:
                if not enemy.is_dead:
                    enemy_rect = pygame.Rect(enemy.x - 30, enemy.y - 30, 60, 60)
                    
                    if bullet.melee:
                        # Melee has larger hit area
                        bullet_rect = pygame.Rect(bullet.x - 50, bullet.y - 50, 100, 100)
                    else:
                        bullet_rect = pygame.Rect(bullet.x - 4, bullet.y - 4, 8, 8)
                    
                    if not bullet.exploded and bullet_rect.colliderect(enemy_rect):
                        if bullet.radius > 0:
                            bullet.explode()
                            self._apply_explosion(bullet, enemies)
                        else:
                            enemy.take_damage(bullet.damage)
                        
                        if not bullet.melee: # Bullets are consumed, melee slashes stay for duration
                            bullets_to_remove.append(bullet)
                            break
            
            # Remove bullets that are far away or exploded
            if bullet.timer <= 0:
                bullets_to_remove.append(bullet)
            if bullet.exploded and bullet.explosion_timer <= 0:
                bullets_to_remove.append(bullet)
        
        # Remove used bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

    def _apply_explosion(self, bullet, enemies):
        for splash_enemy in enemies:
            if not splash_enemy.is_dead:
                dist = math.hypot(splash_enemy.x - bullet.x, splash_enemy.y - bullet.y)
                if dist <= bullet.radius:
                    splash_enemy.take_damage(bullet.damage)
    
    def draw(self, surface, camera=None):
        # Draw weapon
        draw_pos = (self.x, self.y)
        zoom = 1.0
        if camera:
            draw_pos = camera.world_to_screen(self.x, self.y)
            zoom = camera.zoom
            
        img = self.rotated_image
        if zoom != 1.0:
            img = pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
            
        weapon_rect = img.get_rect(center=draw_pos)
        surface.blit(img, weapon_rect)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface, camera)

class WeaponManager:
    def __init__(self):
        self.weapons = []
        self.max_weapons = 6
        self.current_weapon = None
        # Optional callback: on_event(event_name: str, weapon: Weapon)
        self.on_event = None
        self._was_reloading = False
        
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

    def add_weapon(self, name, fire_rate, reload_time, image_path, projectile_speed=5, damage=3000, projectile_radius=0, projectile_image="Sprites/Sprites_Effect/Bullets/14.png", projectile_scale=(48, 48), equip_on_add=False, melee=False):
        existing = self.get_weapon(name)
        if existing:
            if equip_on_add:
                self.current_weapon = existing
            return False
        if len(self.weapons) >= self.max_weapons:
            return False

        lname = name.lower()
        if melee:
            mag, reserve = 9999, 0
        elif "shotgun" in lname:
            mag, reserve = 6, 36
        elif "sniper" in lname:
            mag, reserve = 5, 25
        elif "smg" in lname:
            mag, reserve = 24, 120
        elif "rocket" in lname:
            mag, reserve = 1, 6
        else:
            mag, reserve = 18, 90

        weapon = Weapon(
            name,
            fire_rate,
            reload_time,
            image_path,
            projectile_speed,
            damage,
            projectile_radius,
            projectile_image,
            projectile_scale,
            melee=melee,
            mag_size=mag,
            reserve_ammo=reserve,
        )
        self.weapons.append(weapon)
        if self.current_weapon is None or equip_on_add:
            self.current_weapon = weapon
        return True

    def cycle_weapon(self, direction=1):
        if not self.weapons:
            return
        index = self.weapons.index(self.current_weapon)
        self.current_weapon = self.weapons[(index + direction) % len(self.weapons)]
    
    def update(self, player_x, player_y, target_x, target_y, is_shooting, enemies, blocked_tiles=None, fire_rate_mult=1.0, damage_mult=1.0):
        if not self.current_weapon:
            return False

        self.current_weapon.update_position(player_x, player_y, target_x, target_y)
        was_reloading = self.current_weapon.reloading
        if self.current_weapon.tick():
            if self.on_event:
                self.on_event("reload_complete", self.current_weapon)
        shot_fired = False
        if is_shooting:
            shot_fired = self.current_weapon.shoot(target_x, target_y, fire_rate_mult, damage_mult)
            if shot_fired:
                if self.on_event:
                    self.on_event("shot", self.current_weapon)
        # Fire reload_start only on transition
        if (not was_reloading) and self.current_weapon.reloading and self.on_event:
            self.on_event("reload_start", self.current_weapon)
        self.current_weapon.update_bullets(enemies, blocked_tiles)
        return shot_fired

    def reload(self):
        if not self.current_weapon:
            return False
        ok = self.current_weapon.start_reload()
        if ok and self.on_event:
            self.on_event("reload_start", self.current_weapon)
        return ok
    
    def draw(self, surface, camera=None):
        if self.current_weapon:
            self.current_weapon.draw(surface, camera)