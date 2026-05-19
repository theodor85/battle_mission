import pygame

from app.settings import SHOOT_SOUND_PATH, SHOOT_SOUND_VOLUME

_shoot_sound = None


def play_shoot():
    global _shoot_sound
    if _shoot_sound is None:
        _shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_PATH)
        _shoot_sound.set_volume(SHOOT_SOUND_VOLUME)
    _shoot_sound.play()
