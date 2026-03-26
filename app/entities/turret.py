import random

import pygame

from app.settings import TURRET_SHOOT_COOLDOWN
from app.entities.entity import Entity
from app.entities.bullet import Bullet


class Turret(Entity):
    def __init__(self, x, y, game_map):
        self.images = {
            'up': pygame.image.load("resources/turret_enemy_up.png").convert_alpha(),
            'down': pygame.image.load("resources/turret_enemy_down.png").convert_alpha(),
            'left': pygame.image.load("resources/turret_enemy_left.png").convert_alpha(),
            'right': pygame.image.load("resources/turret_enemy_right.png").convert_alpha(),
        }
        self.destroyed_image = pygame.image.load("resources/turret_destroyed.png").convert_alpha()
        self.direction = 'down'
        self.image = self.images[self.direction]
        w = self.image.get_width()
        h = self.image.get_height()

        super().__init__(x, y, w, h)

        self.game_map = game_map
        self.shoot_timer = random.uniform(0, TURRET_SHOOT_COOLDOWN)
        self.target_pos = (x, y)

    def update(self, dt):
        if not self.alive:
            return None

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        tx, ty = self.target_pos
        dx = tx - cx
        dy = ty - cy

        if abs(dx) >= abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
        self.image = self.images[self.direction]

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = TURRET_SHOOT_COOLDOWN
            return Bullet(self.x, self.y, self.direction, self.width, self.height, self.game_map)
        return None

    def destroy(self):
        self.alive = False
        self.image = self.destroyed_image

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))
