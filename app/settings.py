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

# Tile behaviour types
GROUND = 0   # can drive, bullets fly over
WATER  = 1   # can't drive, bullets fly over
ROCK   = 2   # can't drive, bullets explode
BRICK  = 3   # can't drive, bullets destroy tile → GROUND

TILE_COLORS = {
    GROUND: (34, 139, 34),
    WATER:  (0, 105, 148),
    ROCK:   (128, 128, 128),
    BRICK:  (180, 80, 40),
}

# Named tile definitions: each has a texture path and a behaviour type
TILES = {
    'GRASS': {'path': "resources/images/textures/grass_tile.png", 'type': GROUND},
    'WATER': {'path': "resources/images/textures/water_tile.png", 'type': WATER},
    'ROCK':  {'path': "resources/images/textures/rock_tile.png",  'type': ROCK},
    'BRICK': {'path': None, 'type': BRICK},
}

# Default named tile for each behaviour type (used when converting, e.g. BRICK → GROUND)
DEFAULT_TILE = {
    GROUND: 'GRASS',
    WATER:  'WATER',
    ROCK:   'ROCK',
    BRICK:  'BRICK',
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

# Missiles
MISSILE_SPEED = 400.0
MISSILE_INTERVAL_MIN = 20.0
MISSILE_INTERVAL_MAX = 30.0
MISSILE_AIM_OFFSET_TILES = 3
MISSILE_SAFE_RADIUS_TILES = 5     # не спавнить ракету если рядом враги
MISSILE_DAMAGE_TIERS = {0: 200, 1: 110, 2: 80, 3: 40}
MISSILE_EXPLOSION_SCALE = 3.0

# Camera shake
CAMERA_SHAKE_DURATION = 0.5
CAMERA_SHAKE_INTENSITY = 15

# Helicopter
HELICOPTER_SPEED = 200.0
HELICOPTER_HOVER_TIME = 0.5
HELICOPTER_WIDTH = 100
HELICOPTER_HEIGHT = 100

# Mining vehicle
MINING_VEHICLE_HP = 80
MINING_VEHICLE_COUNT = 2
MINING_VEHICLE_MOVE_SPEED = 150.0
MINING_VEHICLE_MOVE_AWAY_DISTANCE = 600.0
MINING_VEHICLE_MOVE_AWAY_TIMEOUT = 10.0  # переход в ожидание, если застряла
MINING_VEHICLE_PICKUP_WAIT = 10.0
MINING_VEHICLE_REDELIVERY_COOLDOWN = 30.0
MINING_VEHICLE_INITIAL_COOLDOWN_1 = 12.0
MINING_VEHICLE_INITIAL_COOLDOWN_2 = 25.0

# Mining rockets
MINING_ROCKET_SPEED = 400.0
MINING_ROCKET_COUNT = 5
MINING_ROCKET_SHOOT_COOLDOWN = 2.0
MINING_ROCKET_AIM_RANGE_TILES = 10
MINING_ROCKET_INITIAL_DELAY = 1.5
MINING_ROCKET_WIDTH = 30
MINING_ROCKET_HEIGHT = 34

# Mines
MINE_DAMAGE = 10

# Drop point: minimum Manhattan distance in tiles from player
HELICOPTER_DROP_MIN_DIST_TILES = 15

# Music
MUSIC_PATH = "resources/music/Azure Circuit.mp3"
MUSIC_VOLUME = 0.1
MUSIC_FADEOUT_MS = 2000  # плавное затухание при game over (мс)

# Sound effects
SHOOT_SOUND_PATH = "resources/sounds/shoot/shoot.mp3"
SHOOT_SOUND_VOLUME = 0.3
HIT_SOUND_PATH = "resources/sounds/shoot/hit.mp3"
HIT_SOUND_VOLUME = 0.1

# Scene fonts
TITLE_FONT_SIZE = 72
SUBTITLE_FONT_SIZE = 36

# Scene transition delay after game over (seconds)
GAME_OVER_DELAY = 2.5

# Friendly base location
BASE_COLS = 24
BASE_ROWS = 20
BUILDING_WIDTH_TILES = 6
BUILDING_HEIGHT_TILES = 5
BUILDING_LABEL_FONT_SIZE = 28
BUILDING_GARAGE_COLOR = (70, 90, 130)
BUILDING_SHOP_COLOR = (180, 140, 60)
BUILDING_HQ_COLOR = (130, 50, 60)
BUILDING_WALL_COLOR = (40, 40, 40)
HQ_DOOR_WIDTH_TILES = 2
HQ_FADE_DURATION = 1.0
