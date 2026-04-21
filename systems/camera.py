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
        self.zoom = 2.0         # Default zoom level (2x as requested "phóng to")

        # Shake
        self._shake_timer = 0
        self._shake_intensity = 0.0
        self._shake_ox = 0
        self._shake_oy = 0

    def update(self, player_wx, player_wy, world_w=None, world_h=None):
        """Smooth-follow player. Clamp only if world dimensions are provided."""
        # Calculate target top-left to center player
        # With zoom, the effective view size in world coordinates is smaller
        world_view_w = self.view_w / self.zoom
        world_view_h = self.view_h / self.zoom
        
        target_x = player_wx - world_view_w / 2
        target_y = player_wy - world_view_h / 2
        
        # Smooth follow
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
        
        # Clamp camera to world edges ONLY if world bounds are given
        if world_w is not None and world_h is not None:
            self.x = max(0, min(self.x, world_w - world_view_w))
            self.y = max(0, min(self.y, world_h - world_view_h))

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
        """Convert world pixel coords to screen pixel coords with zoom."""
        sx = (wx - self.x) * self.zoom + self._shake_ox
        sy = (wy - self.y) * self.zoom + self._shake_oy
        return int(sx), int(sy)

    def screen_to_world(self, sx, sy):
        """Convert screen pixel coords to world pixel coords with zoom."""
        wx = (sx - self._shake_ox) / self.zoom + self.x
        wy = (sy - self._shake_oy) / self.zoom + self.y
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
        world_view_w = self.view_w / self.zoom
        world_view_h = self.view_h / self.zoom
        min_tx = int(self.x // tile_size) - 2
        max_tx = int((self.x + world_view_w) // tile_size) + 2
        min_ty = int(self.y // tile_size) - 2
        max_ty = int((self.y + world_view_h) // tile_size) + 2
        return min_tx, max_tx, min_ty, max_ty
