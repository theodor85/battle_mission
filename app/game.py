import random
import sys

import pygame
from pygame.locals import QUIT

from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND, ROCK,
    NUMBER_OF_TURRETS, SPAWN_CLEAR_RADIUS,
    MUSIC_PATH, MUSIC_VOLUME, MUSIC_FADEOUT_MS,
)
from app.map import Map
from app.entities import Player, Turret, Explosion, EntityList
from app.camera import Camera
from app.events import EventBus
from app.collision import check_collisions
from app.hud import HUD


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
        self.player = Player(self.map)
        self._place_player_on_ground()
        self.turrets = self._spawn_turrets()
        self.player_bullets = EntityList()
        self.enemy_bullets = EntityList()
        self.explosions = EntityList()
        self.game_over = False
        self.destroyed_tank_image = pygame.image.load(
            "resources/tank_destroyed.png"
        ).convert_alpha()
        self.hud = HUD(self.player, self.turrets)

        self.events = EventBus()
        self.events.listen("turret_destroyed", self._on_turret_destroyed)
        self.events.listen("player_hit", self._on_player_hit)
        self.events.listen("bullet_hit_rock", self._on_bullet_hit_rock)

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
        return [Turret(c * TILE_SIZE, r * TILE_SIZE, self.map) for r, c in chosen]

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.hud.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        # Keep updating explosions even after game over
        for exp in self.explosions:
            exp.update(dt)
        self.explosions.prune()

        if self.game_over:
            return

        self.player.update(dt)
        self.camera.update(self.player.x, self.player.y,
                           self.player.speed_x, self.player.speed_y, dt)

        # Player shooting
        bullet = self.player.shoot(dt)
        if bullet is not None:
            self.player_bullets.add(bullet)

        # Turret updates and shooting
        player_center = (self.player.x + self.player.width / 2,
                         self.player.y + self.player.height / 2)
        for turret in self.turrets:
            turret.target_pos = player_center
            enemy_bullet = turret.update(dt)
            if enemy_bullet is not None:
                self.enemy_bullets.add(enemy_bullet)

        # Update all bullets
        for b in self.player_bullets:
            b.update(dt)
        for b in self.enemy_bullets:
            b.update(dt)

        # Collisions (posts events handled by _on_* methods)
        check_collisions(
            self.player, self.player_bullets, self.enemy_bullets,
            self.turrets, self.events,
        )

        # Prune dead entities
        self.player_bullets.prune()
        self.enemy_bullets.prune()
        for exp in self.explosions:
            exp.update(dt)
        self.explosions.prune()

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
        self.hud.draw(self.screen)
        pygame.display.update()

    # ── Event handlers ──────────────────────────────────────────

    def _on_turret_destroyed(self, data):
        data["turret"].destroy()
        self.explosions.add(Explosion(data["x"], data["y"]))

    def _on_player_hit(self, data):
        self.player.hp -= data["damage"]
        self.explosions.add(Explosion(data["x"], data["y"]))
        if self.player.hp <= 0:
            self.player.hp = 0
            self.player.image = self.destroyed_tank_image
            self.game_over = True
            pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)

    def _on_bullet_hit_rock(self, data):
        self.explosions.add(Explosion(data["x"], data["y"]))
