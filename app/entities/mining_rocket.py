import math

import pygame

from app.entities.entity import Entity
from app.settings import (
    MINING_ROCKET_SPEED, MINING_ROCKET_WIDTH, MINING_ROCKET_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
)

_ARRIVE_THRESHOLD = 12.0
_IMAGE_PATH = "resources/images/mining_vehicle/rocket_mining_30x34.png"


class MiningRocket(Entity):
    _base_image = None

    @classmethod
    def _load_image(cls):
        cls._base_image = pygame.image.load(_IMAGE_PATH).convert_alpha()

    def __init__(self, start_x, start_y, target_x, target_y, target_col, target_row):
        super().__init__(
            start_x - MINING_ROCKET_WIDTH / 2,
            start_y - MINING_ROCKET_HEIGHT / 2,
            MINING_ROCKET_WIDTH,
            MINING_ROCKET_HEIGHT,
        )
        self.target_x = target_x
        self.target_y = target_y
        self.target_col = target_col
        self.target_row = target_row
        self.reached_target = False

        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            dist = 1.0
        self.vx = dx / dist * MINING_ROCKET_SPEED
        self.vy = dy / dist * MINING_ROCKET_SPEED

        if MiningRocket._base_image is None:
            MiningRocket._load_image()
        angle_deg = -math.degrees(math.atan2(self.vy, self.vx)) - 90
        self.image = pygame.transform.rotate(MiningRocket._base_image, angle_deg)

    def _cx(self):
        return self.x + self.width / 2

    def _cy(self):
        return self.y + self.height / 2

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        dist = math.hypot(self._cx() - self.target_x, self._cy() - self.target_y)
        if dist < _ARRIVE_THRESHOLD:
            self.reached_target = True
            self.alive = False
            return

        # Kill if goes off map with buffer
        if (self.x < -200 or self.x > WORLD_WIDTH + 200
                or self.y < -200 or self.y > WORLD_HEIGHT + 200):
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply(self._cx(), self._cy())
        rect = self.image.get_rect(center=(sx, sy))
        surface.blit(self.image, rect)
