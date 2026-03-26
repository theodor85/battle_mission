import random
import sys

import pygame
from pygame.locals import QUIT

from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, DARK_GREEN, DARK_GRAY, ORANGE, RED,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND, ROCK,
    NUMBER_OF_TURRETS, SPAWN_CLEAR_RADIUS,
    PLAYER_MAX_HP, BULLET_DAMAGE,
    MUSIC_PATH, MUSIC_VOLUME, MUSIC_FADEOUT_MS,
)
from app.map import Map
from app.entities import Player, Turret, Explosion
from app.camera import Camera


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Moving")
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1)

        self.map = Map()
        self.camera = Camera()
        self.player = Player()
        self._place_player_on_ground()
        self.turrets = self._spawn_turrets()
        self.player_bullets = []
        self.enemy_bullets = []
        self.explosions = []
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
        self.hp_display = float(PLAYER_MAX_HP)

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
            self._update_hp_display(dt)
            self.draw()

    def _update_hp_display(self, dt):
        HP_BAR_SPEED = 120.0  # единиц HP в секунду
        if self.hp_display > self.player.hp:
            self.hp_display = max(float(self.player.hp),
                                  self.hp_display - HP_BAR_SPEED * dt)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        # Keep updating explosions even after game over
        for exp in self.explosions:
            exp.update(dt)
        self.explosions = [e for e in self.explosions if e.alive]

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
                    cx = turret.x + turret._w / 2
                    cy = turret.y + turret._h / 2
                    self.explosions.append(Explosion(cx, cy))

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
                self.explosions.append(
                    Explosion(b.x + b._w / 2, b.y + b._h / 2))
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.player.image = self.destroyed_tank_image
                    self.game_over = True
                    pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)
                    break

        # Explosions for bullets that hit rocks
        for b in self.player_bullets + self.enemy_bullets:
            if not b.alive and b.hit_pos is not None:
                self.explosions.append(
                    Explosion(b.hit_pos[0] + b._w / 2,
                              b.hit_pos[1] + b._h / 2))

        # Remove dead bullets
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        # Update explosions
        for exp in self.explosions:
            exp.update(dt)
        self.explosions = [e for e in self.explosions if e.alive]

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
        for exp in self.explosions:
            exp.draw(self.screen, self.camera)
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

        # Fill (color depends on displayed HP), proportional to displayed HP
        hp_ratio = self.hp_display / PLAYER_MAX_HP
        fill_width = int(bar_width * hp_ratio)
        if self.hp_display <= 20:
            bar_color = RED
        elif self.hp_display <= 60:
            bar_color = ORANGE
        else:
            bar_color = DARK_GREEN
        radius = bar_height // 2
        if fill_width > 0:
            right_radius = radius if fill_width >= bar_width else 0
            pygame.draw.rect(self.screen, bar_color,
                             (bar_x, bar_y, fill_width, bar_height),
                             border_top_left_radius=radius,
                             border_bottom_left_radius=radius,
                             border_top_right_radius=right_radius,
                             border_bottom_right_radius=right_radius)

        # Border (dark outline, always visible)
        pygame.draw.rect(self.screen, DARK_GRAY,
                         (bar_x, bar_y, bar_width, bar_height),
                         2, border_radius=radius)

        # Turret icons in top-right corner
        alive_count = sum(1 for t in self.turrets if t.alive)
        gap = 15
        for i in range(alive_count):
            x = SCREEN_WIDTH - 25 - margin - (i + 1) * 25 - i * gap
            self.screen.blit(self.turret_hud_icon, (x, margin))
