import math
import random

import pygame

from app.entities.entity import Entity
from app.settings import (
    MINING_VEHICLE_HP, MINING_VEHICLE_MOVE_SPEED,
    MINING_VEHICLE_MOVE_AWAY_DISTANCE, MINING_VEHICLE_MOVE_AWAY_TIMEOUT,
    MINING_VEHICLE_PICKUP_WAIT,
    MINING_ROCKET_COUNT, MINING_ROCKET_SHOOT_COOLDOWN,
    MINING_ROCKET_AIM_RANGE_TILES, MINING_ROCKET_INITIAL_DELAY,
    TILE_SIZE, MAP_COLS, MAP_ROWS,
    WORLD_WIDTH, WORLD_HEIGHT,
)

_IMAGE_PATHS = {
    'up':    'resources/images/mining_vehicle/mining_vehicle_up.png',
    'down':  'resources/images/mining_vehicle/mining_vehicle_down.png',
    'left':  'resources/images/mining_vehicle/mining_vehicle_left.png',
    'right': 'resources/images/mining_vehicle/mining_vehicle_right.png',
}


class MiningVehicle(Entity):
    INACTIVE = 'inactive'
    SHOOTING = 'shooting'
    MOVING_AWAY = 'moving_away'
    WAITING_FOR_PICKUP = 'waiting_for_pickup'
    DESTROYED = 'destroyed'

    def __init__(self, game_map):
        self.images = {d: pygame.image.load(p).convert_alpha()
                       for d, p in _IMAGE_PATHS.items()}
        self.game_map = game_map
        self.direction = 'right'
        self.image = self.images['right']
        img = self.image
        super().__init__(0.0, 0.0, img.get_width(), img.get_height())

        self.hp = MINING_VEHICLE_HP
        self.state = self.INACTIVE
        self.destroyed_permanently = False
        self.delivery_cooldown = 0.0
        self.rockets_left = 0
        self.shoot_timer = 0.0
        self.pickup_timer = 0.0
        self.move_away_timer = 0.0

    @property
    def on_map(self):
        return self.state in (self.SHOOTING, self.MOVING_AWAY, self.WAITING_FOR_PICKUP)

    def place(self, world_x, world_y):
        # Position centered on world_x, world_y using current image size
        self.x = world_x - self.width / 2
        self.y = world_y - self.height / 2
        self.hp = MINING_VEHICLE_HP
        self.state = self.SHOOTING
        self.rockets_left = MINING_ROCKET_COUNT
        self.shoot_timer = MINING_ROCKET_INITIAL_DELAY
        self.move_away_timer = 0.0

    def _set_direction(self, direction):
        if direction == self.direction:
            return
        # Preserve center so the vehicle doesn't jump when sprite size changes
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        self.direction = direction
        self.image = self.images[direction]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = cx - self.width / 2
        self.y = cy - self.height / 2

    def _face_direction(self, dx, dy):
        if abs(dx) >= abs(dy):
            self._set_direction('right' if dx >= 0 else 'left')
        else:
            self._set_direction('down' if dy >= 0 else 'up')

    def update(self, dt, player_cx, player_cy):
        vcx = self.x + self.width / 2
        vcy = self.y + self.height / 2
        if self.state == self.SHOOTING:
            # Face toward player
            self._face_direction(player_cx - vcx, player_cy - vcy)
        elif self.state == self.MOVING_AWAY:
            self._move_away(dt, player_cx, player_cy)

    def _move_away(self, dt, player_cx, player_cy):
        self.move_away_timer += dt

        vcx = self.x + self.width / 2
        vcy = self.y + self.height / 2
        dx = vcx - player_cx
        dy = vcy - player_cy
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            dx, dy, dist = 1.0, 0.0, 1.0

        # Face in movement direction (away from player)
        self._face_direction(dx, dy)

        step_x = dx / dist * MINING_VEHICLE_MOVE_SPEED * dt
        step_y = dy / dist * MINING_VEHICLE_MOVE_SPEED * dt

        # X axis — separate check so the vehicle slides along obstacles
        self.x += step_x
        self.x = max(0.0, min(WORLD_WIDTH - self.width, self.x))
        blocked = self.game_map.get_blocked_rects(self.x, self.y, self.width, self.height)
        if pygame.Rect(self.x, self.y, self.width, self.height).collidelist(blocked) != -1:
            self.x -= step_x
            self.x = max(0.0, min(WORLD_WIDTH - self.width, self.x))

        # Y axis
        self.y += step_y
        self.y = max(0.0, min(WORLD_HEIGHT - self.height, self.y))
        blocked = self.game_map.get_blocked_rects(self.x, self.y, self.width, self.height)
        if pygame.Rect(self.x, self.y, self.width, self.height).collidelist(blocked) != -1:
            self.y -= step_y
            self.y = max(0.0, min(WORLD_HEIGHT - self.height, self.y))

        new_dist = math.hypot(
            self.x + self.width / 2 - player_cx,
            self.y + self.height / 2 - player_cy,
        )
        if (new_dist >= MINING_VEHICLE_MOVE_AWAY_DISTANCE
                or self.move_away_timer >= MINING_VEHICLE_MOVE_AWAY_TIMEOUT):
            self.state = self.WAITING_FOR_PICKUP
            self.pickup_timer = MINING_VEHICLE_PICKUP_WAIT

    def create_rocket(self, player_cx, player_cy):
        from app.entities.mining_rocket import MiningRocket
        player_col = int(player_cx / TILE_SIZE)
        player_row = int(player_cy / TILE_SIZE)
        offset_col = random.randint(-MINING_ROCKET_AIM_RANGE_TILES, MINING_ROCKET_AIM_RANGE_TILES)
        offset_row = random.randint(-MINING_ROCKET_AIM_RANGE_TILES, MINING_ROCKET_AIM_RANGE_TILES)
        target_col = max(0, min(MAP_COLS - 1, player_col + offset_col))
        target_row = max(0, min(MAP_ROWS - 1, player_row + offset_row))
        target_x = float(target_col * TILE_SIZE + TILE_SIZE / 2)
        target_y = float(target_row * TILE_SIZE + TILE_SIZE / 2)
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        return MiningRocket(cx, cy, target_x, target_y, target_col, target_row)

    def draw(self, surface, camera):
        if not self.on_map:
            return
        surface.blit(self.image, camera.apply(self.x, self.y))
