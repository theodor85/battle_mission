import random

from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    LOOK_AHEAD_FACTOR, SMOOTH_FACTOR,
)


class Camera:
    def __init__(self, world_width=None, world_height=None, follow=True):
        self.x = 0.0
        self.y = 0.0
        self._world_width = world_width if world_width is not None else WORLD_WIDTH
        self._world_height = world_height if world_height is not None else WORLD_HEIGHT
        self._follow = follow
        self._shake_timer = 0.0
        self._shake_intensity = 0
        self._shake_offset_x = 0
        self._shake_offset_y = 0

    def start_shake(self, duration, intensity):
        self._shake_timer = duration
        self._shake_intensity = intensity

    def update(self, target_x, target_y, vel_x, vel_y, dt):
        if self._follow:
            target_x = (target_x + vel_x * LOOK_AHEAD_FACTOR) - SCREEN_WIDTH / 2
            target_y = (target_y + vel_y * LOOK_AHEAD_FACTOR) - SCREEN_HEIGHT / 2

            self.x += (target_x - self.x) * SMOOTH_FACTOR
            self.y += (target_y - self.y) * SMOOTH_FACTOR

            self.x = max(0, min(self.x, self._world_width - SCREEN_WIDTH))
            self.y = max(0, min(self.y, self._world_height - SCREEN_HEIGHT))

        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._shake_offset_x = random.randint(-self._shake_intensity, self._shake_intensity)
            self._shake_offset_y = random.randint(-self._shake_intensity, self._shake_intensity)
        else:
            self._shake_offset_x = 0
            self._shake_offset_y = 0

    def apply(self, world_x, world_y):
        return (int(world_x - self.x) + self._shake_offset_x,
                int(world_y - self.y) + self._shake_offset_y)

    def is_visible(self, world_x, world_y):
        return (self.x <= world_x <= self.x + SCREEN_WIDTH
                and self.y <= world_y <= self.y + SCREEN_HEIGHT)
