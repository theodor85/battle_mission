import pygame

from app.settings import MISSILE_SPEED
from app.entities.entity import Entity

_IMAGES = {
    'up':    'resources/images/missile/rocket_enemy_up.png',
    'down':  'resources/images/missile/rocket_enemy_down.png',
    'left':  'resources/images/missile/rocket_enemy_left.png',
    'right': 'resources/images/missile/rocket_enemy_right.png',
}

_DIRECTION_VECTORS = {
    'up':    (0, -1),
    'down':  (0,  1),
    'left':  (-1, 0),
    'right': ( 1, 0),
}

_loaded = {}


def _get_image(direction):
    if direction not in _loaded:
        _loaded[direction] = pygame.image.load(_IMAGES[direction]).convert_alpha()
    return _loaded[direction]


class Missile(Entity):
    def __init__(self, start_x, start_y, target_x, target_y, direction):
        self._image = _get_image(direction)
        w = self._image.get_width()
        h = self._image.get_height()
        super().__init__(start_x, start_y, w, h)
        self.target_x = target_x
        self.target_y = target_y
        self.direction = direction
        self.reached_target = False

        dx, dy = _DIRECTION_VECTORS[direction]
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
        surface.blit(self._image, camera.apply(self.x, self.y))
