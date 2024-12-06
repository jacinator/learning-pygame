from typing import ClassVar, Self

import pygame

from .events import Handlers


class Game(Handlers):
    FRAMERATE: ClassVar[int] =  60

    SCREEN_NAME: ClassVar[str] = "Middle Earth"
    SCREEN_SIZE: ClassVar[tuple[int, int]] =  (1280, 780)

    def __init__(self) -> None:
        self.running: bool = False

    def __enter__(self) -> Self:
        pygame.init()
        pygame.display.set_caption(self.SCREEN_NAME)

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.surface: pygame.Surface = pygame.display.set_mode(self.SCREEN_SIZE)

        return self

    def __exit__(self, *_) -> None:
        pygame.quit()

    def frame(self) -> None:
        self.running &= all(self.handle())

        self.surface.fill("purple")
        pygame.display.flip()

        self.clock.tick(self.FRAMERATE)

    def run(self) -> None:
        self.running = True
        while self.running:
            self.frame()
