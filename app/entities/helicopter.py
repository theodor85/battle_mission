import pygame

from app.entities.entity import Entity
from app.settings import (
    HELICOPTER_SPEED, HELICOPTER_HOVER_TIME,
    HELICOPTER_WIDTH, HELICOPTER_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)

_DIRECTION_VECTORS = {
    'up':    (0, -1),
    'down':  (0,  1),
    'left':  (-1, 0),
    'right': ( 1, 0),
}

_REVERSE = {
    'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left',
}

_FRAME_INTERVAL = 0.125  # seconds per frame (= 8 fps)
_FADE_IN_SPEED  = 8.0    # volume units/sec when entering camera view
_FADE_OUT_SPEED = 4.0    # volume units/sec when leaving  camera view

_frames_cache = {}
_sound_cache: list = []   # [Sound] — loaded once


_MAX_VOLUME = 0.25  # уровень звука


def _get_sound() -> pygame.mixer.Sound:
    if not _sound_cache:
        _sound_cache.append(
            pygame.mixer.Sound('resources/sounds/helicopter/helicopter.mp3')
        )
    return _sound_cache[0]


def _get_frames():
    if not _frames_cache:
        for d in ('up', 'down', 'left', 'right'):
            _frames_cache[d] = [
                pygame.image.load(
                    f'resources/images/helicopter/helicopter_{d}_frame1.png'
                ).convert_alpha(),
                pygame.image.load(
                    f'resources/images/helicopter/helicopter_{d}_frame2.png'
                ).convert_alpha(),
            ]
    return _frames_cache


class Helicopter(Entity):
    FLYING_IN = 'flying_in'
    HOVERING = 'hovering'
    FLYING_OUT = 'flying_out'

    def __init__(self, start_x, start_y, target_x, target_y, direction,
                 vehicle, on_hover_complete):
        self.frames = _get_frames()
        self.direction = direction
        self.frame_index = 0
        self.frame_timer = 0.0

        super().__init__(
            start_x - HELICOPTER_WIDTH / 2,
            start_y - HELICOPTER_HEIGHT / 2,
            HELICOPTER_WIDTH,
            HELICOPTER_HEIGHT,
        )
        self.target_x = target_x
        self.target_y = target_y
        self.exit_direction = _REVERSE[direction]
        self.vehicle = vehicle
        self.on_hover_complete = on_hover_complete
        self.state = self.FLYING_IN
        self.hover_timer = 0.0

        dx, dy = _DIRECTION_VECTORS[direction]
        self.vx = dx * HELICOPTER_SPEED
        self.vy = dy * HELICOPTER_SPEED

        # Sound: dedicated channel, starts silent
        self._channel = pygame.mixer.find_channel()
        self._volume = 0.0
        if self._channel is not None:
            self._channel.play(_get_sound(), loops=-1)
            self._channel.set_volume(0.0)

    def _cx(self):
        return self.x + self.width / 2

    def _cy(self):
        return self.y + self.height / 2

    def _update_volume(self, dt, camera):
        sx, sy = camera.apply(self.x, self.y)
        on_screen = (sx + self.width > 0 and sx < SCREEN_WIDTH
                     and sy + self.height > 0 and sy < SCREEN_HEIGHT)
        target = _MAX_VOLUME if on_screen else 0.0
        speed = _FADE_IN_SPEED if target > self._volume else _FADE_OUT_SPEED
        self._volume += (target - self._volume) * min(1.0, speed * dt)
        if self._channel is not None:
            self._channel.set_volume(self._volume)

    def _stop_audio(self):
        if self._channel is not None:
            self._channel.stop()
            self._channel = None

    def update(self, dt, camera=None):
        # Rotor animation — runs regardless of flight state
        self.frame_timer += dt
        if self.frame_timer >= _FRAME_INTERVAL:
            self.frame_timer -= _FRAME_INTERVAL
            self.frame_index = 1 - self.frame_index

        if camera is not None:
            self._update_volume(dt, camera)

        if self.state == self.FLYING_IN:
            self.x += self.vx * dt
            self.y += self.vy * dt
            arrived = False
            if self.direction == 'right' and self._cx() >= self.target_x:
                arrived = True
            elif self.direction == 'left' and self._cx() <= self.target_x:
                arrived = True
            elif self.direction == 'down' and self._cy() >= self.target_y:
                arrived = True
            elif self.direction == 'up' and self._cy() <= self.target_y:
                arrived = True
            if arrived:
                self.x = self.target_x - self.width / 2
                self.y = self.target_y - self.height / 2
                self.state = self.HOVERING
                self.hover_timer = 0.0

        elif self.state == self.HOVERING:
            self.hover_timer += dt
            if self.hover_timer >= HELICOPTER_HOVER_TIME:
                self.on_hover_complete()
                self.state = self.FLYING_OUT
                self.direction = self.exit_direction  # face the way it's actually going
                self.vx = -self.vx
                self.vy = -self.vy

        elif self.state == self.FLYING_OUT:
            self.x += self.vx * dt
            self.y += self.vy * dt
            exited = False
            if self.exit_direction == 'left' and self.x + self.width < -100:
                exited = True
            elif self.exit_direction == 'right' and self.x > WORLD_WIDTH + 100:
                exited = True
            elif self.exit_direction == 'up' and self.y + self.height < -100:
                exited = True
            elif self.exit_direction == 'down' and self.y > WORLD_HEIGHT + 100:
                exited = True
            if exited:
                self.alive = False
                self._stop_audio()

    def draw(self, surface, camera):
        img = self.frames[self.direction][self.frame_index]
        surface.blit(img, camera.apply(self.x, self.y))
