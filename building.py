#Code for the Building
import pygame

class Building:
    def __init__(self, x, y):
        # Khoi tao toa nha co ban
        self.x = x
        self.y = y

    def update(self):
        # Cap nhat trang thai toa nha
        pass

    def draw(self, surface):
        # Ve toa nha
        pygame.draw.rect(surface, (139, 69, 19), (self.x, self.y, 64, 64))
