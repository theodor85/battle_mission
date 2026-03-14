import random

import pygame

from app.settings import (
    TILE_SIZE, MAP_COLS, MAP_ROWS, SCREEN_WIDTH, SCREEN_HEIGHT,
    GROUND, ROCK, WATER, TILE_COLORS,
)


class Map:
    def __init__(self):
        self.tiles = [[GROUND] * MAP_COLS for _ in range(MAP_ROWS)]
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                val = random.random()
                if val < 0.10:
                    self.tiles[r][c] = ROCK
                elif val < 0.18:
                    self.tiles[r][c] = WATER

    def get_blocked_rects(self, x, y, w, h):
        col_start = max(0, int(x // TILE_SIZE))
        row_start = max(0, int(y // TILE_SIZE))
        col_end = min(MAP_COLS, int((x + w) // TILE_SIZE) + 1)
        row_end = min(MAP_ROWS, int((y + h) // TILE_SIZE) + 1)

        rects = []
        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                if self.tiles[r][c] in (ROCK, WATER):
                    rects.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return rects

    def draw(self, surface, camera):
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
                    TILE_COLORS[self.tiles[r][c]],
                    (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
                )
