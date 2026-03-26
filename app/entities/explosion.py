import pygame

from app.settings import EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_COUNT, EXPLOSION_FPS
from app.entities.entity import Entity


class Explosion(Entity):
    _frames = None

    @classmethod
    def _load_frames(cls):
        sheet = pygame.image.load(
            "resources/explosion_spritesheet.png"
        ).convert_alpha()
        cls._frames = []
        for i in range(EXPLOSION_FRAME_COUNT):
            frame = sheet.subsurface(
                i * EXPLOSION_FRAME_SIZE, 0,
                EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE,
            )
            cls._frames.append(frame)

    def __init__(self, cx, cy):
        if Explosion._frames is None:
            Explosion._load_frames()
        x = cx - EXPLOSION_FRAME_SIZE / 2
        y = cy - EXPLOSION_FRAME_SIZE / 2
        super().__init__(x, y, EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE)
        self.timer = 0.0
        self.frame_index = 0

    def update(self, dt):
        self.timer += dt
        self.frame_index = int(self.timer * EXPLOSION_FPS)
        if self.frame_index >= EXPLOSION_FRAME_COUNT:
            self.alive = False

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(
                Explosion._frames[self.frame_index],
                camera.apply(self.x, self.y),
            )
