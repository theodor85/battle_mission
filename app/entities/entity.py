import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alive = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface, camera):
        raise NotImplementedError


class EntityList:
    def __init__(self):
        self._items = []

    def add(self, entity):
        self._items.append(entity)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def prune(self):
        self._items = [e for e in self._items if e.alive]
