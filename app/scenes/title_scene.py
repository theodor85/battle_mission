import sys

import pygame
from pygame.locals import QUIT, KEYDOWN, K_RETURN, K_UP, K_DOWN, K_ESCAPE

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SUBTITLE_FONT_SIZE, COLOR_INK_DARK_DARKEST, MUSIC_VOLUME,
)
from app.landscape import LANDSCAPES
from app.difficulty import DIFFICULTIES

TITLE_IMAGE_PATH = "resources/images/ui/Battle Mission.png"

_MENU_MAIN = "main"
_MENU_SETTINGS = "settings"


class TitleScene(Scene):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        self._font = pygame.font.SysFont(None, SUBTITLE_FONT_SIZE)
        raw = pygame.image.load(TITLE_IMAGE_PATH).convert()
        self._bg = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self._menu_state = _MENU_MAIN
        self._cursor = 0

        self._music_on = True
        self._landscape_idx = 0
        self._difficulty_idx = 0

    # ── Main menu ──────────────────────────────────────────────

    def _main_items(self):
        return ["Start", "Settings", "Quit Game"]

    def _settings_items(self):
        music_val = "On" if self._music_on else "Off"
        land_val = LANDSCAPES[self._landscape_idx].name
        diff_val = DIFFICULTIES[self._difficulty_idx].name
        return [
            f"Music          {music_val}",
            f"Landscape      {land_val}",
            f"Difficulty     {diff_val}",
        ]

    # ── Events ─────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key):
        if self._menu_state == _MENU_MAIN:
            self._on_key_main(key)
        else:
            self._on_key_settings(key)

    def _on_key_main(self, key):
        items = self._main_items()
        if key == K_UP:
            self._cursor = (self._cursor - 1) % len(items)
        elif key == K_DOWN:
            self._cursor = (self._cursor + 1) % len(items)
        elif key == K_RETURN:
            self._select_main(self._cursor)

    def _on_key_settings(self, key):
        items = self._settings_items()
        if key == K_UP:
            self._cursor = (self._cursor - 1) % len(items)
        elif key == K_DOWN:
            self._cursor = (self._cursor + 1) % len(items)
        elif key == K_RETURN:
            self._toggle_setting(self._cursor)
        elif key == K_ESCAPE:
            self._menu_state = _MENU_MAIN
            self._cursor = 0

    def _select_main(self, idx):
        if idx == 0:  # Start
            from app.scenes.game_scene import GameScene
            landscape = LANDSCAPES[self._landscape_idx]
            difficulty = DIFFICULTIES[self._difficulty_idx]
            self.next_scene = GameScene(
                self.screen, self.clock,
                music_on=self._music_on,
                landscape=landscape,
                difficulty=difficulty,
            )
        elif idx == 1:  # Settings
            self._menu_state = _MENU_SETTINGS
            self._cursor = 0
        elif idx == 2:  # Quit Game
            pygame.quit()
            sys.exit()

    def _toggle_setting(self, idx):
        if idx == 0:  # Music
            self._music_on = not self._music_on
            pygame.mixer.music.set_volume(MUSIC_VOLUME if self._music_on else 0)
        elif idx == 1:  # Landscape
            self._landscape_idx = (self._landscape_idx + 1) % len(LANDSCAPES)
        elif idx == 2:  # Difficulty
            self._difficulty_idx = (self._difficulty_idx + 1) % len(DIFFICULTIES)

    # ── Update / Draw ──────────────────────────────────────────

    def update(self, _dt):
        pass

    def draw(self):
        self.screen.blit(self._bg, (0, 0))

        if self._menu_state == _MENU_MAIN:
            items = self._main_items()
        else:
            items = self._settings_items()

        cx = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 + 250
        line_h = 50

        for i, text in enumerate(items):
            label = text
            if i == self._cursor:
                label = "->  " + label
            else:
                label = "    " + label
            surf = self._font.render(label, True, COLOR_INK_DARK_DARKEST)
            self.screen.blit(surf, surf.get_rect(center=(cx, start_y + i * line_h)))

        pygame.display.update()
