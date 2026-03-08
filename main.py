import sys, random, time

import pygame
from pygame.locals import *


pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000

FPS = 60
FramePerSec = pygame.time.Clock()
 
# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Moving")

MASS = 15.0
MOVING_POWER = 10.0  # 5.0 - хорошо
DRAG = 0.4          # 0.3 - хорошо


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill(BLUE)
        self.rect = self.surf.get_rect()

        self.speed_x = 0
        self.speed_y = 0
        self.moving_power_x = 0
        self.moving_power_y = 0

    def move(self):
        self.handle_input()
        self.calculate_speed()
        self.rect.move_ip(int(self.speed_x), int(self.speed_y))
        self.keep_on_screen()

    def handle_input(self):
        self.moving_power_x = 0
        self.moving_power_y = 0

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.moving_power_y = -MOVING_POWER
        if pressed_keys[K_s]:
            self.moving_power_y = MOVING_POWER
        if pressed_keys[K_a]:
            self.moving_power_x = -MOVING_POWER
        if pressed_keys[K_d]:
            self.moving_power_x = MOVING_POWER

    def calculate_speed(self):
        resulting_power_x = self.moving_power_x - self.resisting_power_x()
        resulting_power_y = self.moving_power_y - self.resisting_power_y()

        self.speed_x = self.speed_x + ((resulting_power_x / MASS))
        self.speed_y = self.speed_y + ((resulting_power_y / MASS))

        print("------------------------------------------------------")
        print(f"Moving Power X: {self.moving_power_x}, Moving Power Y: {self.moving_power_y}")
        print(f"Resisting Power X: {self.resisting_power_x()}, Resisting Power Y: {self.resisting_power_y()}")
        print(f"Speed X: {self.speed_x}, Speed Y: {self.speed_y}")
    
    def resisting_power_x(self):
        if self.speed_x < 0:
            return -DRAG * self.speed_x * self.speed_x
        else:
            return DRAG * self.speed_x * self.speed_x

    def resisting_power_y(self):
        if self.speed_y < 0:
            return -DRAG * self.speed_y * self.speed_y
        else:
            return DRAG * self.speed_y * self.speed_y

    def keep_on_screen(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = 0
            if self.speed_x < 0:
                self.speed_x = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed_x = 0
            if self.speed_x > 0:
                self.speed_x = 0
        if self.rect.top <= 0:
            self.rect.top = 0
            if self.speed_y < 0:
                self.speed_y = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if self.speed_y > 0:
                self.speed_y = 0


P1 = Player()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    P1.move()

    DISPLAYSURF.fill(WHITE)
    DISPLAYSURF.blit(P1.surf, P1.rect)

    pygame.display.update()
    FramePerSec.tick(FPS)

