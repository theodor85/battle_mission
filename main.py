import sys, random

import pygame
from pygame.locals import *


pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000

FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Map
TILE_SIZE = 50
MAP_COLS = 50
MAP_ROWS = 50
WORLD_WIDTH = MAP_COLS * TILE_SIZE
WORLD_HEIGHT = MAP_ROWS * TILE_SIZE

# Tile types
GROUND = 0
ROCK = 1
WATER = 2

TILE_COLORS = {
    GROUND: (34, 139, 34),
    ROCK:   (128, 128, 128),
    WATER:  (0, 105, 148),
}

# Physics
MASS = 15.0
MOVING_POWER = 10.0
DAMPING = 0.85

# Camera
LOOK_AHEAD_FACTOR = 15.0
SMOOTH_FACTOR = 0.08

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moving")


def generate_map():
    tile_map = [[GROUND] * MAP_COLS for _ in range(MAP_ROWS)]
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            val = random.random()
            if val < 0.10:
                tile_map[r][c] = ROCK
            elif val < 0.18:
                tile_map[r][c] = WATER
    return tile_map


def draw_tiles(surface, tile_map, camera):
    start_col = max(0, int(camera.x // TILE_SIZE))
    start_row = max(0, int(camera.y // TILE_SIZE))
    end_col = min(MAP_COLS, int((camera.x + SCREEN_WIDTH) // TILE_SIZE) + 1)
    end_row = min(MAP_ROWS, int((camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 1)

    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            world_x = c * TILE_SIZE
            world_y = r * TILE_SIZE
            screen_x, screen_y = camera.apply(world_x, world_y)
            pygame.draw.rect(
                surface,
                TILE_COLORS[tile_map[r][c]],
                (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
            )


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill(BLUE)
        self.rect = self.surf.get_rect()

        self.x = float(WORLD_WIDTH // 2)
        self.y = float(WORLD_HEIGHT // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.moving_power_x = 0
        self.moving_power_y = 0

    def move(self):
        self.handle_input()
        self.calculate_speed()
        self.x += self.speed_x
        self.y += self.speed_y
        self.keep_on_map()

    def handle_input(self):
        self.moving_power_x = 0
        self.moving_power_y = 0

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.moving_power_y = -MOVING_POWER
        if pressed_keys[K_s]:
            self.moving_power_y = MOVING_POWER
        if pressed_keys[K_a]:
            self.moving_power_x = -MOVING_POWER
        if pressed_keys[K_d]:
            self.moving_power_x = MOVING_POWER

    def calculate_speed(self):
        self.speed_x = (self.speed_x + self.moving_power_x / MASS) * DAMPING
        self.speed_y = (self.speed_y + self.moving_power_y / MASS) * DAMPING

        if abs(self.speed_x) < 0.01:
            self.speed_x = 0
        if abs(self.speed_y) < 0.01:
            self.speed_y = 0

    def keep_on_map(self):
        if self.x < 0:
            self.x = 0
            if self.speed_x < 0:
                self.speed_x = 0
        if self.x + self.rect.width > WORLD_WIDTH:
            self.x = WORLD_WIDTH - self.rect.width
            if self.speed_x > 0:
                self.speed_x = 0
        if self.y < 0:
            self.y = 0
            if self.speed_y < 0:
                self.speed_y = 0
        if self.y + self.rect.height > WORLD_HEIGHT:
            self.y = WORLD_HEIGHT - self.rect.height
            if self.speed_y > 0:
                self.speed_y = 0


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, player):
        target_x = (player.x + player.speed_x * LOOK_AHEAD_FACTOR) - SCREEN_WIDTH / 2
        target_y = (player.y + player.speed_y * LOOK_AHEAD_FACTOR) - SCREEN_HEIGHT / 2

        self.x += (target_x - self.x) * SMOOTH_FACTOR
        self.y += (target_y - self.y) * SMOOTH_FACTOR

        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))

    def apply(self, world_x, world_y):
        return int(world_x - self.x), int(world_y - self.y)


tile_map = generate_map()
camera = Camera()
P1 = Player()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    P1.move()
    camera.update(P1)

    DISPLAYSURF.fill(BLACK)
    draw_tiles(DISPLAYSURF, tile_map, camera)
    DISPLAYSURF.blit(P1.surf, camera.apply(P1.x, P1.y))

    pygame.display.update()
    FramePerSec.tick(FPS)
