import pygame

from app.settings import EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_COUNT, EXPLOSION_FPS
from app.entities.entity import Entity


class Explosion(Entity):
    _frames = None
    _scaled_frames_cache = {}

    @classmethod
    def _load_frames(cls):
        sheet = pygame.image.load(
            "resources/images/effects/explosion_spritesheet.png"
        ).convert_alpha()
        cls._frames = []
        for i in range(EXPLOSION_FRAME_COUNT):
            frame = sheet.subsurface(
                i * EXPLOSION_FRAME_SIZE, 0,
                EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE,
            )
            cls._frames.append(frame)

    def __init__(self, cx, cy, scale=1.0):
        if Explosion._frames is None:
            Explosion._load_frames()

        if scale == 1.0:
            self._my_frames = Explosion._frames
        else:
            if scale not in Explosion._scaled_frames_cache:
                new_size = int(EXPLOSION_FRAME_SIZE * scale)
                Explosion._scaled_frames_cache[scale] = [
                    pygame.transform.scale(f, (new_size, new_size))
                    for f in Explosion._frames
                ]
            self._my_frames = Explosion._scaled_frames_cache[scale]

        size = self._my_frames[0].get_width()
        x = cx - size / 2
        y = cy - size / 2
        super().__init__(x, y, size, size)
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
                self._my_frames[self.frame_index],
                camera.apply(self.x, self.y),
            )
