import pygame

# Screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
FPS = 60

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
ORANGE = (220, 220, 0) # было 140
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR_INK_DARK_DARKEST = (12, 26, 41)
DARK_GRAY = (60, 60, 60)

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

# Terrain generation — see app/landscape.py for profiles
from app.landscape import STEPPE as DEFAULT_LANDSCAPE

# Difficulty — see app/difficulty.py for profiles
from app.difficulty import EASY as DEFAULT_DIFFICULTY

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
PLAYER_SHOOT_COOLDOWN = 1.0  # секунд между выстрелами игрока

# Enemy tanks
ENEMY_TANK_HP = 120  # 3 × BULLET_DAMAGE

# Player HP
PLAYER_MAX_HP = 100
BULLET_DAMAGE = 40

# Explosions
EXPLOSION_FRAME_SIZE = 64
EXPLOSION_FRAME_COUNT = 9
EXPLOSION_FPS = 10

# Music
MUSIC_PATH = "resources/music/Azure Circuit.mp3"
MUSIC_VOLUME = 0.1
MUSIC_FADEOUT_MS = 2000  # плавное затухание при game over (мс)

# Scene fonts
TITLE_FONT_SIZE = 72
SUBTITLE_FONT_SIZE = 36

# Scene transition delay after game over (seconds)
GAME_OVER_DELAY = 2.5
