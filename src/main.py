"""
WebDoom - Pygame Edition
Entry point for the game
"""

import pygame
import sys
from game import Game


def main():
    """Initialize and run the game."""
    pygame.init()

    # Create game instance
    game = Game()

    # Run game loop
    game.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
