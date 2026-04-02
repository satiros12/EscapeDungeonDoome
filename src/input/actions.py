"""
Input actions - Enum defining all possible player input actions

This module defines the InputAction enum that represents all possible
actions a player can perform in the game. Using an enum rather than
raw strings provides type safety and better code completion.
"""

from enum import Enum


class InputAction(str, Enum):
    """
    Enum representing all possible player input actions.

    Each action corresponds to a specific player behavior in the game.
    Using str,Enum allows easy serialization and comparison while
    maintaining type safety.

    Movement actions:
        MOVE_FORWARD: Move player forward in facing direction
        MOVE_BACKWARD: Move player backward (opposite to facing)
        MOVE_LEFT: Strafe left (perpendicular to facing left)
        MOVE_RIGHT: Strafe right (perpendicular to facing right)

    Rotation actions:
        ROTATE_LEFT: Rotate player view counter-clockwise
        ROTATE_RIGHT: Rotate player view clockwise

    Game actions:
        ATTACK: Perform an attack action
        PAUSE: Pause/unpause the game
        CONSOLE: Toggle the console
        QUIT: Quit the game
    """

    # Movement
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"

    # Rotation
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"

    # Game actions
    ATTACK = "attack"
    PAUSE = "pause"
    CONSOLE = "console"
    QUIT = "quit"
