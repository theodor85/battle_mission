import pygame
from pygame.locals import K_w, K_s, K_a, K_d, K_SPACE

import random

from app.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, MASS, MOVING_POWER, DAMPING,
    TILE_SIZE, MAP_COLS, MAP_ROWS, ROCK,
    BULLET_SPEED, SHOOT_COOLDOWN, TURRET_SHOOT_COOLDOWN,
    PLAYER_MAX_HP,
    EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_COUNT, EXPLOSION_FPS,
)


class Bullet:
    _DIRECTION_VECTORS = {
        'up':    ( 0, -1),
        'down':  ( 0,  1),
        'left':  (-1,  0),
        'right': ( 1,  0),
    }
    _images = None

    @classmethod
    def _load_images(cls):
        base = pygame.image.load("resources/shell_8x16.png").convert_alpha()
        cls._images = {
            'up':    base,
            'down':  pygame.transform.rotate(base, 180),
            'left':  pygame.transform.rotate(base, 90),
            'right': pygame.transform.rotate(base, -90),
        }

    def __init__(self, player_x, player_y, direction, player_w, player_h):
        if Bullet._images is None:
            Bullet._load_images()
        dx, dy = self._DIRECTION_VECTORS[direction]
        self.image = self._images[direction]
        w, h = self.image.get_size()

        # Спавн: центр танка + смещение вперёд вдоль направления
        center_x = player_x + player_w / 2
        center_y = player_y + player_h / 2
        offset = player_w / 2 + h / 2 if direction in ('up', 'down') else player_h / 2 + w / 2
        self.x = center_x + dx * offset - w / 2
        self.y = center_y + dy * offset - h / 2

        self.vx = dx * BULLET_SPEED
        self.vy = dy * BULLET_SPEED
        self.alive = True
        self.hit_pos = None
        self._w = w
        self._h = h

    def update(self, dt, game_map):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if (self.x < 0 or self.x + self._w >= WORLD_WIDTH
                or self.y < 0 or self.y + self._h >= WORLD_HEIGHT):
            self.alive = False
            return

        # Проверяем тайл в центре снаряда
        cx = self.x + self._w / 2
        cy = self.y + self._h / 2
        col = int(cx // TILE_SIZE)
        row = int(cy // TILE_SIZE)
        if 0 <= row < MAP_ROWS and 0 <= col < MAP_COLS:
            if game_map.tiles[row][col] == ROCK:
                self.hit_pos = (self.x, self.y)
                self.alive = False

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))


class Turret:
    def __init__(self, x, y):
        self.images = {
            'up': pygame.image.load("resources/turret_enemy_up.png").convert_alpha(),
            'down': pygame.image.load("resources/turret_enemy_down.png").convert_alpha(),
            'left': pygame.image.load("resources/turret_enemy_left.png").convert_alpha(),
            'right': pygame.image.load("resources/turret_enemy_right.png").convert_alpha(),
        }
        self.destroyed_image = pygame.image.load("resources/turret_destroyed.png").convert_alpha()
        self.direction = 'down'
        self.image = self.images[self.direction]
        self.x = x
        self.y = y
        self._w = self.image.get_width()
        self._h = self.image.get_height()
        self.alive = True
        self.shoot_timer = random.uniform(0, TURRET_SHOOT_COOLDOWN)

    def update(self, dt, player):
        if not self.alive:
            return None

        # Determine direction to player
        cx = self.x + self._w / 2
        cy = self.y + self._h / 2
        px = player.x + player.rect.width / 2
        py = player.y + player.rect.height / 2
        dx = px - cx
        dy = py - cy

        if abs(dx) >= abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
        self.image = self.images[self.direction]

        # Shoot
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = TURRET_SHOOT_COOLDOWN
            return Bullet(self.x, self.y, self.direction, self._w, self._h)
        return None

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self._w, self._h)


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
        self.direction = 'up'
        self.shoot_timer = 0.0
        self.hp = PLAYER_MAX_HP

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
        self.direction = direction
        self.image = self.images[direction]

    def shoot(self, dt):
        self.shoot_timer -= dt
        pressed = pygame.key.get_pressed()
        if pressed[K_SPACE] and self.shoot_timer <= 0:
            self.shoot_timer = SHOOT_COOLDOWN
            return Bullet(self.x, self.y, self.direction,
                          self.rect.width, self.rect.height)
        return None


class Explosion:
    _frames = None

    @classmethod
    def _load_frames(cls):
        sheet = pygame.image.load(
            "resources/explosion_spritesheet.png"
        ).convert_alpha()
        cls._frames = []
        for i in range(EXPLOSION_FRAME_COUNT):
            frame = sheet.subsurface(
                i * EXPLOSION_FRAME_SIZE, 0,
                EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE,
            )
            cls._frames.append(frame)

    def __init__(self, cx, cy):
        if Explosion._frames is None:
            Explosion._load_frames()
        self.x = cx - EXPLOSION_FRAME_SIZE / 2
        self.y = cy - EXPLOSION_FRAME_SIZE / 2
        self.timer = 0.0
        self.frame_index = 0
        self.alive = True

    def update(self, dt):
        self.timer += dt
        self.frame_index = int(self.timer * EXPLOSION_FPS)
        if self.frame_index >= EXPLOSION_FRAME_COUNT:
            self.alive = False

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(
                Explosion._frames[self.frame_index],
                camera.apply(self.x, self.y),
            )
