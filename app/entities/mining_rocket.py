import math

import pygame

from app.entities.entity import Entity
from app.settings import (
    MINING_ROCKET_SPEED, MINING_ROCKET_WIDTH, MINING_ROCKET_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
)

_COLOR = (220, 80, 20)
_COLOR_TIP = (255, 200, 0)
_ARRIVE_THRESHOLD = 12.0


class MiningRocket(Entity):
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
        sx, sy = camera.apply(self.x, self.y)
        w, h = self.width, self.height
        pygame.draw.rect(surface, _COLOR, (sx, sy, w, h))
        pygame.draw.rect(surface, _COLOR_TIP, (sx + 2, sy, w - 4, h // 4))
