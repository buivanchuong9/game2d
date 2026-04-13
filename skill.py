import pygame
import math

class Skill:
    def __init__(self, name, cooldown, image_path, effect_image_path=None, scale=(48,48), effect_scale=(48,48)):
        self.name = name
        self.cooldown = cooldown  # milliseconds
        self.last_used = -99999
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
        self.effect_image = None
        if effect_image_path:
            self.effect_image = pygame.image.load(effect_image_path).convert_alpha()
            self.effect_image = pygame.transform.scale(self.effect_image, effect_scale)
        self.active_effects = []  # List of (x, y, timer)

    def can_use(self):
        return pygame.time.get_ticks() - self.last_used > self.cooldown

    def use(self, x, y, target_x, target_y):
        if self.can_use():
            self.last_used = pygame.time.get_ticks()
            angle = math.atan2(target_y - y, target_x - x)
            fx = x + math.cos(angle) * 60
            fy = y + math.sin(angle) * 60
            self.active_effects.append([fx, fy, 18])
            return True
        return False

    def update(self):
        for eff in self.active_effects:
            eff[2] -= 1
        self.active_effects = [eff for eff in self.active_effects if eff[2] > 0]

    def draw(self, surface):
        for eff in self.active_effects:
            if self.effect_image:
                rect = self.effect_image.get_rect(center=(eff[0], eff[1]))
                surface.blit(self.effect_image, rect)
            else:
                pygame.draw.circle(surface, (255, 255, 0), (int(eff[0]), int(eff[1])), 32, 3)

class SkillManager:
    def __init__(self):
        self.skills = []
        self.max_skills = 6
        self.current_skill = None
        self.last_used_index = -1

    def add_skill(self, skill):
        if len(self.skills) < self.max_skills:
            self.skills.append(skill)
            if self.current_skill is None:
                self.current_skill = skill

    def use_skill(self, index, x, y, target_x, target_y):
        if 0 <= index < len(self.skills):
            used = self.skills[index].use(x, y, target_x, target_y)
            if used:
                self.last_used_index = index
            return used
        return False

    def update(self):
        for skill in self.skills:
            skill.update()

    def draw(self, surface):
        for skill in self.skills:
            skill.draw(surface)
