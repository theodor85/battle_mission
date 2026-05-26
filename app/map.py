import random
from collections import deque

import pygame

from app.settings import (
    TILE_SIZE, MAP_COLS, MAP_ROWS, SCREEN_WIDTH, SCREEN_HEIGHT,
    GROUND, WATER, ROCK, BRICK, TILE_COLORS, TILES, DEFAULT_TILE,
)


class Map:
    def __init__(self, profile=None, cols=None, rows=None):
        self.profile = profile
        self.cols = cols if cols is not None else MAP_COLS
        self.rows = rows if rows is not None else MAP_ROWS
        self.world_width = self.cols * TILE_SIZE
        self.world_height = self.rows * TILE_SIZE
        self.tiles = [['GRASS'] * self.cols for _ in range(self.rows)]
        if profile is not None:
            self._generate_mountains()
            self._generate_rivers()
            self._generate_lakes()
            self._clear_spawn_area()
            self._ensure_connectivity()
            self._generate_bricks()

        def _load_tile(path):
            raw = pygame.image.load(path).convert()
            return pygame.transform.scale(raw, (TILE_SIZE, TILE_SIZE))

        self._textures: dict[str, pygame.Surface | None] = {}
        for name, info in TILES.items():
            if info['path']:
                self._textures[name] = _load_tile(info['path'])
            else:
                self._textures[name] = None

    # ── Helpers ──────────────────────────────────────────────────

    def _tile_type(self, row, col) -> int:
        return TILES[self.tiles[row][col]]['type']

    def set_tile(self, row, col, tile_name: str):
        self.tiles[row][col] = tile_name

    # ── Terrain generation ────────────────────────────────────────

    def _generate_mountains(self):
        p = self.profile
        grid = [['GRASS'] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < p.rock_seed_chance:
                    grid[r][c] = 'ROCK'

        for _ in range(p.rock_smooth_iterations):
            new_grid = [['GRASS'] * self.cols for _ in range(self.rows)]
            for r in range(self.rows):
                for c in range(self.cols):
                    neighbors = 0
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if grid[nr][nc] == 'ROCK':
                                    neighbors += 1
                            else:
                                neighbors += 1
                    if neighbors >= p.rock_neighbor_threshold:
                        new_grid[r][c] = 'ROCK'
                    elif grid[r][c] == 'ROCK' and neighbors >= p.rock_neighbor_threshold - 1:
                        new_grid[r][c] = 'ROCK'
            grid = new_grid

        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c] == 'ROCK':
                    self.tiles[r][c] = 'ROCK'

    def _generate_rivers(self):
        for _ in range(self.profile.river_count):
            self._carve_river()

    def _carve_river(self):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            r, c = 0, random.randint(0, self.cols - 1)
            dr, dc = 1, 0
        elif edge == 'bottom':
            r, c = self.rows - 1, random.randint(0, self.cols - 1)
            dr, dc = -1, 0
        elif edge == 'left':
            r, c = random.randint(0, self.rows - 1), 0
            dr, dc = 0, 1
        else:
            r, c = random.randint(0, self.rows - 1), self.cols - 1
            dr, dc = 0, -1

        steps = 0
        max_steps = self.rows + self.cols
        while 0 <= r < self.rows and 0 <= c < self.cols and steps < max_steps:
            if self.tiles[r][c] != 'ROCK':
                self.tiles[r][c] = 'WATER'
                if dc != 0:
                    for adj in (-1, 1):
                        nr = r + adj
                        if 0 <= nr < self.rows and self.tiles[nr][c] != 'ROCK':
                            self.tiles[nr][c] = 'WATER'
                elif dr != 0:
                    for adj in (-1, 1):
                        nc = c + adj
                        if 0 <= nc < self.cols and self.tiles[r][nc] != 'ROCK':
                            self.tiles[r][nc] = 'WATER'

            r += dr
            c += dc

            if random.random() < 0.3:
                if dr != 0:
                    c += random.choice([-1, 0, 1])
                    c = max(0, min(self.cols - 1, c))
                else:
                    r += random.choice([-1, 0, 1])
                    r = max(0, min(self.rows - 1, r))

            steps += 1

    def _generate_lakes(self):
        for _ in range(self.profile.lake_count):
            self._flood_lake()

    def _flood_lake(self):
        for _ in range(50):
            r = random.randint(2, self.rows - 3)
            c = random.randint(2, self.cols - 3)
            if self.tiles[r][c] == 'GRASS':
                break
        else:
            return

        size = random.randint(self.profile.lake_max_size // 2, self.profile.lake_max_size)
        queue = deque([(r, c)])
        visited = {(r, c)}
        filled = 0

        while queue and filled < size:
            cr, cc = queue.popleft()
            if self.tiles[cr][cc] != 'GRASS':
                continue
            self.tiles[cr][cc] = 'WATER'
            filled += 1

            neighbors = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
            random.shuffle(neighbors)
            for nr, nc in neighbors:
                if (0 <= nr < self.rows and 0 <= nc < self.cols
                        and (nr, nc) not in visited
                        and self.tiles[nr][nc] == 'GRASS'):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    def _clear_spawn_area(self):
        center_r = self.rows // 2
        center_c = self.cols // 2
        radius = self.profile.spawn_clear_radius
        for r in range(center_r - radius, center_r + radius + 1):
            for c in range(center_c - radius, center_c + radius + 1):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.tiles[r][c] = 'GRASS'

    def _ensure_connectivity(self):
        spawn_r = self.rows // 2
        spawn_c = self.cols // 2

        visited = [[False] * self.cols for _ in range(self.rows)]
        components = []

        for sr in range(self.rows):
            for sc in range(self.cols):
                if visited[sr][sc] or self._tile_type(sr, sc) != GROUND:
                    continue
                component = set()
                queue = deque([(sr, sc)])
                visited[sr][sc] = True
                while queue:
                    r, c = queue.popleft()
                    component.add((r, c))
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < self.rows and 0 <= nc < self.cols
                                and not visited[nr][nc]
                                and self._tile_type(nr, nc) == GROUND):
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                components.append(component)

        if not components:
            return

        main_idx = 0
        for i, comp in enumerate(components):
            if (spawn_r, spawn_c) in comp:
                main_idx = i
                break

        main_component = components[main_idx]

        for i, comp in enumerate(components):
            if i == main_idx or len(comp) < 3:
                continue
            best_dist = float('inf')
            best_pair = None
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

            (r1, c1), (r2, c2) = best_pair
            r, c = r1, c1
            while r != r2 or c != c2:
                if self._tile_type(r, c) != GROUND:
                    self.tiles[r][c] = DEFAULT_TILE[GROUND]
                if r != r2:
                    r += 1 if r2 > r else -1
                elif c != c2:
                    c += 1 if c2 > c else -1
            self.tiles[r][c] = DEFAULT_TILE[GROUND]

            main_component = main_component | comp

    def _generate_bricks(self):
        placed = 0
        attempts = 0
        target = self.profile.brick_cluster_count
        while placed < target and attempts < 500:
            attempts += 1
            r = random.randint(1, self.rows - 2)
            c = random.randint(1, self.cols - 2)
            if self.tiles[r][c] != 'GRASS':
                continue
            h = random.choice([2, 3])
            w = random.choice([2, 3])
            for dr in range(h):
                for dc in range(w):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if self.tiles[nr][nc] == 'GRASS':
                            self.tiles[nr][nc] = 'BRICK'
            placed += 1

    # ── Public API ────────────────────────────────────────────────

    def get_blocked_rects(self, x, y, w, h):
        col_start = max(0, int(x // TILE_SIZE))
        row_start = max(0, int(y // TILE_SIZE))
        col_end = min(self.cols, int((x + w) // TILE_SIZE) + 1)
        row_end = min(self.rows, int((y + h) // TILE_SIZE) + 1)

        rects = []
        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                if self._tile_type(r, c) in (WATER, ROCK, BRICK):
                    rects.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return rects

    def draw(self, surface, camera):
        start_col = max(0, int(camera.x // TILE_SIZE))
        start_row = max(0, int(camera.y // TILE_SIZE))
        end_col = min(self.cols, int((camera.x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        end_row = min(self.rows, int((camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 1)

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                tile_name = self.tiles[r][c]
                screen_x, screen_y = camera.apply(c * TILE_SIZE, r * TILE_SIZE)
                tex = self._textures.get(tile_name)
                if tex is not None:
                    surface.blit(tex, (screen_x, screen_y))
                else:
                    tile_type = TILES[tile_name]['type']
                    color = TILE_COLORS.get(tile_type, (0, 0, 0))
                    pygame.draw.rect(surface, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
