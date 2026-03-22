import random
import sys

import pygame
from pygame.locals import QUIT

from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GREEN,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND, ROCK,
    NUMBER_OF_TURRETS, SPAWN_CLEAR_RADIUS,
    PLAYER_MAX_HP, BULLET_DAMAGE,
)
from app.map import Map
from app.entities import Player, Turret
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
        self.turrets = self._spawn_turrets()
        self.player_bullets = []
        self.enemy_bullets = []
        self.game_over = False
        self.destroyed_tank_image = pygame.image.load(
            "resources/tank_destroyed.png"
        ).convert_alpha()
        self.turret_hud_icon = pygame.transform.scale(
            pygame.image.load("resources/turret_enemy_down.png").convert_alpha(),
            (50, 50),
        )
        self.tank_hud_icon = pygame.transform.scale(
            pygame.image.load("resources/tank_up.png").convert_alpha(),
            (50, 50),
        )

    def _place_player_on_ground(self):
        for dr in range(MAP_ROWS // 2):
            r = MAP_ROWS // 2 + dr
            c = MAP_COLS // 2
            if self.map.tiles[r][c] == GROUND:
                self.player.x = float(c * TILE_SIZE)
                self.player.y = float(r * TILE_SIZE)
                return

    def _spawn_turrets(self):
        center_r = MAP_ROWS // 2
        center_c = MAP_COLS // 2
        candidates = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if self.map.tiles[r][c] == ROCK:
                    continue
                if (abs(r - center_r) <= SPAWN_CLEAR_RADIUS
                        and abs(c - center_c) <= SPAWN_CLEAR_RADIUS):
                    continue
                candidates.append((r, c))
        chosen = random.sample(candidates, min(NUMBER_OF_TURRETS, len(candidates)))
        return [Turret(c * TILE_SIZE, r * TILE_SIZE) for r, c in chosen]

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
        if self.game_over:
            return

        self.player.update(dt, self.map)
        self.camera.update(self.player, dt)

        # Player shooting
        bullet = self.player.shoot(dt)
        if bullet is not None:
            self.player_bullets.append(bullet)

        # Turret updates and shooting
        for turret in self.turrets:
            enemy_bullet = turret.update(dt, self.player)
            if enemy_bullet is not None:
                self.enemy_bullets.append(enemy_bullet)

        # Update all bullets
        for b in self.player_bullets:
            b.update(dt, self.map)
        for b in self.enemy_bullets:
            b.update(dt, self.map)

        # Player bullets vs turrets
        for turret in self.turrets:
            if not turret.alive:
                continue
            turret_rect = turret.get_rect()
            for b in self.player_bullets:
                if not b.alive:
                    continue
                bullet_rect = pygame.Rect(b.x, b.y, b._w, b._h)
                if turret_rect.colliderect(bullet_rect):
                    turret.alive = False
                    turret.image = turret.destroyed_image
                    b.alive = False

        # Enemy bullets vs player
        player_rect = pygame.Rect(
            self.player.x, self.player.y,
            self.player.rect.width, self.player.rect.height,
        )
        for b in self.enemy_bullets:
            if not b.alive:
                continue
            bullet_rect = pygame.Rect(b.x, b.y, b._w, b._h)
            if player_rect.colliderect(bullet_rect):
                self.player.hp -= BULLET_DAMAGE
                b.alive = False
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.player.image = self.destroyed_tank_image
                    self.game_over = True
                    break

        # Remove dead bullets
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen, self.camera)
        for turret in self.turrets:
            turret.draw(self.screen, self.camera)
        for b in self.player_bullets:
            b.draw(self.screen, self.camera)
        for b in self.enemy_bullets:
            b.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self._draw_hud()
        pygame.display.update()

    def _draw_hud(self):
        # HP bar in top-left corner
        margin = 10
        icon_size = 50
        bar_width = 250
        bar_height = 25
        bar_gap = 10

        # Tank icon
        self.screen.blit(self.tank_hud_icon, (margin, margin))

        # HP bar positioned to the right of icon, vertically centered
        bar_x = margin + icon_size + bar_gap
        bar_y = margin + (icon_size - bar_height) // 2

        # Fill (green, proportional to HP)
        hp_ratio = self.player.hp / PLAYER_MAX_HP
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            pygame.draw.rect(self.screen, GREEN,
                             (bar_x, bar_y, fill_width, bar_height))

        # Border (white outline, always visible)
        pygame.draw.rect(self.screen, WHITE,
                         (bar_x, bar_y, bar_width, bar_height), 2)

        # Turret icons in top-right corner
        alive_count = sum(1 for t in self.turrets if t.alive)
        gap = 15
        for i in range(alive_count):
            x = SCREEN_WIDTH - 25 - margin - (i + 1) * 25 - i * gap
            self.screen.blit(self.turret_hud_icon, (x, margin))
