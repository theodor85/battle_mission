import sys

import pygame
from pygame.locals import QUIT, KEYDOWN, K_RETURN

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE,
    TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
)

_OVERLAY_ALPHA = 100  # прозрачность тёмного затемнения (0–255)


class GameOverScene(Scene):
    def __init__(self, screen, clock, title, background=None,
                 music_on=True, landscape=None):
        super().__init__(screen, clock)
        self._title = title
        self._background = background
        self._music_on = music_on
        self._landscape = landscape
        self._title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self._subtitle_font = pygame.font.SysFont(None, SUBTITLE_FONT_SIZE)
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, _OVERLAY_ALPHA))

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
        if self._background is not None:
            self.screen.blit(self._background, (0, 0))
        else:
            self.screen.fill(BLACK)

        self.screen.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        title = self._title_font.render(self._title, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(cx, cy - 40)))

        subtitle = self._subtitle_font.render("Press Enter to try again", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, cy + 40)))

        pygame.display.update()
