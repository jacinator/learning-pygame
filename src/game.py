from __future__ import annotations

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


class Debug:
    BG: ClassVar[tuple[int, int, int, int]] = (0, 0, 0, 100)
    FG: ClassVar[tuple[int, int, int, int]] = (255, 255, 255, 255)

    FONT_SIZE: ClassVar[int] = 13

    PADDING: ClassVar[tuple[int, int]] = (15, 5)
    POSITION: ClassVar[tuple[int, int]] = (10, 10)

    def __init__(self, game: Game) -> None:
        self.game: Game = game
        self.font: pygame.font.Font = pygame.font.SysFont("monospace", self.FONT_SIZE)

    def render(self) -> None:
        text: tuple[str, ...] = (
            f"Camera position: {self.game.camera_position}",
            f"Mouse position: {self.game.mouse_position}",
            f"Event mode: {self.game.mode}",
        )
        lines: tuple[pygame.Surface, ...] = tuple(
            self.font.render(t, 1, self.FG) for t in text
        )

        bg: pygame.Surface = pygame.Surface(
            (
                self.PADDING[0] * 2 + max(i.get_width() for i in lines),
                self.PADDING[1] * 2 + sum(i.get_height() for i in lines),
            ),
        )
        bg.fill(self.BG)
        bg.set_alpha(self.BG[-1])

        self.game.surface.blit(bg, self.POSITION)

        position_x: int = self.POSITION[0] + self.PADDING[0]
        position_y: int = self.POSITION[1] + self.PADDING[1]

        line: pygame.Surface
        for line in lines:
            line.set_alpha(self.FG[-1])
            self.game.surface.blit(line, (position_x, position_y))
            position_y += line.get_height()


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

        self.debug: Debug = Debug(self)
        self.chunk: Chunk = Chunk(self)

        return self

    def __exit__(self, *_) -> None:
        pygame.quit()

    def frame(self) -> None:
        self.handle_events()
        self.surface.fill(self.color)

        self.chunk.render()
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
    return (randint(0, 255), randint(0, 255), randint(0, 255))
