import random
import sys

import pygame
from pygame.locals import QUIT

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND,
    NUMBER_OF_TURRETS, NUMBER_OF_ENEMY_TANKS,
    BULLET_DAMAGE,
    MUSIC_PATH, MUSIC_VOLUME, MUSIC_FADEOUT_MS,
    GAME_OVER_DELAY, DEFAULT_LANDSCAPE,
)
from app.map import Map
from app.entities import Player, Turret, EnemyTank, Explosion, EntityList
from app.camera import Camera
from app.events import EventBus
from app.collision import check_collisions
from app.hud import HUD


class GameScene(Scene):
    def __init__(self, screen, clock, music_on=True, landscape=None):
        super().__init__(screen, clock)
        self._music_on = music_on
        self._landscape = landscape or DEFAULT_LANDSCAPE

        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME if music_on else 0)
        pygame.mixer.music.play(loops=-1)

        self.map = Map(profile=self._landscape)
        self.camera = Camera()
        self.player = Player(self.map)
        self._place_player_on_ground()
        self.turrets = self._spawn_turrets()
        self.enemy_tanks = self._spawn_enemy_tanks()
        self.player_bullets = EntityList()
        self.enemy_bullets = EntityList()
        self.explosions = EntityList()
        self.game_over = False
        self._game_over_timer = 0.0
        self._game_over_title = ""
        self.destroyed_tank_image = pygame.image.load(
            "resources/images/enemy_tank/tank_destroyed.png"
        ).convert_alpha()
        self.hud = HUD(self.player, self.turrets, self.enemy_tanks)

        self.events = EventBus()
        self.events.listen("turret_destroyed", self._on_turret_destroyed)
        self.events.listen("player_hit", self._on_player_hit)
        self.events.listen("bullet_hit_rock", self._on_bullet_hit_rock)
        self.events.listen("enemy_tank_hit", self._on_enemy_tank_hit)

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
        clear_radius = self._landscape.spawn_clear_radius
        candidates = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if self.map.tiles[r][c] != GROUND:
                    continue
                if (abs(r - center_r) <= clear_radius
                        and abs(c - center_c) <= clear_radius):
                    continue
                candidates.append((r, c))
        chosen = random.sample(candidates, min(NUMBER_OF_TURRETS, len(candidates)))
        return [Turret(c * TILE_SIZE, r * TILE_SIZE, self.map) for r, c in chosen]

    def _spawn_enemy_tanks(self):
        center_r = MAP_ROWS // 2
        center_c = MAP_COLS // 2
        clear_radius = self._landscape.spawn_clear_radius
        turret_positions = {(int(t.y // TILE_SIZE), int(t.x // TILE_SIZE))
                           for t in self.turrets}
        candidates = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if self.map.tiles[r][c] != GROUND:
                    continue
                if (abs(r - center_r) <= clear_radius
                        and abs(c - center_c) <= clear_radius):
                    continue
                if (r, c) in turret_positions:
                    continue
                candidates.append((r, c))
        chosen = random.sample(candidates,
                               min(NUMBER_OF_ENEMY_TANKS, len(candidates)))
        return [EnemyTank(c * TILE_SIZE, r * TILE_SIZE, self.map)
                for r, c in chosen]

    def _trigger_game_over(self, title):
        if self.game_over:
            return
        self.game_over = True
        self._game_over_title = title
        self._game_over_timer = 0.0
        pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        self.hud.update(dt)

        for exp in self.explosions:
            exp.update(dt)
        self.explosions.prune()

        if self.game_over:
            self._game_over_timer += dt
            if self._game_over_timer >= GAME_OVER_DELAY:
                from app.scenes.game_over_scene import GameOverScene
                self.next_scene = GameOverScene(
                    self.screen, self.clock, self._game_over_title,
                    background=self.screen.copy(),
                    music_on=self._music_on,
                    landscape=self._landscape,
                )
            return

        self.player.blockers = [t.get_rect() for t in self.enemy_tanks
                                if t.alive]
        self.player.update(dt)
        self.camera.update(self.player.x, self.player.y,
                           self.player.speed_x, self.player.speed_y, dt)

        bullet = self.player.shoot(dt)
        if bullet is not None:
            self.player_bullets.add(bullet)

        player_center = (self.player.x + self.player.width / 2,
                         self.player.y + self.player.height / 2)
        for turret in self.turrets:
            turret.target_pos = player_center
            enemy_bullet = turret.update(dt)
            if enemy_bullet is not None:
                self.enemy_bullets.add(enemy_bullet)

        # Build blocker rects for enemy tank physics
        player_rect = self.player.get_rect()
        for tank in self.enemy_tanks:
            if not tank.alive:
                continue
            blockers = [player_rect]
            for other in self.enemy_tanks:
                if other is not tank and other.alive:
                    blockers.append(other.get_rect())
            enemy_bullet = tank.update(
                dt, self.camera, player_center,
                self.player_bullets, blockers)
            if enemy_bullet is not None:
                self.enemy_bullets.add(enemy_bullet)

        for b in self.player_bullets:
            b.update(dt)
        for b in self.enemy_bullets:
            b.update(dt)

        check_collisions(
            self.player, self.player_bullets, self.enemy_bullets,
            self.turrets, self.enemy_tanks, self.events,
        )

        self.player_bullets.prune()
        self.enemy_bullets.prune()

        # Проверка победы
        if (all(not t.alive for t in self.turrets)
                and all(not t.alive for t in self.enemy_tanks)):
            self._trigger_game_over("Victory!")

    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen, self.camera)
        for turret in self.turrets:
            turret.draw(self.screen, self.camera)
        for tank in self.enemy_tanks:
            tank.draw(self.screen, self.camera)
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
            self._trigger_game_over("Game Over")

    def _on_enemy_tank_hit(self, data):
        tank = data["tank"]
        tank.hp -= BULLET_DAMAGE
        self.explosions.add(Explosion(data["x"], data["y"]))
        if tank.hp <= 0:
            tank.destroy()

    def _on_bullet_hit_rock(self, data):
        self.explosions.add(Explosion(data["x"], data["y"]))
