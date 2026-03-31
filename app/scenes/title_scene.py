import sys

import pygame
from pygame.locals import QUIT, KEYDOWN, K_RETURN

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SUBTITLE_FONT_SIZE, COLOR_INK_DARK_DARKEST,
)

TITLE_IMAGE_PATH = "resources/Battle Mission.png"


class TitleScene(Scene):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        self._subtitle_font = pygame.font.SysFont(None, SUBTITLE_FONT_SIZE)
        raw = pygame.image.load(TITLE_IMAGE_PATH).convert()
        self._bg = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                from app.scenes.game_scene import GameScene
                self.next_scene = GameScene(self.screen, self.clock)

    def update(self, _dt):
        pass

    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        subtitle = self._subtitle_font.render("Press Enter to start", True, COLOR_INK_DARK_DARKEST)
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, cy + 200)))

        pygame.display.update()
