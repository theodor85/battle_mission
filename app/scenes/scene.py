from abc import ABC, abstractmethod


class Scene(ABC):
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.next_scene = None  # установить для перехода на другую сцену

    @abstractmethod
    def handle_events(self): ...

    @abstractmethod
    def update(self, dt): ...

    @abstractmethod
    def draw(self): ...
