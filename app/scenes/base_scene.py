import random
import sys

import pygame
from pygame.locals import QUIT

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK,
    PLAYER_MAX_HP, HQ_FADE_DURATION,
    MUSIC_PATH, MUSIC_VOLUME,
)
from app.locations import BaseLocation
from app.entities import Player
from app.camera import Camera
from app.hud import HUD
from app.landscape import LANDSCAPES


class BaseScene(Scene):
    """Дружественная база: игрок ездит по маленькой локации, заезжает в HQ для перехода
    на новую миссию."""

    def __init__(self, screen, clock, music_on=True, landscape=None, difficulty=None):
        super().__init__(screen, clock)
        self._music_on = music_on
        self._landscape = landscape
        self._difficulty = difficulty

        pygame.mixer.stop()
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME if music_on else 0)
        pygame.mixer.music.play(loops=-1)

        self.location = BaseLocation()
        self.map = self.location.map
        self.camera = Camera(world_width=self.map.world_width,
                             world_height=self.map.world_height,
                             follow=False)
        self.player = Player(self.map)
        self.player.x, self.player.y = self.location.player_spawn
        self.player.hp = PLAYER_MAX_HP
        self.hud = HUD(self.player, [], [], [])

        self._fade_alpha = 0.0
        self._fading = False
        self._fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fade_surface.fill(BLACK)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        self.hud.update(dt)

        if self._fading:
            self._fade_alpha = min(255.0,
                                   self._fade_alpha + (255.0 / HQ_FADE_DURATION) * dt)
            if self._fade_alpha >= 255.0:
                self._goto_next_mission()
            return

        self.player.blockers = [r for b in self.location.buildings
                                for r in b.get_blocker_rects()]
        self.player.update(dt)
        self.camera.update(self.player.x, self.player.y,
                           self.player.speed_x, self.player.speed_y, dt)

        if self.location.hq.player_fully_inside(self.player.get_rect()):
            self._fading = True

    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen, self.camera)
        for b in self.location.buildings:
            b.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self.hud.draw(self.screen)

        if self._fade_alpha > 0:
            self._fade_surface.set_alpha(int(self._fade_alpha))
            self.screen.blit(self._fade_surface, (0, 0))

        pygame.display.update()

    def _goto_next_mission(self):
        from app.scenes.game_scene import GameScene
        new_landscape = random.choice(LANDSCAPES)
        self.next_scene = GameScene(
            self.screen, self.clock,
            music_on=self._music_on,
            landscape=new_landscape,
            difficulty=self._difficulty,
            player_hp=PLAYER_MAX_HP,
        )
