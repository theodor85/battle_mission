import pygame

from app.settings import (
    SHOOT_SOUND_PATH, SHOOT_SOUND_VOLUME,
    HIT_SOUND_PATH, HIT_SOUND_VOLUME,
)

_shoot_sound = None
_hit_sound = None


def play_shoot():
    global _shoot_sound
    if _shoot_sound is None:
        _shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_PATH)
        _shoot_sound.set_volume(SHOOT_SOUND_VOLUME)
    _shoot_sound.play()


def play_hit():
    global _hit_sound
    if _hit_sound is None:
        _hit_sound = pygame.mixer.Sound(HIT_SOUND_PATH)
        _hit_sound.set_volume(HIT_SOUND_VOLUME)
    _hit_sound.play()
