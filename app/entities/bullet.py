import pygame

from app.settings import (
    WORLD_WIDTH, WORLD_HEIGHT,
    TILE_SIZE, MAP_COLS, MAP_ROWS, ROCK,
    BULLET_SPEED,
)
from app.entities.entity import Entity


class Bullet(Entity):
    _DIRECTION_VECTORS = {
        'up':    ( 0, -1),
        'down':  ( 0,  1),
        'left':  (-1,  0),
        'right': ( 1,  0),
    }
    _images = None

    @classmethod
    def _load_images(cls):
        base = pygame.image.load("resources/images/bullet/shell_8x16.png").convert_alpha()
        cls._images = {
            'up':    base,
            'down':  pygame.transform.rotate(base, 180),
            'left':  pygame.transform.rotate(base, 90),
            'right': pygame.transform.rotate(base, -90),
        }

    def __init__(self, player_x, player_y, direction, player_w, player_h, game_map):
        if Bullet._images is None:
            Bullet._load_images()
        dx, dy = self._DIRECTION_VECTORS[direction]
        self.image = self._images[direction]
        w, h = self.image.get_size()

        center_x = player_x + player_w / 2
        center_y = player_y + player_h / 2
        offset = player_w / 2 + h / 2 if direction in ('up', 'down') else player_h / 2 + w / 2
        x = center_x + dx * offset - w / 2
        y = center_y + dy * offset - h / 2

        super().__init__(x, y, w, h)

        self.game_map = game_map
        self.vx = dx * BULLET_SPEED
        self.vy = dy * BULLET_SPEED
        self.hit_pos = None

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if (self.x < 0 or self.x + self.width >= WORLD_WIDTH
                or self.y < 0 or self.y + self.height >= WORLD_HEIGHT):
            self.alive = False
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        col = int(cx // TILE_SIZE)
        row = int(cy // TILE_SIZE)
        if 0 <= row < MAP_ROWS and 0 <= col < MAP_COLS:
            if self.game_map.tiles[row][col] == ROCK:
                self.hit_pos = (self.x, self.y)
                self.alive = False

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))
