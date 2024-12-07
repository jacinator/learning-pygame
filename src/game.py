from __future__ import annotations

from collections.abc import Generator
from enum import Flag, auto
from random import randint
from typing import ClassVar, Self

import pygame


class Chunk:
    BLOCK_SIZE: ClassVar[int] = 8
    CHUNK_SIZE: ClassVar[int] = BLOCK_SIZE * 8

    def __init__(self, game: Game) -> None:
        self.game: Game = game

        self.surface: pygame.Surface = pygame.Surface(
            (self.CHUNK_SIZE, self.CHUNK_SIZE)
        )
        self.surface.fill((255, 255, 255))

    def render(self) -> None:
        self.game.surface.blit(
            self.surface,
            (
                self.game.camera_position.x
                + self.game.rect.centerx
                - self.CHUNK_SIZE / 2,
                self.game.camera_position.y
                + self.game.rect.centery
                - self.CHUNK_SIZE / 2,
            ),
        )


class TextBox:
    BG: ClassVar[tuple[int, int, int, int]] = (0, 0, 0, 100)
    FG: ClassVar[tuple[int, int, int, int]] = (255, 255, 255, 255)

    FONT_FAMILY: ClassVar[str] = "monospace"
    FONT_SIZE: ClassVar[int] = 13

    PADDING: ClassVar[tuple[int, int]] = (15, 5)

    def __init__(self, surface: pygame.Surface, position: tuple[int, int]) -> None:
        self.font: pygame.font.Font = pygame.font.SysFont(
            self.FONT_FAMILY, self.FONT_SIZE
        )
        self.position: tuple[int, int] = position
        self.surface: pygame.Surface = surface

    def __iter__(self) -> Generator[str]:
        yield from ()

    def _get_background(self, x: int, y: int) -> pygame.Surface:
        surface: pygame.Surface = pygame.Surface(
            (self.PADDING[0] * 2 + x, self.PADDING[1] * 2 + y)
        )
        surface.fill(self.BG)
        surface.set_alpha(self.BG[-1])
        return surface

    def _get_foreground(self) -> Generator[pygame.Surface]:
        text: str
        for text in self:
            surface: pygame.Surface = self.font.render(text, 1, self.FG)
            surface.set_alpha(self.FG[-1])
            yield surface

    def render(self) -> None:
        fg: tuple[pygame.Surface, ...] = tuple(self._get_foreground())
        lh: int = fg[0].get_height()

        bg: pygame.Surface = self._get_background(
            max(x.get_width() for x in fg), lh * len(fg)
        )

        x: int = self.PADDING[0] + self.position[0]
        y: int = self.PADDING[1] + self.position[1]

        blits: Generator[tuple[pygame.Surface, tuple[int, int]]] = (
            (b, (x, lh * a + y)) for a, b in enumerate(fg)
        )
        self.surface.blits(((bg, self.position), *blits))


class AlertTextBox(TextBox):
    def __iter__(self) -> Generator[str]:
        yield "Try your mouse buttons!"


class DebugTextBox(TextBox):
    def __init__(self, game: Game, position: tuple[int, int]) -> None:
        self.game: Game = game
        super().__init__(game.surface, position)

    def __iter__(self) -> Generator[str]:
        yield f"Camera position: {self.game.camera_position}"
        yield f"Mouse position: {self.game.mouse_position}"
        yield f"Event mode: {self.game.mode}"


class Mode(Flag):
    DRAG = auto()
    NONE = auto()


class Game:
    FRAMERATE: ClassVar[int] = 60
    ZERO: pygame.Vector2 = pygame.Vector2((0, 0))

    SCREEN_NAME: ClassVar[str] = "Middle Earth"
    SCREEN_SIZE: ClassVar[tuple[int, int]] = (1280, 780)

    def __init__(self) -> None:
        self.color: tuple[int, int, int] = get_color()

        self.running: bool = False
        self.mode: Mode = Mode.NONE

        self.camera_position: pygame.Vector2 = self.ZERO.copy()
        self.mouse_position: pygame.Vector2 = self.ZERO.copy()

    def __enter__(self) -> Self:
        pygame.init()
        pygame.display.set_caption(self.SCREEN_NAME)

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.rect: pygame.Rect = pygame.Rect((0, 0), self.SCREEN_SIZE)
        self.surface: pygame.Surface = pygame.display.set_mode(self.SCREEN_SIZE)

        self.surface.get_width()
        self.alert: TextBox = AlertTextBox(self.surface, (10, 80))
        self.debug: TextBox = DebugTextBox(self, (10, 10))

        self.chunk: Chunk = Chunk(self)

        return self

    def __exit__(self, *_) -> None:
        pygame.quit()

    def frame(self) -> None:
        self.handle_events()
        self.surface.fill(self.color)

        self.chunk.render()
        self.alert.render()
        self.debug.render()

        pygame.display.flip()
        self.clock.tick(self.FRAMERATE)

    def handle_events(self) -> None:
        event: pygame.event.Event
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event: pygame.event.Event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                self.handle_keydown(event)

            case pygame.QUIT:
                self.running = False

            case pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            case pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)

            case pygame.MOUSEMOTION:
                self.handle_mousemotion(event)

    def handle_keydown(self, event: pygame.event.Event) -> None:
        match (self.mode, event.key):
            case (_, pygame.K_ESCAPE):
                self.running = False

    def handle_mousebuttondown(self, event: pygame.event.Event) -> None:
        match (self.mode, event.button):
            case (Mode.NONE, pygame.BUTTON_LEFT):
                self.color = get_color()

            case (Mode.NONE, pygame.BUTTON_RIGHT):
                self.camera_position = self.ZERO.copy()

            case (Mode.NONE, pygame.BUTTON_MIDDLE):
                self.mode = Mode.DRAG

    def handle_mousebuttonup(self, event: pygame.event.Event) -> None:
        match (self.mode, event.button):
            case (Mode.DRAG, pygame.BUTTON_MIDDLE):
                self.mode = Mode.NONE

    def handle_mousemotion(self, event: pygame.event.Event) -> None:
        position: pygame.Vector2 = pygame.Vector2(event.pos)

        match (self.mode, event.buttons):
            case (Mode.DRAG, _):
                self.camera_position += position - self.mouse_position

        self.mouse_position = position

    def run(self) -> None:
        self.running = True
        while self.running:
            self.frame()


def get_color() -> tuple[int, int, int]:
    return (randint(0, 160), randint(0, 160), randint(0, 160))
