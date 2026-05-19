import pygame

from app.settings import (
    TILE_SIZE,
    BUILDING_WIDTH_TILES, BUILDING_HEIGHT_TILES,
    BUILDING_LABEL_FONT_SIZE, BUILDING_WALL_COLOR,
    HQ_DOOR_WIDTH_TILES,
    WHITE,
)
from app.entities.entity import Entity


class Building(Entity):
    """Здание на дружественной базе. kind: 'garage' | 'shop' | 'hq'."""

    GARAGE = 'garage'
    SHOP = 'shop'
    HQ = 'hq'

    def __init__(self, col, row, kind, color, label):
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        w = BUILDING_WIDTH_TILES * TILE_SIZE
        h = BUILDING_HEIGHT_TILES * TILE_SIZE
        super().__init__(float(x), float(y), w, h)
        self.kind = kind
        self.color = color
        self.label = label
        self._font = pygame.font.SysFont(None, BUILDING_LABEL_FONT_SIZE)
        self._label_surface = self._font.render(label, True, WHITE)

        if kind == Building.HQ:
            door_w = HQ_DOOR_WIDTH_TILES * TILE_SIZE
            door_x = x + (w - door_w) // 2
            door_y = y + h - TILE_SIZE
            self.door_rect = pygame.Rect(door_x, door_y, door_w, TILE_SIZE)
            self.interior_rect = pygame.Rect(
                x + TILE_SIZE, y + TILE_SIZE,
                w - 2 * TILE_SIZE, h - 2 * TILE_SIZE,
            )
        else:
            self.door_rect = None
            self.interior_rect = None

    def get_blocker_rects(self):
        if self.kind != Building.HQ:
            return [self.get_rect()]
        x, y, w, h = int(self.x), int(self.y), self.width, self.height
        door = self.door_rect
        return [
            pygame.Rect(x, y, w, TILE_SIZE),                           # top wall
            pygame.Rect(x, y, TILE_SIZE, h),                           # left wall
            pygame.Rect(x + w - TILE_SIZE, y, TILE_SIZE, h),           # right wall
            pygame.Rect(x + TILE_SIZE, y + h - TILE_SIZE,
                        door.x - (x + TILE_SIZE), TILE_SIZE),          # bottom-left
            pygame.Rect(door.right, y + h - TILE_SIZE,
                        (x + w - TILE_SIZE) - door.right, TILE_SIZE),  # bottom-right
        ]

    def player_fully_inside(self, player_rect):
        if self.interior_rect is None:
            return False
        return self.interior_rect.contains(player_rect)

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x, self.y)
        if self.kind == Building.HQ:
            self._draw_hq(surface, sx, sy)
        else:
            pygame.draw.rect(surface, self.color, (sx, sy, self.width, self.height))
            pygame.draw.rect(surface, BUILDING_WALL_COLOR,
                             (sx, sy, self.width, self.height), 3)
        label_rect = self._label_surface.get_rect(
            center=(sx + self.width // 2, sy + self.height // 2))
        surface.blit(self._label_surface, label_rect)

    def _draw_hq(self, surface, sx, sy):
        pygame.draw.rect(surface, self.color, (sx, sy, self.width, self.height))
        off_x = sx - self.x
        off_y = sy - self.y
        for rect in self.get_blocker_rects():
            wsx = int(rect.x + off_x)
            wsy = int(rect.y + off_y)
            pygame.draw.rect(surface, BUILDING_WALL_COLOR,
                             (wsx, wsy, rect.width, rect.height))
