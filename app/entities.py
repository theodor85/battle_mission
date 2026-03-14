import pygame
from pygame.locals import K_w, K_s, K_a, K_d

from app.settings import WORLD_WIDTH, WORLD_HEIGHT, MASS, MOVING_POWER, DAMPING


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = {
            'up': pygame.image.load("resources/tank_up.png"),
            'down': pygame.image.load("resources/tank_down.png"),
            'left': pygame.image.load("resources/tank_left.png"),
            'right': pygame.image.load("resources/tank_right.png"),
        }
        self.image = self.images['up']
        self.rect = self.image.get_rect()

        self.x = float(WORLD_WIDTH // 2)
        self.y = float(WORLD_HEIGHT // 2)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.moving_power_x = 0.0
        self.moving_power_y = 0.0

    def update(self, dt, game_map):
        self._handle_input()
        self._calculate_speed(dt)
        self._apply_movement(game_map)
        self._keep_on_map()
        self._update_direction()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))

    def _handle_input(self):
        self.moving_power_x = 0.0
        self.moving_power_y = 0.0

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.moving_power_y = -MOVING_POWER
        if pressed_keys[K_s]:
            self.moving_power_y = MOVING_POWER
        if pressed_keys[K_a]:
            self.moving_power_x = -MOVING_POWER
        if pressed_keys[K_d]:
            self.moving_power_x = MOVING_POWER

    def _calculate_speed(self, dt):
        self.speed_x = (self.speed_x + self.moving_power_x / MASS) * DAMPING
        self.speed_y = (self.speed_y + self.moving_power_y / MASS) * DAMPING

        if abs(self.speed_x) < 0.01:
            self.speed_x = 0.0
        if abs(self.speed_y) < 0.01:
            self.speed_y = 0.0

    def _apply_movement(self, game_map):
        w, h = self.rect.width, self.rect.height

        self.x += self.speed_x
        tank_rect = pygame.Rect(self.x, self.y, w, h)
        if tank_rect.collidelist(game_map.get_blocked_rects(self.x, self.y, w, h)) != -1:
            self.x -= self.speed_x
            self.speed_x = 0.0

        self.y += self.speed_y
        tank_rect = pygame.Rect(self.x, self.y, w, h)
        if tank_rect.collidelist(game_map.get_blocked_rects(self.x, self.y, w, h)) != -1:
            self.y -= self.speed_y
            self.speed_y = 0.0

    def _keep_on_map(self):
        if self.x < 0:
            self.x = 0.0
            if self.speed_x < 0:
                self.speed_x = 0.0
        if self.x + self.rect.width > WORLD_WIDTH:
            self.x = float(WORLD_WIDTH - self.rect.width)
            if self.speed_x > 0:
                self.speed_x = 0.0
        if self.y < 0:
            self.y = 0.0
            if self.speed_y < 0:
                self.speed_y = 0.0
        if self.y + self.rect.height > WORLD_HEIGHT:
            self.y = float(WORLD_HEIGHT - self.rect.height)
            if self.speed_y > 0:
                self.speed_y = 0.0

    def _update_direction(self):
        if abs(self.speed_x) < 0.01 and abs(self.speed_y) < 0.01:
            return
        if abs(self.speed_x) >= abs(self.speed_y):
            direction = 'right' if self.speed_x > 0 else 'left'
        else:
            direction = 'down' if self.speed_y > 0 else 'up'
        self.image = self.images[direction]
