import sys

import pygame
from pygame.locals import QUIT

from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND,
)
from app.map import Map
from app.entities import Player
from app.camera import Camera


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Moving")
        self.clock = pygame.time.Clock()

        self.map = Map()
        self.camera = Camera()
        self.player = Player()
        self._place_player_on_ground()

    def _place_player_on_ground(self):
        for dr in range(MAP_ROWS // 2):
            r = MAP_ROWS // 2 + dr
            c = MAP_COLS // 2
            if self.map.tiles[r][c] == GROUND:
                self.player.x = float(c * TILE_SIZE)
                self.player.y = float(r * TILE_SIZE)
                return

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        self.player.update(dt, self.map)
        self.camera.update(self.player, dt)

    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        pygame.display.update()
