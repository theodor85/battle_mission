import pygame

# Screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
FPS = 60

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
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
    ROCK: (128, 128, 128),
    WATER: (0, 105, 148),
}

# Terrain generation
ROCK_SEED_CHANCE = 0.22
ROCK_SMOOTH_ITERATIONS = 5
ROCK_NEIGHBOR_THRESHOLD = 4
RIVER_COUNT = 2
LAKE_COUNT = 3
LAKE_MAX_SIZE = 25
SPAWN_CLEAR_RADIUS = 3

# Physics
MASS = 15.0
MOVING_POWER = 10.0
DAMPING = 0.85

# Camera
LOOK_AHEAD_FACTOR = 15.0
SMOOTH_FACTOR = 0.08

# Bullets
BULLET_SPEED = 400.0        # пикселей в секунду
BULLET_WIDTH = 8             # ширина снаряда (поперёк направления)
BULLET_HEIGHT = 16           # длина снаряда (вдоль направления)
BULLET_COLOR = (255, 255, 0) # жёлтый
SHOOT_COOLDOWN = 1.0         # секунд между выстрелами (1 раз в секунду)

# Turrets
NUMBER_OF_TURRETS = 5
TURRET_SHOOT_COOLDOWN = 2.0  # секунд между выстрелами туррели

# Player HP
PLAYER_MAX_HP = 100
BULLET_DAMAGE = 50
