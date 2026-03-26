from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    LOOK_AHEAD_FACTOR, SMOOTH_FACTOR,
)


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_x, target_y, vel_x, vel_y, dt):
        target_x = (target_x + vel_x * LOOK_AHEAD_FACTOR) - SCREEN_WIDTH / 2
        target_y = (target_y + vel_y * LOOK_AHEAD_FACTOR) - SCREEN_HEIGHT / 2

        self.x += (target_x - self.x) * SMOOTH_FACTOR
        self.y += (target_y - self.y) * SMOOTH_FACTOR

        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))

    def apply(self, world_x, world_y):
        return int(world_x - self.x), int(world_y - self.y)
