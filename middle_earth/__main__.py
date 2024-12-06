from .game import Game


def main() -> None:
    game: Game
    with Game() as game:
        game.run()


if __name__ == "__main__":
    main()
