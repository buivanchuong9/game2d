"""
camera.py — Camera system for infinite scrolling map.
Converts world coordinates to screen coordinates with smooth follow and shake.
"""
import math
import random


class Camera:
    def __init__(self, screen_w, screen_h, sidebar_w=256):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.sidebar_w = sidebar_w
        self.view_w = screen_w - sidebar_w
        self.view_h = screen_h
        self.x = 0.0   # Top-left of camera in world coords
        self.y = 0.0
        self.smoothing = 0.12   # Lower = smoother (lerp factor)

        # Shake
        self._shake_timer = 0
        self._shake_intensity = 0.0
        self._shake_ox = 0
        self._shake_oy = 0

    def update(self, player_wx, player_wy, world_w=2000, world_h=2000):
        """Smooth-follow player and clamp to world boundaries."""
        target_x = player_wx - self.view_w / 2
        target_y = player_wy - self.view_h / 2
        
        # Smooth follow
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
        
        # Clamp camera to world edges
        self.x = max(0, min(self.x, world_w - self.view_w))
        self.y = max(0, min(self.y, world_h - self.view_h))

        if self._shake_timer > 0:
            self._shake_timer -= 1
            mag = self._shake_intensity * (self._shake_timer / max(1, self._shake_timer + 1))
            self._shake_ox = random.randint(-int(mag), int(mag))
            self._shake_oy = random.randint(-int(mag), int(mag))
        else:
            self._shake_ox = 0
            self._shake_oy = 0

    def shake(self, intensity=8, duration=12):
        """Trigger a screen shake (e.g. explosion)."""
        self._shake_intensity = max(self._shake_intensity, intensity)
        self._shake_timer = max(self._shake_timer, duration)

    def world_to_screen(self, wx, wy):
        """Convert world pixel coords to screen pixel coords."""
        sx = wx - self.x + self._shake_ox
        sy = wy - self.y + self._shake_oy
        return int(sx), int(sy)

    def screen_to_world(self, sx, sy):
        """Convert screen pixel coords to world pixel coords."""
        wx = sx + self.x - self._shake_ox
        wy = sy + self.y - self._shake_oy
        return wx, wy

    def is_visible(self, wx, wy, margin=128):
        """Check if a world position is on screen (with margin for culling)."""
        sx, sy = self.world_to_screen(wx, wy)
        return (
            -margin <= sx <= self.view_w + margin
            and -margin <= sy <= self.view_h + margin
        )

    def get_visible_tile_range(self, tile_size):
        """Return (min_tx, max_tx, min_ty, max_ty) of visible tile grid."""
        min_tx = int(self.x // tile_size) - 2
        max_tx = int((self.x + self.view_w) // tile_size) + 2
        min_ty = int(self.y // tile_size) - 2
        max_ty = int((self.y + self.view_h) // tile_size) + 2
        return min_tx, max_tx, min_ty, max_ty
