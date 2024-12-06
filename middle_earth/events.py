from collections.abc import Generator

import pygame


class Handlers:
    def handle(self) -> Generator[bool]:
        event: pygame.event.Event
        for event in pygame.event.get_events():
            yield self.handle_event(event)

    def handle_event(self, event: pygame.event.Event) -> bool:
        match event.type:
            case pygame.KEYDOWN:
                return self.handle_keydown(event)
            case pygame.QUIT:
                return False
            case _:
                return True

    def handle_keydown(self, event: pygame.event.Event) -> bool:
        match event.key:
            case pygame.K_ESCAPE:
                return False
            case _:
                return True
