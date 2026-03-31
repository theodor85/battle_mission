import pygame

from app.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from app.scenes.title_scene import TitleScene


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle Mission")
        self.clock = pygame.time.Clock()
        self.scene = TitleScene(self.screen, self.clock)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.scene.handle_events()
            self.scene.update(dt)
            self.scene.draw()
            if self.scene.next_scene is not None:
                self.scene = self.scene.next_scene
