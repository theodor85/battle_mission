import random
from collections import deque

import pygame

from app.settings import (
    TILE_SIZE, MAP_COLS, MAP_ROWS, SCREEN_WIDTH, SCREEN_HEIGHT,
    GROUND, ROCK, WATER, TILE_COLORS,
    ROCK_SEED_CHANCE, ROCK_SMOOTH_ITERATIONS, ROCK_NEIGHBOR_THRESHOLD,
    RIVER_COUNT, LAKE_COUNT, LAKE_MAX_SIZE, SPAWN_CLEAR_RADIUS,
)


class Map:
    def __init__(self):
        self.tiles = [[GROUND] * MAP_COLS for _ in range(MAP_ROWS)]
        self._generate_mountains()
        self._generate_rivers()
        self._generate_lakes()
        self._clear_spawn_area()
        self._ensure_connectivity()

    def _generate_mountains(self):
        grid = [[GROUND] * MAP_COLS for _ in range(MAP_ROWS)]
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if random.random() < ROCK_SEED_CHANCE:
                    grid[r][c] = ROCK

        for _ in range(ROCK_SMOOTH_ITERATIONS):
            new_grid = [[GROUND] * MAP_COLS for _ in range(MAP_ROWS)]
            for r in range(MAP_ROWS):
                for c in range(MAP_COLS):
                    neighbors = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < MAP_ROWS and 0 <= nc < MAP_COLS:
                                if grid[nr][nc] == ROCK:
                                    neighbors += 1
                            else:
                                neighbors += 1
                    if neighbors >= ROCK_NEIGHBOR_THRESHOLD:
                        new_grid[r][c] = ROCK
                    elif grid[r][c] == ROCK and neighbors >= ROCK_NEIGHBOR_THRESHOLD - 1:
                        new_grid[r][c] = ROCK
            grid = new_grid

        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if grid[r][c] == ROCK:
                    self.tiles[r][c] = ROCK

    def _generate_rivers(self):
        for _ in range(RIVER_COUNT):
            self._carve_river()

    def _carve_river(self):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            r, c = 0, random.randint(0, MAP_COLS - 1)
            dr, dc = 1, 0
        elif edge == 'bottom':
            r, c = MAP_ROWS - 1, random.randint(0, MAP_COLS - 1)
            dr, dc = -1, 0
        elif edge == 'left':
            r, c = random.randint(0, MAP_ROWS - 1), 0
            dr, dc = 0, 1
        else:
            r, c = random.randint(0, MAP_ROWS - 1), MAP_COLS - 1
            dr, dc = 0, -1

        steps = 0
        max_steps = MAP_ROWS + MAP_COLS
        while 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS and steps < max_steps:
            if self.tiles[r][c] != ROCK:
                self.tiles[r][c] = WATER
                if dc != 0:
                    for adj in (-1, 1):
                        nr = r + adj
                        if 0 <= nr < MAP_ROWS and self.tiles[nr][c] != ROCK:
                            self.tiles[nr][c] = WATER
                elif dr != 0:
                    for adj in (-1, 1):
                        nc = c + adj
                        if 0 <= nc < MAP_COLS and self.tiles[r][nc] != ROCK:
                            self.tiles[r][nc] = WATER

            r += dr
            c += dc

            if random.random() < 0.3:
                if dr != 0:
                    c += random.choice([-1, 0, 1])
                    c = max(0, min(MAP_COLS - 1, c))
                else:
                    r += random.choice([-1, 0, 1])
                    r = max(0, min(MAP_ROWS - 1, r))

            steps += 1

    def _generate_lakes(self):
        for _ in range(LAKE_COUNT):
            self._flood_lake()

    def _flood_lake(self):
        for _ in range(50):
            r = random.randint(2, MAP_ROWS - 3)
            c = random.randint(2, MAP_COLS - 3)
            if self.tiles[r][c] == GROUND:
                break
        else:
            return

        size = random.randint(LAKE_MAX_SIZE // 2, LAKE_MAX_SIZE)
        queue = deque([(r, c)])
        visited = {(r, c)}
        filled = 0

        while queue and filled < size:
            cr, cc = queue.popleft()
            if self.tiles[cr][cc] != GROUND:
                continue
            self.tiles[cr][cc] = WATER
            filled += 1

            neighbors = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
            random.shuffle(neighbors)
            for nr, nc in neighbors:
                if (0 <= nr < MAP_ROWS and 0 <= nc < MAP_COLS
                        and (nr, nc) not in visited
                        and self.tiles[nr][nc] == GROUND):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    def _clear_spawn_area(self):
        center_r = MAP_ROWS // 2
        center_c = MAP_COLS // 2
        for r in range(center_r - SPAWN_CLEAR_RADIUS, center_r + SPAWN_CLEAR_RADIUS + 1):
            for c in range(center_c - SPAWN_CLEAR_RADIUS, center_c + SPAWN_CLEAR_RADIUS + 1):
                if 0 <= r < MAP_ROWS and 0 <= c < MAP_COLS:
                    self.tiles[r][c] = GROUND

    def _ensure_connectivity(self):
        spawn_r = MAP_ROWS // 2
        spawn_c = MAP_COLS // 2

        # Find all connected components of GROUND tiles
        visited = [[False] * MAP_COLS for _ in range(MAP_ROWS)]
        components = []

        for sr in range(MAP_ROWS):
            for sc in range(MAP_COLS):
                if visited[sr][sc] or self.tiles[sr][sc] != GROUND:
                    continue
                component = set()
                queue = deque([(sr, sc)])
                visited[sr][sc] = True
                while queue:
                    r, c = queue.popleft()
                    component.add((r, c))
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < MAP_ROWS and 0 <= nc < MAP_COLS
                                and not visited[nr][nc]
                                and self.tiles[nr][nc] == GROUND):
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                components.append(component)

        if not components:
            return

        # Find which component contains the spawn point
        main_idx = 0
        for i, comp in enumerate(components):
            if (spawn_r, spawn_c) in comp:
                main_idx = i
                break

        main_component = components[main_idx]

        # Connect each other component to the main one by carving a corridor
        for i, comp in enumerate(components):
            if i == main_idx or len(comp) < 3:
                continue
            # Find closest pair of tiles between main and this component
            best_dist = float('inf')
            best_pair = None
            # Sample for performance on large components
            sample_main = random.sample(sorted(main_component), min(100, len(main_component)))
            sample_comp = random.sample(sorted(comp), min(100, len(comp)))
            for r1, c1 in sample_main:
                for r2, c2 in sample_comp:
                    dist = abs(r1 - r2) + abs(c1 - c2)
                    if dist < best_dist:
                        best_dist = dist
                        best_pair = ((r1, c1), (r2, c2))

            if best_pair is None:
                continue

            # Carve corridor between the two points
            (r1, c1), (r2, c2) = best_pair
            r, c = r1, c1
            while r != r2 or c != c2:
                if self.tiles[r][c] != GROUND:
                    self.tiles[r][c] = GROUND
                if r != r2:
                    r += 1 if r2 > r else -1
                elif c != c2:
                    c += 1 if c2 > c else -1
            self.tiles[r][c] = GROUND

            # Add carved tiles to main component for next iterations
            main_component = main_component | comp

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
