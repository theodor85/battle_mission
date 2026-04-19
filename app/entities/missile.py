import pygame

from app.settings import MISSILE_SPEED, MISSILE_WIDTH, MISSILE_HEIGHT, MISSILE_COLOR
from app.entities.entity import Entity


class Missile(Entity):
    _DIRECTION_VECTORS = {
        'up':    (0, -1),
        'down':  (0,  1),
        'left':  (-1, 0),
        'right': ( 1, 0),
    }

    def __init__(self, start_x, start_y, target_x, target_y, direction):
        if direction in ('left', 'right'):
            w, h = MISSILE_HEIGHT, MISSILE_WIDTH
        else:
            w, h = MISSILE_WIDTH, MISSILE_HEIGHT
        super().__init__(start_x, start_y, w, h)
        self.target_x = target_x
        self.target_y = target_y
        self.direction = direction
        self.reached_target = False

        dx, dy = self._DIRECTION_VECTORS[direction]
        self.vx = dx * MISSILE_SPEED
        self.vy = dy * MISSILE_SPEED

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.direction == 'left' and self.x <= self.target_x:
            self._arrive()
        elif self.direction == 'right' and self.x >= self.target_x:
            self._arrive()
        elif self.direction == 'up' and self.y <= self.target_y:
            self._arrive()
        elif self.direction == 'down' and self.y >= self.target_y:
            self._arrive()

    def _arrive(self):
        self.reached_target = True
        self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x, self.y)
        pygame.draw.rect(surface, MISSILE_COLOR, (sx, sy, self.width, self.height))
