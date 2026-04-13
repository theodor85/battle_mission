import sys

import pygame
from pygame.locals import QUIT, KEYDOWN, K_RETURN

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SUBTITLE_FONT_SIZE, COLOR_INK_DARK_DARKEST,
)

_VICTORY_IMAGE_PATH = "resources/images/ui/Victory.png"
_GAME_OVER_IMAGE_PATH = "resources/images/ui/Game Over.png"


class GameOverScene(Scene):
    def __init__(self, screen, clock, title, background=None,
                 music_on=True, landscape=None):
        super().__init__(screen, clock)
        self._title = title
        self._background = background
        self._music_on = music_on
        self._landscape = landscape
        self._subtitle_font = pygame.font.SysFont(None, SUBTITLE_FONT_SIZE)
        self._is_victory = "Victory" in title

        image_path = _VICTORY_IMAGE_PATH if self._is_victory else _GAME_OVER_IMAGE_PATH
        raw = pygame.image.load(image_path).convert()
        self._bg = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                from app.scenes.game_scene import GameScene
                self.next_scene = GameScene(
                    self.screen, self.clock,
                    music_on=self._music_on,
                    landscape=self._landscape,
                )

    def update(self, dt):
        pass

    def draw(self):
        self.screen.blit(self._bg, (0, 0))

        cx = SCREEN_WIDTH // 2
        text = "Press Enter to start again" if self._is_victory else "Press Enter to try again"
        subtitle = self._subtitle_font.render(text, True, COLOR_INK_DARK_DARKEST)
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, SCREEN_HEIGHT // 2 + 250)))

        pygame.display.update()
