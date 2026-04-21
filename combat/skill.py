# skill.py
# Quản lý kỹ năng, Skill, SkillManager...

# Để trống, sẽ bổ sung sau khi tách xong các phần liên quan
import pygame
import math

class Skill:
    def __init__(self, name, cooldown, icon_path, effect_image_paths=None, scale=(48,48), effect_scale=(64,64), is_gif=False, rows=1, cols=1, sheet_rect=None, damage=1500):
        self.name = name
        self.cooldown = cooldown
        self.last_used = -99999
        self.damage = damage
        self.icon = pygame.image.load(icon_path).convert_alpha()
        self.icon = pygame.transform.scale(self.icon, scale)
        self.effect_frames = []
        self.is_gif = is_gif
        
        if effect_image_paths:
            if isinstance(effect_image_paths, str):
                full_sheet = pygame.image.load(effect_image_paths).convert_alpha()
                if sheet_rect:
                    full_sheet = full_sheet.subsurface(sheet_rect)
                
                sw, sh = full_sheet.get_size()
                fw, fh = sw // cols, sh // rows
                for r in range(rows):
                    for c in range(cols):
                        frame = full_sheet.subsurface((c * fw, r * fh, fw, fh))
                        self.effect_frames.append(pygame.transform.scale(frame, effect_scale))
            else:
                self.effect_frames = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), effect_scale) for p in effect_image_paths]
        
        self.active_effects = [] # List of [x, y, timer, frame_index, dx, dy]

    def can_use(self):
        return pygame.time.get_ticks() - self.last_used > self.cooldown

    def use(self, x, y, target_x, target_y):
        if self.can_use():
            self.last_used = pygame.time.get_ticks()
            angle = math.atan2(target_y - y, target_x - x)
            fx = x + math.cos(angle) * 40
            fy = y + math.sin(angle) * 40
            self.active_effects.append([fx, fy, 40, 0, math.cos(angle)*10, math.sin(angle)*10])
            return True
        return False

    def update(self, enemies=None, blocked_tiles=None, tile_size=16):
        to_remove = []
        for i, eff in enumerate(self.active_effects):
            eff[2] -= 1 # Timer
            eff[0] += eff[4] # Move X
            eff[1] += eff[5] # Move Y
            
            # Animation
            if len(self.effect_frames) > 0:
                eff[3] = (eff[3] + 1) % len(self.effect_frames)
            
            # Wall Collision
            if blocked_tiles:
                tx, ty = int(eff[0] // tile_size), int(eff[1] // tile_size)
                if (tx, ty) in blocked_tiles:
                    to_remove.append(i)
                    continue

            # Enemy Collision
            if enemies:
                eff_rect = pygame.Rect(eff[0]-20, eff[1]-20, 40, 40)
                hit = False
                for enemy in enemies:
                    if not enemy.is_dead:
                        e_rect = pygame.Rect(enemy.x-25, enemy.y-25, 50, 50)
                        if eff_rect.colliderect(e_rect):
                            enemy.take_damage(self.damage)
                            hit = True
                if hit:
                    to_remove.append(i)
                    continue

        self.active_effects = [obj for i, obj in enumerate(self.active_effects) if i not in to_remove and obj[2] > 0]

    def draw(self, surface, camera=None):
        for eff in self.active_effects:
            draw_pos = (eff[0], eff[1])
            zoom = 1.0
            if camera:
                draw_pos = camera.world_to_screen(eff[0], eff[1])
                zoom = camera.zoom
            
            if self.effect_frames:
                frame = self.effect_frames[eff[3]]
                if zoom != 1.0:
                    frame = pygame.transform.scale(frame, (int(frame.get_width() * zoom), int(frame.get_height() * zoom)))
                rect = frame.get_rect(center=draw_pos)
                surface.blit(frame, rect)
            else:
                pygame.draw.circle(surface, (255, 255, 0), draw_pos, int(20 * zoom), 2)

class SkillManager:
    def __init__(self):
        self.skills = []
        self.max_skills = 6

    def add_skill(self, skill):
        if len(self.skills) < self.max_skills:
            self.skills.append(skill)

    def use_skill(self, index, x, y, target_x, target_y):
        if 0 <= index < len(self.skills):
            return self.skills[index].use(x, y, target_x, target_y)
        return False

    def update(self, enemies=None, blocked_tiles=None):
        for skill in self.skills:
            skill.update(enemies, blocked_tiles)

    def draw(self, surface, camera=None):
        for skill in self.skills:
            skill.draw(surface, camera)
